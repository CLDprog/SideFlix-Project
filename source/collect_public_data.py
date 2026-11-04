"""Small public-source collection, using the course's requests/JSON pattern.

Run: python source/collect_public_data.py from Sideflix.
Does not connect to PostgreSQL/Snowflake or alter the historical fixture.
"""
import csv
import gzip
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
import requests
import time

ROOT = Path(__file__).resolve().parent
REAL = ROOT / 'real'
NOW = datetime.now(timezone.utc).isoformat()
FILMS = [('A', 'Whiplash', '112552', 'tt2582802'),
         ('B', 'Moonlight', '162414', 'tt4975722'),
         ('C', 'Frances Ha', '102800', 'tt2347569'),
         ('D', 'Room', '140174', 'tt3170832'),
         ('E', 'Sicario', '139644', 'tt3397884'),
         ('F', 'Get Out', '168250', 'tt5052448')]
HEADERS = {'User-Agent': 'SideflixAcademic/1.0 (educational film metadata project)'}

def get(url, **kw):
    for attempt in range(3):
        r = requests.get(url, headers=HEADERS, timeout=30, **kw)
        if r.status_code == 429 and attempt < 2:
            delay = int(r.headers.get('Retry-After', '10'))
            if delay > 30:
                r.raise_for_status()
            time.sleep(delay)
            continue
        r.raise_for_status()
        return r

def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

def entity_for(film):
    cid, title, mid, imdb = film
    cached = []
    for path in (REAL / 'wikidata').glob('*.json'):
        e = next(iter(json.loads(path.read_text())['entities'].values()))
        ids = [x.get('mainsnak', {}).get('datavalue', {}).get('value')
               for x in e.get('claims', {}).get('P345', [])]
        if imdb in ids:
            cached.append({'id': e['id'], 'description': 'verified film'})
    search = {'search': cached} if cached else get('https://www.wikidata.org/w/api.php', params={
        'action': 'wbsearchentities', 'search': title, 'language': 'en',
        'format': 'json', 'limit': 15}).json()
    for candidate in search.get('search', []):
        if 'film' not in candidate.get('description', '').lower():
            continue
        qid = candidate['id']
        url = f'https://www.wikidata.org/wiki/Special:EntityData/{qid}.json'
        path = REAL / 'wikidata' / f'{qid}.json'
        obj = json.loads(path.read_text()) if path.exists() else get(url).json()
        ent = obj['entities'][qid]
        ids = [x.get('mainsnak', {}).get('datavalue', {}).get('value')
               for x in ent.get('claims', {}).get('P345', [])]
        if imdb not in ids:
            continue
        article = ent['sitelinks']['enwiki']['title']
        save_json(REAL / 'wikidata' / f'{qid}.json', obj)
        from urllib.parse import quote
        pvurl = ('https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/'
                 f'en.wikipedia.org/all-access/user/{quote(article, safe="")}/'
                 'daily/2026102600/2026110100')
        pvpath = REAL / 'wikimedia' / f'{qid}_20261026_20261101.json'
        pv = json.loads(pvpath.read_text()) if pvpath.exists() else get(pvurl).json()
        assert len(pv.get('items', [])) == 7, (title, 'missing pageview days')
        assert len({x['timestamp'] for x in pv['items']}) == 7
        assert all(x['views'] >= 0 for x in pv['items'])
        save_json(REAL / 'wikimedia' / f'{qid}_20261026_20261101.json', pv)
        print('API_OK', title, qid, article, flush=True)
        return dict(content_id=cid, title=title, movielens_id=mid,
                    imdb_tconst=imdb, wikidata_qid=qid, wikipedia_article=article,
                    wikidata_url=url, wikimedia_url=pvurl,
                    netflix_title_verified='Sicario' if cid == 'E' else '',
                    netflix_identity_evidence='https://www.netflix.com/be-fr/title/80046311' if cid == 'E' else '')
    raise ValueError(f'No verified Wikidata entity for {title} / {imdb}')

