"""TD4.2 DockerOperator DAG, five real sources plus explicitly simulated usage."""
import json
import os
import urllib.request
import pendulum
from airflow.sdk import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

REPO=os.environ['SIDEFLIX_REPO_DIR']
WORK=os.environ['SIDEFLIX_WORK_DIR']
ENV={k:os.environ.get(k,'') for k in ['SNOWFLAKE_ACCOUNT','SNOWFLAKE_USER','PGHOST','PGPORT','PGDATABASE','PGUSER','PGPASSWORD']}
ENV.update(SNOWFLAKE_PRIVATE_KEY_FILE='/secrets/rsa_key.p8',SNOWFLAKE_DISABLE_PLATFORM_DETECTION='true',
    AWS_EC2_METADATA_DISABLED='true',DBT_SEND_ANONYMOUS_USAGE_STATS='false',
    DBT_TARGET_PATH='/tmp/dbt-target',DBT_LOG_PATH='/tmp/dbt-logs')
MOUNTS=[Mount(source=os.environ['SIDEFLIX_KEYS_DIR'],target='/secrets',type='bind',read_only=True),
    Mount(source=WORK,target='/work',type='bind'),
    Mount(source=REPO+'/source',target='/app/source',type='bind')]

def alert_on_failure(context):
    ti=context['task_instance']
    text=f"Sideflix {ti.dag_id}.{ti.task_id} FAILED, run {context['run_id']}, attempt {ti.try_number}; logs: {ti.log_url}"
    url=os.environ.get('ALERT_WEBHOOK_URL')
    if not url:
        print('ALERT NOT DELIVERED: missing ALERT_WEBHOOK_URL;',text)
        return
    req=urllib.request.Request(url,data=json.dumps({'text':text}).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=10) as response:
        print('ALERT_DELIVERED_HTTP',response.status)

# Paris 06:00 run treats the completed UTC day. Manual demo overrides date explicitly.
# The fallback must stay lazy: a manual run has no data interval (Airflow 3), so dict.get(default) would fail.
DAY=("{{ dag_run.conf['date'] if dag_run.conf and dag_run.conf.get('date') "
     "else data_interval_end.in_timezone('UTC').subtract(days=1).to_date_string() }}")
ARGS=' --date '+DAY+' --run-id {{ run_id }}'

with DAG(dag_id='sideflix_daily',schedule='0 6 * * *',
         start_date=pendulum.datetime(2026,11,1,tz='Europe/Paris'),catchup=False,max_active_runs=1,
         default_args={'retries':2,'retry_delay':pendulum.duration(seconds=20),'on_failure_callback':alert_on_failure},
         tags=['sideflix']) as dag:
    def job(task_id,image,command):
        return DockerOperator(task_id=task_id,image=image,command=command,
            environment=ENV,mounts=MOUNTS,user=os.environ['SIDEFLIX_TASK_USER'],
            mount_tmp_dir=False,auto_remove='success',
            extra_hosts={'host.docker.internal':'host-gateway'})
    ingest=job('ingest_sources','sideflix-ingest:1.0.0','python ingestion/run_pipeline_job.py ingest'+ARGS)
    check=job('check_sources','sideflix-ingest:1.0.0','python ingestion/run_pipeline_job.py check'+ARGS)
    build=job('dbt_build','sideflix-dbt:1.0.0','python ingestion/run_pipeline_job.py build'+ARGS)
    publish=job('publish_daily_usage','sideflix-ingest:1.0.0',
        'python ingestion/publish_daily_usage.py'+ARGS+' --try-number {{ ti.try_number }}')
    ingest >> check >> build >> publish
