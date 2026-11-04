with totals as (
    select (select count(*) from {{ ref('stg_sessions') }}) as raw_rows,
        (select count(*) from {{ ref('quarantine_sessions') }}) as rejects,
        (select count(*) from {{ ref('silver_sessions') }}) as retained,
        (select count(*)-count(distinct session_id) from {{ ref('stg_sessions') }}
            where session_id not in (select session_id from {{ ref('quarantine_sessions') }})) as duplicates
)
select * from totals where raw_rows<>retained+rejects+duplicates or rejects<>1 or duplicates<>1
