select s.* from {{ ref('silver_sessions') }} s
join {{ ref('silver_catalog') }} c on c.content_id=s.content_id
where s.watched_seconds is null or s.watched_seconds<=0 or s.watched_seconds>c.duration_seconds
