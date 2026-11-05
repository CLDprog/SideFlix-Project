-- Flatten the received entity and its IMDb claim; join on verified stable identifiers.
-- Wikidata may keep only the multilingual default label ("mul") when it equals the English one.
select c.content_id,e.key::string as wikidata_qid,
    coalesce(e.value:labels:en:value::string, e.value:labels:mul:value::string) as wikidata_label,
    e.value:descriptions:en:value::string as description_en,
    e.value:sitelinks:enwiki:title::string as wikipedia_article,
    w.source_system,w._batch_id,w._source_file,w._loaded_at
from {{ source('bronze','wikidata_raw') }} w,
    lateral flatten(w.raw:entities) e,
    lateral flatten(e.value:claims:P345) p,
    {{ ref('silver_catalog') }} c
where w._batch_id='{{ var("batch_wikidata") }}'
  and p.value:mainsnak:datavalue:value::string=c.imdb_tconst
qualify row_number() over(partition by c.content_id order by w._loaded_at desc,w._source_file desc,e.key desc)=1
