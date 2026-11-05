-- Fixed demonstration snapshots, not an assertion that every real-world day has six films.
-- Every model it reads is upstream of GOLD_EDITORIAL_WEEKLY, so a failure skips that table and fails the build: nothing is published.
with counts as (
    select 'sessions' as source,count(*) as actual,30 as expected from {{ ref('silver_sessions') }}
    union all select 'imdb',count(*),6 from {{ ref('silver_imdb') }}
    union all select 'catalog',count(*),6 from {{ ref('silver_catalog') }}
    union all select 'movielens_works',count(*),6 from {{ ref('silver_movielens') }}
    union all select 'movielens_ratings',coalesce(sum(rating_count),0),74 from {{ ref('silver_movielens') }}
    union all select 'netflix_rows',count(*),3 from {{ ref('silver_netflix') }}
    union all select 'netflix_confirmed',count(*),1 from {{ ref('silver_netflix') }} where mapping_status='confirmed'
    union all select 'wikidata',count(*),6 from {{ ref('silver_wikidata') }}
    union all select 'wikimedia_days',count(*),42 from {{ ref('silver_wikimedia') }}
)
select * from counts where actual<>expected
