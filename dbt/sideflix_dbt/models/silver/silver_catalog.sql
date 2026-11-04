select
    content_id,
    nullif(trim(title), '') as title,
    lower(trim(content_type)) as content_type,
    duration_seconds::number(38,0) as duration_seconds,
    updated_at,
    _loaded_at
from {{ source('bronze', 'catalog') }}
