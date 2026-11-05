"""TD 2A/pack 05: PUT/COPY for files; requests -> VARIANT for APIs.
Default: simulated v2 sessions only. --public includes the five real sources.
--api-mode snapshot replays saved payloads; live makes actual API requests.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from uuid import uuid4
import sys
from check_connection import connect_snowflake

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from source.collect_public_data import get

TABLES = {name:'SIDEFLIX.BRONZE.'+name.upper()+'_RAW'
          for name in ['imdb','movielens','netflix','wikidata','wikimedia']}
STAGE = '@SIDEFLIX.BRONZE.PUBLIC_SOURCES_STAGE'


def digest(records):
    return hashlib.sha256(json.dumps(records,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:24]


def journal(cur, source, batch, loaded):
    cur.execute('INSERT INTO SIDEFLIX.BRONZE.PUBLIC_SOURCE_RUNS VALUES(%s,%s,%s,CURRENT_TIMESTAMP(),%s,%s)',
                (str(uuid4()),source,batch,loaded,'SUCCESS'))


def file_batch(cur, source, target, records):
    if not records: raise ValueError('Empty required source: '+source)
    batch=source+'_'+digest(records)
    path=ROOT/'source/real/landing'/batch/(source+'.jsonl')
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records),encoding='utf-8')
    cur.execute(f'SELECT count(*) FROM {target} WHERE _batch_id=%s',(batch,))
    before=cur.fetchone()[0]
    if before not in (0,len(records)):raise ValueError('Partial batch requires investigation: '+batch)
    loaded=0
    if before==0:
        stage=STAGE+'/'+batch
        cur.execute(f"PUT 'file://{path.as_posix()}' {stage} AUTO_COMPRESS=TRUE OVERWRITE=FALSE")
        put=cur.fetchall()
        print('PUT',source,[r[6] for r in put],flush=True)
        cur.execute(f'''COPY INTO {target}(raw,_source_file,_loaded_at,_batch_id,source_system)
            FROM (SELECT $1,METADATA$FILENAME,CURRENT_TIMESTAMP(),'{batch}','{source}' FROM {stage})
            FILE_FORMAT=(FORMAT_NAME='SIDEFLIX.BRONZE.JSON_LINES')
            PATTERN='.*[.]jsonl[.]gz' ON_ERROR=ABORT_STATEMENT''')
        columns=[x[0].lower() for x in cur.description]
        result=[dict(zip(columns,row)) for row in cur.fetchall()]
        loaded=sum(int(r.get('rows_loaded',0)) for r in result)
    cur.execute(f'SELECT count(*) FROM {target} WHERE _batch_id=%s',(batch,))
    after=cur.fetchone()[0]
    if after!=len(records):raise ValueError(f'{source}: expected {len(records)}, got {after}')
    journal(cur,source,batch,loaded)
    result=dict(source=source,method='PUT_COPY',batch_id=batch,expected=len(records),before=before,loaded=loaded,after=after)
    print(json.dumps(result),flush=True)
    return result


def api_batch(cur, source, mapping, mode, replay=None):
    records=[]
    for i,r in enumerate(mapping):
        if source=='wikidata':
            path=ROOT/'source/real/wikidata'/f"{r['wikidata_qid']}.json"
            url=r['wikidata_url']
        else:
            path=ROOT/'source/real/wikimedia'/f"{r['wikidata_qid']}_20261026_20261101.json"
            url=r['wikimedia_url']
        if replay:
            path=ROOT/'source/real/api_runs'/source/replay['batch_id']/(str(i)+'.json')
        payload=get(url).json() if mode=='live' and not replay else json.loads(path.read_text())
        if source=='wikidata':
            ent=payload['entities'][r['wikidata_qid']]
            ids=[v.get('mainsnak',{}).get('datavalue',{}).get('value') for v in ent['claims'].get('P345',[])]
            if r['imdb_tconst'] not in ids:raise ValueError('Unexpected IMDb mapping from API')
        else:
            items=payload['items']
            if len(items)!=7 or len({x['timestamp'] for x in items})!=7 or any(x['views']<0 for x in items):
                raise ValueError('Invalid/missing pageview days')
        records.append({'url':url,'payload':payload})
    batch=source+'_'+digest(records)
    if replay and batch!=replay['batch_id']:raise ValueError('Replay payload checksum mismatch')
    target=TABLES[source]
    cur.execute(f'SELECT count(*) FROM {target} WHERE _batch_id=%s',(batch,))
    before=cur.fetchone()[0]
    if before not in (0,len(records)):raise ValueError('Partial API snapshot: '+batch)
    cur.execute('BEGIN')
    try:
        for i,r in enumerate(records):
            saved=ROOT/'source/real/api_runs'/source/batch/(str(i)+'.json')
            saved.parent.mkdir(parents=True,exist_ok=True)
            saved.write_text(json.dumps(r['payload'],ensure_ascii=False,indent=2),encoding='utf-8')
            # Same INSERT SELECT PARSE_JSON as the pack; MERGE makes retry safe.
            cur.execute(f'''MERGE INTO {target} t USING
                (SELECT PARSE_JSON(%s) raw,%s file,%s batch,%s source) s
                ON t._batch_id=s.batch AND t._source_file=s.file
                WHEN NOT MATCHED THEN INSERT(raw,_source_file,_loaded_at,_batch_id,source_system)
                VALUES(s.raw,s.file,CURRENT_TIMESTAMP(),s.batch,s.source)''',
                (json.dumps(r['payload']),r['url'],batch,source))
        cur.execute(f'SELECT count(*) FROM {target} WHERE _batch_id=%s',(batch,))
        after=cur.fetchone()[0]
        if after!=len(records):raise ValueError('API reconciliation failed')
        loaded=after-before
        # Journal and API rows commit together.
        journal(cur,source,batch,loaded)
        cur.execute('COMMIT')
    except Exception:
        cur.execute('ROLLBACK');raise
    result=dict(source=source,method='API_'+mode,batch_id=batch,expected=len(records),before=before,loaded=loaded,after=after)
    print(json.dumps(result),flush=True)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--public',action='store_true')
    p.add_argument('--api-mode',choices=['snapshot','live'],default='snapshot')
    p.add_argument('--receipt',default='evidence/02_ingestion/ingestion_v2_receipt.json')
    p.add_argument('--replay-receipt',help='Replay the exact API payloads of a previous receipt, without HTTP requests')
    p.add_argument('--incident-device',metavar='RUN_ID',help='TD quality incident: isolated copy, never edits reference files')
    args=p.parse_args();mapping=list(csv.DictReader((ROOT/'source/content_mapping.csv').open()))
    results=[]
    replay={r['source']:r for r in json.loads((ROOT/args.replay_receipt).read_text())} if args.replay_receipt else {}
    with connect_snowflake() as sf,sf.cursor() as cur:
        sessions=[]
        for file in sorted((ROOT/'source/v2/sessions').glob('sessions_*.json')):
            sessions.extend(json.loads(line) for line in file.read_text().splitlines() if line.strip())
        if len(sessions)!=32:raise ValueError('Expected 32 simulated input rows')
        if args.incident_device:
            # Change one valid session in this in-memory copy, preserving expected counts.
            bad=next(r for r in sessions if r['session_id']=='S1')
            bad.update(session_id='TEST_BAD_DEVICE',device='invalid',incident_run_id=args.incident_device)
            print('INCIDENT_BAD_DEVICE: isolated batch for run',args.incident_device,flush=True)
        results.append(file_batch(cur,'sessions_simulated','SIDEFLIX.BRONZE.SESSIONS_RAW',sessions))
        if args.public:
            imdb=list(csv.DictReader((ROOT/'source/real/imdb/title.basics.selected.tsv').open(),delimiter='\t'))
            if len(imdb)!=6:raise ValueError('Expected six IMDb records')
            results.append(file_batch(cur,'imdb',TABLES['imdb'],imdb))
            selected={r['movielens_id'] for r in mapping};ml=[]
            for name,kind in [('movies','movie'),('links','link'),('ratings','rating')]:
                for r in csv.DictReader((ROOT/f'source/real/movielens/ml-latest-small/{name}.csv').open()):
                    if r['movieId'] in selected:ml.append(dict(r,record_type=kind))
            if sum(r['record_type']=='rating' for r in ml)!=74:raise ValueError('MovieLens snapshot changed; review expected counts')
            results.append(file_batch(cur,'movielens',TABLES['movielens'],ml))
            netflix=[r for r in csv.DictReader((ROOT/'source/real/netflix/all-weeks-global.tsv').open(),delimiter='\t')
                     if r.get('show_title') in {'Sicario','Get Out'} and r.get('category','').startswith('Films')]
            if not netflix:raise ValueError('Missing Netflix matching records')
            results.append(file_batch(cur,'netflix',TABLES['netflix'],netflix))
            for source in ['wikidata','wikimedia']:
                results.append(api_batch(cur,source,mapping,'snapshot' if replay else args.api_mode,replay.get(source)))
    out=ROOT/args.receipt;out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(results,indent=2)+'\n')
    print('ALL_LOADS_RECONCILED',len(results),flush=True)

if __name__=='__main__':main()
