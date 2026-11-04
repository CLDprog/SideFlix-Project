-- Selected authentic IMDb rows; latest version wins, deterministic ties.
select raw:tconst::string as imdb_tconst,
    nullif(trim(raw:primaryTitle::string),'') as imdb_title,
    try_to_number(raw:startYear::string) as release_year,
    try_to_number(raw:runtimeMinutes::string) * 60 as imdb_duration_seconds,
    nullif(raw:genres::string,'\\N') as genres,
    source_system, _batch_id, _source_file, _loaded_at
from {{ source('bronze','imdb_raw') }}
where _batch_id = '{{ var("batch_imdb") }}'
qualify row_number() over(partition by raw:tconst::string
    order by _loaded_at desc, _batch_id desc, _source_file desc, to_json(raw) desc)=1
