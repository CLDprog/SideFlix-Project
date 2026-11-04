with expected as (
    select content_id,count(distinct session_id) as sessions,sum(watched_seconds)/60.0 as minutes
    from {{ ref('silver_sessions') }} where to_date(started_at_utc)
      between dateadd(day,-6,to_date('{{ var("analysis_date") }}')) and to_date('{{ var("analysis_date") }}')
    group by content_id
), actual as (
    select content_id,count(*) as copies,sum(valid_sessions) as sessions,sum(minutes_watched) as minutes
    from {{ ref('gold_editorial_weekly') }} group by content_id
)
select e.*,a.* from expected e full outer join actual a using(content_id)
where e.sessions is null or a.sessions is null or a.copies<>1 or e.sessions<>a.sessions or abs(e.minutes-a.minutes)>0.00001
