-- Keep ratings at their grain before aggregation; never join ratings to sessions.
with links as (
    select raw:movieId::string as movie_id,
        'tt'||lpad(raw:imdbId::string,7,'0') as imdb_tconst
    from {{ source('bronze','movielens_raw') }}
    where _batch_id='{{ var("batch_movielens") }}' and raw:record_type::string='link'
    qualify row_number() over(partition by raw:movieId::string order by _loaded_at desc,_source_file desc,to_json(raw) desc)=1
), ratings as (
    select raw:movieId::string as movie_id,raw:userId::string as viewer_id,
        try_to_double(raw:rating::string) as rating,
        to_timestamp_ntz(try_to_number(raw:timestamp::string),0) as rated_at_utc,
        source_system,_batch_id,_source_file,_loaded_at
    from {{ source('bronze','movielens_raw') }}
    where _batch_id='{{ var("batch_movielens") }}' and raw:record_type::string='rating'
    qualify row_number() over(partition by raw:movieId::string,raw:userId::string
        order by try_to_number(raw:timestamp::string) desc,_loaded_at desc,_source_file desc,to_json(raw) desc)=1
)
select l.imdb_tconst,count(*) as rating_count,avg(r.rating) as avg_rating,
    min(r.rated_at_utc)::date as ratings_start,max(r.rated_at_utc)::date as ratings_end,
    max(r.source_system) as source_system,max(r._batch_id) as _batch_id,
    max(r._source_file) as _source_file,max(r._loaded_at) as _loaded_at
from ratings r join links l on l.movie_id=r.movie_id
group by l.imdb_tconst
