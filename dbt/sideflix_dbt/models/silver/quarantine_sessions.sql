with checked as (
    select s.*,
        case
            when s.session_id is null then 'missing_session_id'
            when s.viewer_id is null then 'missing_viewer_id'
            when s.started_at_utc is null then 'invalid_started_at'
            when c.content_id is null then 'unknown_content'
            when s.watched_seconds is null or s.watched_seconds <= 0 then 'invalid_watched_seconds'
            when s.watched_seconds > c.duration_seconds then 'watched_seconds_exceeds_duration'
        end as reject_reason
    from {{ ref('stg_sessions') }} s
    left join {{ ref('silver_catalog') }} c on c.content_id = s.content_id
)
select * from checked
where reject_reason is not null
