"""Stage 7: independently recompute fixture and authentic context examples."""
import csv,json
from decimal import Decimal
from pathlib import Path
from check_connection import connect_snowflake
ROOT=Path(__file__).resolve().parent.parent
receipt={r['source']:r for r in json.loads((ROOT/'evidence/02_ingestion/ingestion_v2_initial.json').read_text())}
mapping=list(csv.DictReader((ROOT/'source/content_mapping.csv').open()))
# Recompute final 31 October/A directly from simulated input, not from Silver.
rows=[]
for path in (ROOT/'source/v2/sessions').glob('sessions_*.json'):
    rows.extend(json.loads(line) for line in path.read_text().splitlines() if line.strip())
chosen={r['session_id']:r for r in rows if r['content_id']=='A' and r['started_at'].startswith('2026-10-31') and r['watched_seconds']>0}
seconds=sum(r['watched_seconds'] for r in chosen.values())
assert len(chosen)==3 and seconds==2610
ratings=[Decimal(r['rating']) for r in csv.DictReader((ROOT/'source/real/movielens/ml-latest-small/ratings.csv').open()) if r['movieId']==mapping[0]['movielens_id']]
avg=sum(ratings)/len(ratings)
wiki=json.loads((ROOT/'source/real/api_runs/wikimedia'/receipt['wikimedia']['batch_id']/'0.json').read_text())
views=sum(x['views'] for x in wiki['items'])
netflix=[r for r in csv.DictReader((ROOT/'source/real/netflix/all-weeks-global.tsv').open(),delimiter='\t') if r['show_title']=='Sicario' and r['category'].startswith('Films')]
assert len(netflix)==1
with connect_snowflake() as sf,sf.cursor() as cur:
    cur.execute("SELECT valid_sessions,minutes_watched FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY WHERE content_id='A' AND usage_date='2026-10-31'")
    actual=cur.fetchone();assert actual==(3,Decimal('43.5'))
    print('PASS final lot A/2026-10-31: expected 3 sessions, 2610s /60 =43.5min; actual',actual,flush=True)
    cur.execute("SELECT rating_count,avg_rating,pageviews FROM SIDEFLIX.GOLD.GOLD_EDITORIAL_WEEKLY WHERE content_id='A'")
    actual=cur.fetchone();assert actual[0]==len(ratings) and abs(Decimal(str(actual[1]))-avg)<Decimal('.0000001') and actual[2]==views
    print('PASS authentic Whiplash context: ratings count',len(ratings),'sum',sum(ratings),'mean',avg,'pageviews',views,'actual',actual,flush=True)
    n=netflix[0]
    cur.execute("SELECT observed_top10_weeks,best_observed_rank,last_observed_week FROM SIDEFLIX.GOLD.GOLD_EDITORIAL_WEEKLY WHERE content_id='E'")
    actual=cur.fetchone();assert actual==(1,int(n['weekly_rank']),__import__('datetime').date.fromisoformat(n['week']))
    print('PASS authentic Sicario Netflix context: week',n['week'],'rank',n['weekly_rank'],'actual',actual,flush=True)
    # Historical prototype evidence is optional on a clean installation.
    cur.execute("""SELECT count(*) FROM SIDEFLIX.INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA='LAB' AND TABLE_NAME='GOLD_CONTENT_DAILY_REFERENCE'""")
    if cur.fetchone()[0]:
        cur.execute('SELECT count(*),count(DISTINCT raw:session_id::string),count_if(raw:watched_seconds::number<=0) FROM SIDEFLIX.LAB.SESSIONS_REFERENCE')
        assert cur.fetchone()==(32,31,1)
        cur.execute("SELECT content_id,valid_sessions,minutes_watched FROM SIDEFLIX.LAB.GOLD_CONTENT_DAILY_REFERENCE WHERE usage_date='2026-10-30' ORDER BY content_id")
        actual=cur.fetchall();assert actual==[('A',2,Decimal(45)),('B',1,Decimal(10))]
        print('PASS isolated historical LAB reference: A45+B10=55min',actual,flush=True)
    else:
        print('Historical prototype reference absent; final-data checks above remain required',flush=True)
print('ALL_INDEPENDENT_BUSINESS_SAMPLES_PASS',flush=True)
