with stg as (
    select * from {{ ref('stg_freework_jobs') }}
),

skills_categorized as (
    select
        *,
        {{ categorize_skills('normalized_skills') }} as skill_categories
    from stg
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
from skills_categorized
order by publication_date desc