select
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
from {{ ref('stg_freework__jobs') }}
order by publication_date desc
