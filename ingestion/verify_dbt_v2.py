"""Compare cloud outputs with the independently calculated source fixture."""
import csv
from decimal import Decimal
from pathlib import Path
from check_connection import connect_snowflake
ROOT=Path(__file__).resolve().parent.parent
with connect_snowflake() as sf,sf.cursor() as cur:
    expected_counts={'SILVER.SILVER_IMDB':6,'SILVER.SILVER_CATALOG':6,'SILVER.STG_SESSIONS':32,
        'SILVER.QUARANTINE_SESSIONS':1,'SILVER.SILVER_SESSIONS':30,'SILVER.SILVER_MOVIELENS':6,
        'SILVER.SILVER_NETFLIX':3,'SILVER.SILVER_WIKIDATA':6,'SILVER.SILVER_WIKIMEDIA':42,
        'GOLD.GOLD_CONTENT_DAILY':14,'GOLD.GOLD_EDITORIAL_WEEKLY':6}
    for table,expected in expected_counts.items():
        cur.execute('SELECT count(*) FROM SIDEFLIX.'+table);actual=cur.fetchone()[0]
        assert actual==expected,(table,actual,expected)
        print('PASS',table,actual,flush=True)
    cur.execute('SELECT usage_date,content_id,valid_sessions,minutes_watched FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY ORDER BY 1,2')
    daily=cur.fetchall();expected=list(csv.DictReader((ROOT/'source/v2/expected_daily_usage.csv').open()))
    for actual,exp in zip(daily,expected):
        assert str(actual[0])==exp['usage_date'] and actual[1]==exp['content_id']
        assert actual[2]==int(exp['valid_sessions']) and abs(actual[3]-Decimal(exp['minutes_watched']))<Decimal('.00001')
    print('PASS all 14 daily business outputs match independent expected CSV',flush=True)
    cur.execute('SELECT session_id,reject_reason,raw:watched_seconds::number FROM SIDEFLIX.SILVER.QUARANTINE_SESSIONS')
    assert cur.fetchall()==[('S31','invalid_watched_seconds',-60)]
    cur.execute("SELECT count(*) FROM SIDEFLIX.SILVER.SILVER_SESSIONS WHERE session_id='S4'");assert cur.fetchone()[0]==1
    cur.execute('''SELECT count(*),count(DISTINCT content_id),sum(valid_sessions),sum(minutes_watched),
        count_if(rating_count>0 AND avg_rating IS NOT NULL),count_if(wikidata_qid IS NOT NULL),
        count_if(pageviews IS NOT NULL),count_if(netflix_status='confirmed_match'),
        count_if(sideflix_sessions_simulated) FROM SIDEFLIX.GOLD.GOLD_EDITORIAL_WEEKLY''')
    row=cur.fetchone();assert row[:3]==(6,6,30) and row[4:]==(6,6,6,1,6),row
    assert abs(row[3]-sum(x[3] for x in daily))<Decimal('.00001'),row
    print('PASS weekly grain, unchanged 30 sessions/minutes, five sources useful; Netflix confirmed only for E',flush=True)
    cur.execute('SELECT * FROM SIDEFLIX.GOLD.GOLD_EDITORIAL_WEEKLY ORDER BY editorial_rank')
    cols=[x[0] for x in cur.description];rows=cur.fetchall()
    with (ROOT/'rendu/gold_editorial_v2.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(cols);writer.writerows(rows)
    print('PASS winner:',rows[0][cols.index('TITLE')],rows[0][cols.index('MINUTES_WATCHED')],flush=True)
    cur.execute('''SELECT count(*),count_if(imdb_duration_seconds=duration_seconds)
        FROM SIDEFLIX.SILVER.SILVER_CATALOG''');assert cur.fetchone()==(6,6)
print('ALL_DBT_V2_BUSINESS_CHECKS_PASS',flush=True)
