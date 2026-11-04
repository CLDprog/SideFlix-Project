select replace(f.value:article::string,'_',' ') as wikipedia_article,
    try_to_date(substr(f.value:timestamp::string,1,8),'YYYYMMDD') as view_date,
    try_to_number(f.value:views::string) as pageviews,
    w.source_system,w._batch_id,w._source_file,w._loaded_at
from {{ source('bronze','wikimedia_raw') }} w,lateral flatten(w.raw:items) f
where w._batch_id='{{ var("batch_wikimedia") }}'
qualify row_number() over(partition by f.value:article::string,f.value:timestamp::string
    order by w._loaded_at desc,w._source_file desc,to_json(f.value) desc)=1
