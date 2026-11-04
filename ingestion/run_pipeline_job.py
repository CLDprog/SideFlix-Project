"""Small TD4.2 job entry point: explicit day/run_id and shared run receipts."""
import argparse
from datetime import date
import json
import os
from pathlib import Path
import subprocess
import sys
from check_connection import connect_snowflake

ROOT=Path(__file__).resolve().parent.parent

def main():
    p=argparse.ArgumentParser()
    p.add_argument('job',choices=['ingest','check','build'])
    p.add_argument('--date',required=True,type=date.fromisoformat)
    p.add_argument('--run-id',required=True)
    p.add_argument('--work-dir',default='/work')
    p.add_argument('--incident-device',action='store_true')
    args=p.parse_args()
    # Stable safe filename; preserve the actual run ID in the validation record.
    import hashlib
    folder=Path(args.work_dir)/hashlib.sha256(args.run_id.encode()).hexdigest()[:24]
    folder.mkdir(parents=True,exist_ok=True)
    receipt=folder/'ingestion.json';valid=folder/'validated.json'
    def run(cmd):
        print(json.dumps({'job':args.job,'date':str(args.date),'run_id':args.run_id,'command':cmd}),flush=True)
        subprocess.run(cmd,cwd=ROOT,check=True)
    if args.job=='ingest':
        if valid.exists():valid.unlink()
        run([sys.executable,'source/collect_public_data.py'])
        run([sys.executable,'ingestion/incremental_catalog.py'])
        load=[sys.executable,'ingestion/load_sessions.py','--public','--api-mode','live','--receipt',str(receipt)]
        if args.incident_device:load+=['--incident-device',args.run_id]
        run(load)
        return
    results=json.loads(receipt.read_text())
    vars={'analysis_date':str(args.date),**{'batch_'+r['source']:r['batch_id'] for r in results}}
    if args.job=='check':
        tables={r['source']:'SIDEFLIX.BRONZE.'+(r['source'].upper()+'_RAW' if r['source']!='sessions_simulated' else 'SESSIONS_RAW') for r in results}
        with connect_snowflake() as sf,sf.cursor() as cur:
            assert len(results)==6,'Missing source receipt'
            for r in results:
                cur.execute(f'''SELECT count(*),count_if(_source_file IS NULL OR _loaded_at IS NULL OR source_system IS NULL)
                    FROM {tables[r['source']]} WHERE _batch_id=%s''',(r['batch_id'],))
                assert cur.fetchone()==(r['expected'],0),'Incomplete source '+r['source']
            cur.execute('''SELECT count(*) FROM SIDEFLIX.BRONZE.SESSIONS_RAW
                WHERE _batch_id=%s AND try_to_date(substr(raw:started_at::string,1,10))=%s''',
                (vars['batch_sessions_simulated'],str(args.date)))
            assert cur.fetchone()[0]>0,'No simulated sessions for requested UTC day; use an available demonstration date'
        print('SOURCE_CHECKS_PASS',str(args.date),args.run_id,flush=True)
        return
    if valid.exists():valid.unlink()
    common=['--project-dir','dbt/sideflix_dbt','--profiles-dir','dbt/profiles-core','--vars',json.dumps(vars)]
    dbt=str(Path(sys.executable).with_name('dbt'))
    run([dbt,'source','freshness',*common])
    run([dbt,'build',*common])
    target=Path(os.environ.get('DBT_TARGET_PATH',str(ROOT/'dbt/sideflix_dbt/target')))
    output=json.loads((target/'run_results.json').read_text())
    assert all(r['status'] in ['pass','success'] for r in output['results'])
    valid.write_text(json.dumps({'date':str(args.date),'run_id':args.run_id,
        'invocation_id':output['metadata']['invocation_id'],'status':'validated','vars':vars},indent=2))
    print('BUILD_VALIDATED',str(valid),flush=True)

if __name__=='__main__':main()
