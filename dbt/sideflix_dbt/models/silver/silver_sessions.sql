-- Same validity rules as quarantine; device values are checked by dbt tests.
select
    s.session_id, s.content_id, s.viewer_id, s.started_at_utc,
    s.watched_seconds, s.device, s.source_system, s._batch_id, s._source_file, s._loaded_at
from {{ ref('stg_sessions') }} s
join {{ ref('silver_catalog') }} c on c.content_id = s.content_id
where s.session_id is not null
  and s.viewer_id is not null
  and s.started_at_utc is not null
  and s.watched_seconds > 0
  and s.watched_seconds <= c.duration_seconds
qualify row_number() over (
    partition by s.session_id order by s._loaded_at desc, s._batch_id desc, s._source_file desc,
        s.started_at_utc desc, s.watched_seconds desc, s.device desc, s.content_id desc, s.viewer_id desc
) = 1
