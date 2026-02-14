
with source as (
    select * from {{ source('free_work', 'raw_freework_jobs') }}
),

deduplicated as (
    select
        *,
        row_number() over (partition by job_id order by scraped_at desc) as rn
    from source
)

select
    job_id,
    title,
    company,
    date_posted,
    url,
    skills,
    contracts,
    description,
    income,
    duration,
    experience_level,
    location,
    source,
    scraped_at
from deduplicated
where rn = 1
