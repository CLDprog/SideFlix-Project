"""TD4.2 publish_daily_sales adaptation: validated Gold -> date-keyed MERGE."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
from check_connection import connect_snowflake


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--date',required=True,type=date.fromisoformat)
    p.add_argument('--run-id',required=True)
    p.add_argument('--work-dir',default='/work')
    p.add_argument('--try-number',type=int,default=1)
    p.add_argument('--crash-on-try',type=int,default=0)
    args=p.parse_args()
    path=Path(args.work_dir)/hashlib.sha256(args.run_id.encode()).hexdigest()[:24]/'validated.json'
    valid=json.loads(path.read_text())
    assert (valid['date'],valid['run_id'],valid['status'])==(str(args.date),args.run_id,'validated')
    with connect_snowflake() as sf,sf.cursor() as cur:
        cur.execute('''SELECT count(*),sum(valid_sessions),sum(minutes_watched)
            FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY WHERE usage_date=%s''',(str(args.date),))
        rows,sessions,minutes=cur.fetchone()
        if not rows:raise ValueError('Missing validated Gold day; refusing zero publication')
        cur.execute('''CREATE TABLE IF NOT EXISTS SIDEFLIX.LAB.DAILY_USAGE(
            usage_date DATE,valid_sessions NUMBER,minutes_watched NUMBER(18,6),
            published_at TIMESTAMP_TZ,run_id VARCHAR,validation_id VARCHAR,attempt NUMBER)''')
        cur.execute('''MERGE INTO SIDEFLIX.LAB.DAILY_USAGE t USING
            (SELECT to_date(%s) usage_date,%s sessions,%s minutes) s ON t.usage_date=s.usage_date
            WHEN MATCHED THEN UPDATE SET valid_sessions=s.sessions,minutes_watched=s.minutes,
                published_at=CURRENT_TIMESTAMP(),run_id=%s,validation_id=%s,attempt=%s
            WHEN NOT MATCHED THEN INSERT VALUES(s.usage_date,s.sessions,s.minutes,
                CURRENT_TIMESTAMP(),%s,%s,%s)''',
            (str(args.date),sessions,minutes,args.run_id,valid['invocation_id'],args.try_number,
             args.run_id,valid['invocation_id'],args.try_number))
        print('MERGE_PUBLISHED',str(args.date),sessions,str(minutes),'run_id',args.run_id,'attempt',args.try_number,flush=True)
        if args.try_number==args.crash_on_try:raise SystemExit('Simulated crash AFTER write (TD4.2)')
        cur.execute('SELECT count(*) FROM SIDEFLIX.LAB.DAILY_USAGE WHERE usage_date=%s',(str(args.date),))
        assert cur.fetchone()[0]==1,'Publication duplicate'
        print('PUBLICATION_UNIQUE_DATE_PASS',flush=True)

if __name__=='__main__':main()
