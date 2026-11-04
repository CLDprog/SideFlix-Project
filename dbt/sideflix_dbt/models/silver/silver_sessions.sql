-- Memes regles de validite que la quarantaine ; device reste soumis aux tests dbt.
select
    s.session_id, s.content_id, s.viewer_id, s.started_at_utc,
    s.watched_seconds, s.device, s._source_file, s._loaded_at
from {{ ref('stg_sessions') }} s
join {{ ref('silver_catalog') }} c on c.content_id = s.content_id
where s.session_id is not null
  and s.viewer_id is not null
  and s.started_at_utc is not null
  and s.watched_seconds > 0
  and s.watched_seconds <= c.duration_seconds
qualify row_number() over (
    partition by s.session_id order by s._loaded_at, s._source_file
) = 1
