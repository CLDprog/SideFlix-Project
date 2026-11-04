-- TRY_ conversions and retained load metadata, following TD 3.3.
select
    nullif(trim(raw:session_id::string), '') as session_id,
    nullif(trim(raw:content_id::string), '') as content_id,
    nullif(trim(raw:viewer_id::string), '') as viewer_id,
    convert_timezone('UTC', try_to_timestamp_tz(raw:started_at::string))::timestamp_ntz as started_at_utc,
    try_to_number(raw:watched_seconds::string) as watched_seconds,
    lower(trim(raw:device::string)) as device,
    raw,
    source_system,
    _batch_id,
    _source_file,
    _loaded_at
from {{ source('bronze', 'sessions_raw') }}
where source_system = 'sessions_simulated'
  and _batch_id = '{{ var("batch_sessions_simulated") }}'
