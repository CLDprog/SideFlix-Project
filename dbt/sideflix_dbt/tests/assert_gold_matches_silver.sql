with expected as (
    select to_date(started_at_utc) as usage_date,content_id,
        count(distinct session_id) as sessions,sum(watched_seconds)/60.0 as minutes
    from {{ ref('silver_sessions') }} group by 1,2
)
select e.*,g.* from expected e full outer join {{ ref('gold_content_daily') }} g using(usage_date,content_id)
where e.sessions is null or g.valid_sessions is null or e.sessions<>g.valid_sessions
    or abs(e.minutes-g.minutes_watched)>0.00001
