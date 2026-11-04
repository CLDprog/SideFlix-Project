"""Stage 5.4: actual reconciliation, metadata, grains and COPY replay."""
import csv
import hashlib
import json
from pathlib import Path
from check_connection import connect_snowflake
from load_sessions import TABLES, STAGE
ROOT=Path(__file__).resolve().parent.parent
for row in csv.DictReader((ROOT/'source/sources_manifest.csv').open()):
    path=ROOT/'source'/row['file']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256'],str(path)
print('PASS: all original manifest file checksums unchanged',flush=True)
receipt=json.loads((ROOT/'rendu/ingestion_v2_initial.json').read_text())
replay=json.loads((ROOT/'rendu/ingestion_v2_replay.json').read_text())
assert all(r['loaded']==0 and r['before']==r['after']==r['expected'] for r in replay)
with connect_snowflake() as sf,sf.cursor() as cur:
    for row in receipt:
        source=row['source'];batch=row['batch_id']
        table=TABLES.get(source,'SIDEFLIX.BRONZE.SESSIONS_RAW')
        cur.execute(f'''SELECT count(*),count_if(source_system IS NULL OR _source_file IS NULL OR
            _loaded_at IS NULL OR _batch_id IS NULL),count(DISTINCT source_system)
            FROM {table} WHERE _batch_id=%s''',(batch,))
        count,missing,systems=cur.fetchone()
        assert (count,missing,systems)==(row['expected'],0,1)
        cur.execute('''SELECT count(*),sum(rows_loaded) FROM SIDEFLIX.BRONZE.PUBLIC_SOURCE_RUNS
            WHERE batch_id=%s AND source_system=%s AND status='SUCCESS' ''',(batch,source))
        runs,loaded=cur.fetchone();assert runs>=2 and loaded==count
        if row['method']=='PUT_COPY':
            cur.execute(f'''COPY INTO {table}(raw,_source_file,_loaded_at,_batch_id,source_system)
                FROM (SELECT $1,METADATA$FILENAME,CURRENT_TIMESTAMP(),'{batch}','{source}' FROM {STAGE}/{batch})
                FILE_FORMAT=(FORMAT_NAME='SIDEFLIX.BRONZE.JSON_LINES')
                PATTERN='.*[.]jsonl[.]gz' ON_ERROR=ABORT_STATEMENT''')
            result=cur.fetchall()
            assert all('0 files processed' in str(r).lower() for r in result),result
            print('COPY_REPLAY',source,str(result),flush=True)
        cur.execute(f'SELECT count(*) FROM {table} WHERE _batch_id=%s',(batch,))
        assert cur.fetchone()[0]==count
        print('PASS',source,'expected/actual',count,'metadata complete; journal matched; replay unchanged',flush=True)
    checks={
        'imdb_unique':"SELECT count(DISTINCT raw:tconst::string) FROM SIDEFLIX.BRONZE.IMDB_RAW",
        'movielens_ratings':"SELECT count(*),count(DISTINCT raw:userId::string||':'||raw:movieId::string) FROM SIDEFLIX.BRONZE.MOVIELENS_RAW WHERE raw:record_type::string='rating'",
        'netflix_grain':"SELECT count(DISTINCT concat(raw:week::string,'|',raw:category::string,'|',raw:show_title::string,'|',coalesce(raw:season_title::string,''))) FROM SIDEFLIX.BRONZE.NETFLIX_RAW",
        'wikidata_unique':"SELECT count(DISTINCT _source_file) FROM SIDEFLIX.BRONZE.WIKIDATA_RAW",
        'wikimedia_days':"SELECT count(*),count(DISTINCT concat(f.value:article::string,'|',f.value:timestamp::string)) FROM SIDEFLIX.BRONZE.WIKIMEDIA_RAW,LATERAL FLATTEN(raw:items) f",
        'simulated_sessions':"SELECT count(*),count(DISTINCT raw:session_id::string),count_if(raw:watched_seconds::number<0) FROM SIDEFLIX.BRONZE.SESSIONS_RAW WHERE source_system='sessions_simulated'",
    }
    expected=[(6,),(74,74),(3,),(6,),(42,42),(32,31,1)]
    for (name,sql),exp in zip(checks.items(),expected):
        cur.execute(sql);actual=cur.fetchone();assert actual==exp,(name,actual,exp)
        print('PASS',name,actual,flush=True)
print('ALL_BRONZE_V2_CHECKS_PASS',flush=True)
