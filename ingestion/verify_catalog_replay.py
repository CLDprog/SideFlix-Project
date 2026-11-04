"""TD2B controlled update/replay on LAB copies, preserving the real catalogue."""
import json
import os
import subprocess
import sys
from pathlib import Path
import psycopg2
from check_connection import connect_snowflake

ROOT=Path(__file__).resolve().parent.parent
os.environ.setdefault('PGHOST','127.0.0.1')
os.environ.setdefault('PGDATABASE','sideflix')

def pg_rows(cur):
    cur.execute('SELECT * FROM public.catalog ORDER BY content_id')
    return cur.fetchall()

pg=psycopg2.connect()
pg.autocommit=True
try:
    with pg.cursor() as pc, connect_snowflake() as sf, sf.cursor() as sc:
        pg_before=pg_rows(pc)
        sc.execute('SELECT * FROM SIDEFLIX.BRONZE.CATALOG ORDER BY content_id')
        sf_before=sc.fetchall()
        pc.execute('DROP TABLE IF EXISTS lab.catalog_ingest_test')
        pc.execute('CREATE TABLE lab.catalog_ingest_test (LIKE public.catalog INCLUDING ALL)')
        pc.execute('INSERT INTO lab.catalog_ingest_test SELECT * FROM public.catalog')
        pc.execute('CREATE TRIGGER catalog_test_touch BEFORE UPDATE ON lab.catalog_ingest_test FOR EACH ROW EXECUTE FUNCTION public.touch_catalog_updated_at()')
        sc.execute('CREATE OR REPLACE TABLE SIDEFLIX.LAB.CATALOG_INGEST_TEST LIKE SIDEFLIX.BRONZE.CATALOG')
        def run(label, expected):
            result=subprocess.run([sys.executable,str(ROOT/'ingestion/incremental_catalog.py'),
                '--target','SIDEFLIX.LAB.CATALOG_INGEST_TEST','--pg-table','lab.catalog_ingest_test'],
                capture_output=True,text=True)
            if result.returncode:
                print(result.stdout,result.stderr,flush=True)
                result.check_returncode()
            row=json.loads(result.stdout.strip().splitlines()[-1])
            assert (row['extracted'],row['inserted'],row['updated'])==expected,row
            print(label,json.dumps(row),flush=True)
        run('INITIAL',(6,6,0))
        run('REPLAY',(0,0,0))
        pc.execute("SELECT title FROM lab.catalog_ingest_test WHERE content_id='A'")
        original=pc.fetchone()[0]
        try:
            pc.execute("UPDATE lab.catalog_ingest_test SET title=%s WHERE content_id='A'",(original+' [LAB TEST]',))
            run('CONTROLLED_UPDATE',(1,0,1))
        finally:
            pc.execute("UPDATE lab.catalog_ingest_test SET title=%s WHERE content_id='A'",(original,))
        run('RESTORE',(1,0,1))
        run('FINAL_REPLAY',(0,0,0))
        assert pg_rows(pc)==pg_before,'Real PostgreSQL catalogue changed'
        sc.execute('SELECT * FROM SIDEFLIX.BRONZE.CATALOG ORDER BY content_id')
        assert sc.fetchall()==sf_before,'Real Snowflake catalogue changed'
        print('PASS: real PostgreSQL and Snowflake catalogues unchanged; LAB restored',flush=True)

finally:
    pg.close()