def main():
    ml = REAL / 'movielens' / 'ml-latest-small'
    if not (ml/'movies.csv').exists():
        import zipfile
        archive = get('https://files.grouplens.org/datasets/movielens/ml-latest-small.zip').content
        ml.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(io.BytesIO(archive)) as z:
            for name in ('movies.csv', 'ratings.csv', 'links.csv', 'tags.csv', 'README.txt'):
                (ml/name).write_bytes(z.read('ml-latest-small/'+name))
    netflix = REAL/'netflix/all-weeks-global.tsv'
    if not netflix.exists():
        raw = get('https://www.netflix.com/tudum/top10/data/all-weeks-global.tsv').content
        parsed = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')), delimiter='\t'))
        assert parsed and {'week', 'show_title', 'weekly_rank'} <= parsed[0].keys()
        netflix.parent.mkdir(parents=True, exist_ok=True)
        netflix.write_bytes(raw)
    movies = {r['movieId']: r for r in csv.DictReader((ml/'movies.csv').open())}
    links = {r['movieId']: r for r in csv.DictReader((ml/'links.csv').open())}
    ratings = list(csv.DictReader((ml/'ratings.csv').open()))
    assert len(movies) == 9742 and len(ratings) == 100836
    assert all(r['movieId'] in movies for r in ratings)
    for cid, title, mid, imdb in FILMS:
        assert 'tt' + links[mid]['imdbId'].zfill(7) == imdb
        assert any(r['movieId'] == mid for r in ratings)
    mapping = [entity_for(film) for film in FILMS]
    write_csv(ROOT / 'content_mapping.csv', mapping)
    path = REAL / 'imdb' / 'title.basics.selected.tsv'
    path.parent.mkdir(parents=True, exist_ok=True)
    wanted = {f[3] for f in FILMS}
    if path.exists():
        selected = list(csv.DictReader(path.open(), delimiter='\t'))
    else:
        print('IMDB_STREAM_START', flush=True)
        response = get('https://datasets.imdbws.com/title.basics.tsv.gz', stream=True)
        response.raw.decode_content = False
        selected = []
        with gzip.GzipFile(fileobj=response.raw) as gz:
            reader = csv.DictReader(io.TextIOWrapper(gz, encoding='utf-8'), delimiter='\t')
            for row in reader:
                if row['tconst'] in wanted:
                    selected.append(row)
                    print('IMDB_FOUND', row['tconst'], row['primaryTitle'], flush=True)
                    if len(selected) == len(wanted):
                        break
        response.close()
        assert {r['tconst'] for r in selected} == wanted
        with path.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(selected[0]), delimiter='\t')
            w.writeheader(); w.writerows(selected)
    assert {r['tconst'] for r in selected} == wanted
    imdb = {r['tconst']: r for r in selected}
    for r in mapping:
        i = imdb[r['imdb_tconst']]
        assert i['titleType'] == 'movie' and int(i['runtimeMinutes']) > 0
        r['release_year'] = i['startYear']
        r['duration_seconds'] = int(i['runtimeMinutes']) * 60
    write_csv(ROOT / 'content_mapping.csv', mapping)
    catalog = [dict(content_id=r['content_id'], title=imdb[r['imdb_tconst']]['primaryTitle'],
                    content_type='film', duration_seconds=r['duration_seconds'],
                    imdb_tconst=r['imdb_tconst'], source_system='imdb', snapshot_at=NOW)
               for r in mapping]
    write_csv(ROOT / 'catalog_real.csv', catalog)
    files = [('movielens', p, 'https://files.grouplens.org/datasets/movielens/ml-latest-small.zip')
             for p in ml.glob('*') if p.is_file()]
    files += [('netflix', REAL/'netflix/all-weeks-global.tsv',
               'https://www.netflix.com/tudum/top10/data/all-weeks-global.tsv'),
              ('imdb', path, 'https://datasets.imdbws.com/title.basics.tsv.gz')]
    for r in mapping:
        files += [('wikidata', REAL/'wikidata'/f"{r['wikidata_qid']}.json", r['wikidata_url']),
                  ('wikimedia', REAL/'wikimedia'/f"{r['wikidata_qid']}_20261026_20261101.json", r['wikimedia_url'])]
    manifest = [dict(dataset=ds, file=str(p.relative_to(ROOT)), source_url=url,
                     sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                     bytes=p.stat().st_size, verified_at_utc=NOW,
                     provenance_note='verified local copy; original download time unknown' if ds=='movielens' else 'public source snapshot')
                for ds,p,url in files]
    # Retain reviewed annotations when reusing the exact same snapshot.
    prior_path = ROOT/'sources_manifest.csv'
    if prior_path.exists():
        prior = {r['file']: r for r in csv.DictReader(prior_path.open())}
        extra = ['grain', 'period_start', 'period_end', 'terms_url',
                 'usage_attribution', 'gold_destination']
        for row in manifest:
            previous = prior.get(row['file'], {})
            for field in extra:
                row[field] = previous.get(field, '') if previous.get('sha256') == row['sha256'] else ''
    write_csv(ROOT/'sources_manifest.csv', manifest)
    print('COLLECTION_COMPLETE', len({r['dataset'] for r in manifest}), 'datasets', flush=True)

if __name__ == '__main__':
    main()
