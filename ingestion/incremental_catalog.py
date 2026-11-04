"""TD 2B: PostgreSQL watermark -> temporary batch -> Snowflake MERGE.
Replays and controlled LAB tests do not replace the original reference tables.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4
import psycopg2
from check_connection import connect_snowflake

DEFAULT_TARGET = 'SIDEFLIX.BRONZE.CATALOG'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', choices=[DEFAULT_TARGET,'SIDEFLIX.LAB.CATALOG_INGEST_TEST'], default=DEFAULT_TARGET)
    parser.add_argument('--pg-table', choices=['public.catalog','lab.catalog_ingest_test'], default='public.catalog')
    args = parser.parse_args()
    os.environ.setdefault('PGHOST','127.0.0.1')
    os.environ.setdefault('PGDATABASE','sideflix')
    with connect_snowflake() as sf, sf.cursor() as cur:
        cur.execute('ALTER SESSION SET TIMEZONE=\'UTC\'')
        cur.execute(f"SELECT TO_VARCHAR(MAX(updated_at), 'YYYY-MM-DD\"T\"HH24:MI:SS.FF6TZH:TZM') FROM {args.target}")
        watermark = cur.fetchone()[0] or '1900-01-01T00:00:00+00:00'
        with psycopg2.connect() as pg, pg.cursor() as pc:
            pc.execute(f'''SELECT content_id,title,content_type,duration_seconds,
                to_char(updated_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
                imdb_tconst,source_system FROM {args.pg_table}
                WHERE updated_at > %s::timestamptz ORDER BY updated_at,content_id''',(watermark,))
            rows = pc.fetchall()
            pc.execute(f'SELECT count(*) FROM {args.pg_table}')
            source_count = pc.fetchone()[0]
        batch = 'catalog_'+hashlib.sha256(json.dumps(rows).encode()).hexdigest()[:20]
        inserted = updated = 0
        if rows:
            cur.execute('''CREATE OR REPLACE TEMPORARY TABLE CATALOG_BATCH (
                content_id VARCHAR,title VARCHAR,content_type VARCHAR,duration_seconds NUMBER,
                updated_at VARCHAR,imdb_tconst VARCHAR,source_system VARCHAR)''')
            cur.executemany('INSERT INTO CATALOG_BATCH VALUES (%s,%s,%s,%s,%s,%s,%s)',rows)
            cur.execute(f'''MERGE INTO {args.target} t USING (
                SELECT content_id,title,content_type,duration_seconds,
                TO_TIMESTAMP_TZ(updated_at) updated_at,imdb_tconst,source_system FROM CATALOG_BATCH) s
                ON t.content_id=s.content_id
                WHEN MATCHED THEN UPDATE SET title=s.title,content_type=s.content_type,
                duration_seconds=s.duration_seconds,updated_at=s.updated_at,imdb_tconst=s.imdb_tconst,
                source_system=s.source_system,_source_file='source/catalog_real.csv',
                _batch_id=%s,_loaded_at=CURRENT_TIMESTAMP()
                WHEN NOT MATCHED THEN INSERT
                (content_id,title,content_type,duration_seconds,updated_at,imdb_tconst,source_system,
                 _source_file,_batch_id,_loaded_at)
                VALUES(s.content_id,s.title,s.content_type,s.duration_seconds,s.updated_at,
                s.imdb_tconst,s.source_system,'source/catalog_real.csv',%s,CURRENT_TIMESTAMP())''',(batch,batch))
            result = cur.fetchone(); inserted,updated = int(result[0]),int(result[1])
        cur.execute(f'SELECT count(*),count(DISTINCT content_id) FROM {args.target}')
        total,unique = cur.fetchone()
        if total != source_count or total != unique: raise ValueError('Catalogue reconciliation failed')
        # Existing course journal preserved, including its original column layout.
        if args.target == DEFAULT_TARGET:
            cur.execute('INSERT INTO SIDEFLIX.BRONZE.LOAD_RUNS SELECT CURRENT_TIMESTAMP(),%s,%s,%s,%s,%s,%s',
                        (watermark,len(rows),inserted,updated,source_count,total))
        cur.execute('INSERT INTO SIDEFLIX.BRONZE.PUBLIC_SOURCE_RUNS VALUES(%s,%s,%s,CURRENT_TIMESTAMP(),%s,%s)',
                    (str(uuid4()),'catalogue_postgresql' if args.target==DEFAULT_TARGET else 'catalogue_lab',batch,len(rows),'SUCCESS'))
        print(json.dumps(dict(target=args.target,watermark=watermark,extracted=len(rows),
                              inserted=inserted,updated=updated,total=total,batch_id=batch)))

if __name__=='__main__': main()
