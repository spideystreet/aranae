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
),

enriched as (
    select 
        *,
        {{ generate_job_tags('title', 'description', 'skills') }} as tags
    from unioned
)

select * from enriched