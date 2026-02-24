with freework as (
    select * from {{ ref('pvt_freework_jobs') }}
),

wttj as (
    select * from {{ ref('pvt_wttj_jobs') }}
),

unioned as (
    select * from freework
    union all
    select * from wttj
)

select * from unioned
order by publication_date desc
