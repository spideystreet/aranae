with stg as (
    select * from {{ ref('stg_wttj_jobs') }}
)

select
    -- FIXED ORDER TO MATCH FREEWORK
    job_id,
    title,
    company,
    publication_date,
    city,
    region,
    url,
    skills,
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
from stg
