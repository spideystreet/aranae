{{ config(materialized='table') }}

with source as (
    select * from {{ source('wttj', 'RAW_WTTJ') }}
    where source = 'wttj'
),

final as (
    select
        job_id,
        title,
        company,
        -- Normalize Date
        {{ normalize_date('publication_date') }} as publication_date,
        -- Use explicit city/region from source
        city,
        region,
        
        location as raw_location,
        url,
        skills,
        description,
        income as raw_income,
        {{ extract_income('income', 'salary') }} as salary,
        {{ extract_income('income', 'tjm') }} as tjm,
        duration,
        {{ normalize_experience('experience_level') }} as experience_level,
        start_date,
        -- MAPPING WTTJ REMOTE (RAW -> STANDARD)
        CASE 
            WHEN remote = 'full' THEN 'Télétravail 100%'
            WHEN remote IN ('partial', 'punctual') THEN 'Télétravail partiel'
            WHEN remote = 'no' THEN 'Présentiel'
            ELSE 'Pas d''infos'
        END as remote,
        -- MAPPING WTTJ CONTRACTS (RAW -> STANDARD)
        CASE 
            WHEN contracts = 'full_time' THEN 'CDI'
            WHEN contracts = 'temporary' THEN 'CDD'
            WHEN contracts = 'apprenticeship' THEN 'Alternance'
            WHEN contracts = 'internship' THEN 'Stage'
            WHEN contracts = 'freelance' THEN 'Freelance'
            ELSE contracts -- Keep raw if unknown
        END as contracts,
        source,
        scraped_at
    from source
)

select * from final
where publication_date is not null
