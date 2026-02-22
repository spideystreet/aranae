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

select 
    job_id,
    title,
    company,
    publication_date,
    city,
    region,
    url,
    raw_skills,
    normalized_skills,
    skill_categories,
    contracts,
    description,
    salary,
    tjm,
    duration,
    experience_level,
    start_date,
    remote,
    source,
    scraped_at
from unioned