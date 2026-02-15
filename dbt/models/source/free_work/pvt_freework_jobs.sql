{{ config(
    materialized='table'
) }}

select * from {{ ref('stg_freework_jobs') }}
order by publication_date desc
