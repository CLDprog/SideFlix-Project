with failures as (
    select 'wikimedia_duplicate' as problem from {{ ref('silver_wikimedia') }} group by wikipedia_article,view_date having count(*)<>1
    union all select 'netflix_duplicate' from {{ ref('silver_netflix') }} group by ranking_week,category,show_title,season_title having count(*)<>1
    union all select 'bad_rating' from {{ ref('silver_movielens') }} where avg_rating is null or avg_rating<0.5 or avg_rating>5 or rating_count<=0
    union all select 'bad_pageviews_or_period' from {{ ref('silver_wikimedia') }} where pageviews is null or pageviews<0 or view_date is null or view_date not between '2026-10-26'::date and '2026-11-01'::date
    union all select 'missing_article_day' from {{ ref('silver_wikimedia') }} group by wikipedia_article having count(distinct view_date)<>7
    union all select 'bad_rank' from {{ ref('silver_netflix') }} where weekly_rank is null or weekly_rank not between 1 and 10 or ranking_week is null
    union all select 'imdb_duration_mismatch' from {{ ref('silver_catalog') }} where imdb_duration_seconds is null or imdb_duration_seconds<>duration_seconds
)
select * from failures
