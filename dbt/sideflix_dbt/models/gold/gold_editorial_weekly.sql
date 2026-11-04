-- Each input is aggregated to one row per content/article BEFORE the joins.
with usage as (
    select content_id,count(distinct session_id) as valid_sessions,sum(watched_seconds)/60.0 as minutes_watched
    from {{ ref('silver_sessions') }}
    where to_date(started_at_utc) between dateadd(day,-6,to_date('{{ var("analysis_date") }}')) and to_date('{{ var("analysis_date") }}')
    group by content_id
), netflix as (
    select content_id,count(*) as observed_top10_weeks,min(weekly_rank) as best_observed_rank,
        min(ranking_week) as first_observed_week,max(ranking_week) as last_observed_week
    from {{ ref('silver_netflix') }} where content_id is not null group by content_id
), pageviews as (
    select wikipedia_article,sum(pageviews) as pageviews,min(view_date) as views_start,max(view_date) as views_end
    from {{ ref('silver_wikimedia') }} group by wikipedia_article
)
select to_date('{{ var("analysis_date") }}') as analysis_date,c.content_id,c.title,c.imdb_tconst,
    c.release_year,c.genres,c.duration_seconds,u.valid_sessions,u.minutes_watched,
    row_number() over(order by u.minutes_watched desc,u.valid_sessions desc,c.content_id) as editorial_rank,
    m.rating_count,m.avg_rating,m.ratings_start,m.ratings_end,
    n.observed_top10_weeks,n.best_observed_rank,n.first_observed_week,n.last_observed_week,
    iff(n.content_id is null,'not_observed_or_unmatched','confirmed_match') as netflix_status,
    w.wikidata_qid,w.wikidata_label,w.description_en,w.wikipedia_article,
    p.pageviews,p.views_start,p.views_end,
    true as sideflix_sessions_simulated,
    'IMDb; MovieLens; Netflix Top 10; Wikidata; Wikimedia' as external_sources,
    current_timestamp() as published_at_utc
from usage u join {{ ref('silver_catalog') }} c on c.content_id=u.content_id
left join {{ ref('silver_movielens') }} m on m.imdb_tconst=c.imdb_tconst
left join netflix n on n.content_id=c.content_id
left join {{ ref('silver_wikidata') }} w on w.content_id=c.content_id
left join pageviews p on p.wikipedia_article=w.wikipedia_article
