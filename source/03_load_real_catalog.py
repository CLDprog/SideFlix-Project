"""TD 2/pack 04: load the reviewed CSV into local PostgreSQL, replay safely.

python source/03_load_real_catalog.py
Uses standard PG* environment variables, database sideflix by default.
The original catalogue is preserved once in lab.catalog_reference.
"""
import csv
import os
from pathlib import Path
import psycopg2

ROOT = Path(__file__).resolve().parent

UPSERT = """
INSERT INTO public.catalog
 (content_id,title,content_type,duration_seconds,imdb_tconst,source_system)
VALUES (%s,%s,%s,%s,%s,%s)
ON CONFLICT (content_id) DO UPDATE SET
 title=EXCLUDED.title, content_type=EXCLUDED.content_type,
 duration_seconds=EXCLUDED.duration_seconds, imdb_tconst=EXCLUDED.imdb_tconst,
 source_system=EXCLUDED.source_system
WHERE (catalog.title,catalog.content_type,catalog.duration_seconds,
       catalog.imdb_tconst,catalog.source_system)
 IS DISTINCT FROM
 (EXCLUDED.title,EXCLUDED.content_type,EXCLUDED.duration_seconds,
  EXCLUDED.imdb_tconst,EXCLUDED.source_system)
"""

def main():
    with (ROOT/'catalog_real.csv').open() as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 6 or len({r['content_id'] for r in rows}) != 6:
        raise ValueError('Expected six unique reviewed catalogue entries')
    values = [(r['content_id'], r['title'], r['content_type'],
               int(r['duration_seconds']),r['imdb_tconst'],r['source_system']) for r in rows]
    if not all(v[3]>0 and v[4].startswith('tt') for v in values):
        raise ValueError('Invalid runtime or IMDb identifier')
    os.environ.setdefault('PGHOST','127.0.0.1')
    os.environ.setdefault('PGDATABASE','sideflix')
    with psycopg2.connect() as con, con.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS public.catalog (
          content_id text PRIMARY KEY, title text NOT NULL,
          content_type text NOT NULL CHECK(content_type IN
             ('film','short_film','documentary','reportage','series_episode')),
          duration_seconds integer NOT NULL CHECK(duration_seconds>0),
          updated_at timestamptz NOT NULL DEFAULT clock_timestamp());
        CREATE SCHEMA IF NOT EXISTS lab;
        CREATE TABLE IF NOT EXISTS lab.catalog_reference AS TABLE public.catalog;
        ALTER TABLE public.catalog ADD COLUMN IF NOT EXISTS imdb_tconst text;
        ALTER TABLE public.catalog ADD COLUMN IF NOT EXISTS source_system text;
        CREATE UNIQUE INDEX IF NOT EXISTS catalog_imdb_unique ON public.catalog(imdb_tconst);
        CREATE OR REPLACE FUNCTION public.touch_catalog_updated_at()
        RETURNS trigger AS $$ BEGIN NEW.updated_at:=clock_timestamp(); RETURN NEW; END;
        $$ LANGUAGE plpgsql;
        CREATE OR REPLACE TRIGGER catalog_touch BEFORE UPDATE ON public.catalog
          FOR EACH ROW EXECUTE FUNCTION public.touch_catalog_updated_at();
        """)
        changed = 0
        for row in values:
            cur.execute(UPSERT,row)
            changed += cur.rowcount
        cur.execute('SELECT count(*),count(DISTINCT imdb_tconst) FROM public.catalog')
        total, distinct_ids = cur.fetchone()
        if total != 6 or distinct_ids != 6:
            raise ValueError(f'Unexpected catalogue state: {total}/{distinct_ids}')
        print(f'CATALOGUE_OK rows={total} distinct_imdb={distinct_ids} changed={changed}')
        cur.execute('SELECT count(*) FROM lab.catalog_reference')
        print(f'LEGACY_REFERENCE_PRESERVED rows={cur.fetchone()[0]}')

if __name__ == '__main__':
    main()
