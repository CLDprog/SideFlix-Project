-- Only Sicario is identity-confirmed in source/content_mapping.csv (Netflix title 80046311).
-- Get Out remains in Silver as unmatched; absence/ambiguity is never a zero.
select try_to_date(raw:week::string) as ranking_week,
    raw:category::string as category,raw:show_title::string as show_title,
    raw:season_title::string as season_title,
    try_to_number(raw:weekly_rank::string) as weekly_rank,
    try_to_number(raw:weekly_hours_viewed::string) as weekly_hours_viewed,
    case when raw:show_title::string='Sicario' then 'E' end as content_id,
    iff(raw:show_title::string='Sicario','confirmed','unmatched') as mapping_status,
    source_system,_batch_id,_source_file,_loaded_at
from {{ source('bronze','netflix_raw') }}
where _batch_id='{{ var("batch_netflix") }}'
qualify row_number() over(partition by raw:week::string,raw:category::string,
    raw:show_title::string,raw:season_title::string
    order by _loaded_at desc,_source_file desc,to_json(raw) desc)=1
