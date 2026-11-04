-- Jour de debut de session en UTC ; une ligne par jour et contenu.
select
    to_date(started_at_utc) as usage_date,
    content_id,
    count(distinct session_id) as valid_sessions,
    sum(watched_seconds) / 60.0 as minutes_watched
from {{ ref('silver_sessions') }}
group by 1, 2
