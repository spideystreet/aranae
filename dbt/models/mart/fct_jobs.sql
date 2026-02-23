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
    {{ normalize_city('city') }} as city,
    region,
    url,
    skills,
    contracts,
    description,
    salary,
    tjm,
    duration,
    {{ categorize_experience('experience_level') }} as experience_level,
    start_date,
    remote,
    source,
    scraped_at
from unioned
