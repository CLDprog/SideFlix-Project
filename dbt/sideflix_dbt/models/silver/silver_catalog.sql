select c.content_id, nullif(trim(c.title),'') as title,
    lower(trim(c.content_type)) as content_type,
    c.duration_seconds::number(38,0) as duration_seconds,
    c.imdb_tconst, i.release_year, i.genres, i.imdb_duration_seconds,
    c.source_system, c._batch_id, c._source_file, c.updated_at, c._loaded_at
from {{ source('bronze','catalog') }} c
join {{ ref('silver_imdb') }} i on i.imdb_tconst=c.imdb_tconst
where c.source_system='imdb'
