
{{ config(
    materialized='table'
) }}

with source as (
    select * from {{ source('free_work', 'raw_freework_jobs') }}
),

deduplicated as (
    select
        *,
        row_number() over (partition by job_id order by scraped_at desc) as rn
    from source
),

final as (
    select
        job_id,
        title,
        company,
        -- Apply transformations here:
        -- 1. Normalize Date
        {{ normalize_date('publication_date') }} as publication_date,
        -- 2. Extract City
        split_part(location, ',', 1) as city,
        
        location as raw_location,
        url,
        skills,
        contracts,
        description,
        income as raw_income,
        {{ extract_income('income', 'salary') }} as salary,
        {{ extract_income('income', 'tjm') }} as tjm,
        duration,
        experience_level,
        start_date,
        source,
        scraped_at
    from deduplicated
    where rn = 1
)

select * from final
where publication_date is not null
