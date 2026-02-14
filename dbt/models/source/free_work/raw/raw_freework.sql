
select * from {{ source('dagster_raw', 'raw_freework_jobs') }}
