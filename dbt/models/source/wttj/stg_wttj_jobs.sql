with source as (
    select * from {{ source('wttj', 'RAW_WTTJ') }}
    where source = 'wttj'
),

final as (
    select
        job_id,
        title,
        company,
        {{ normalize_date('publication_date') }} as publication_date,
        city,
        region,
        location as raw_location,
        url,
        skills as raw_skills,
        {{ standardize_skills('skills') }} as normalized_skills,
        description,
        income as raw_income,
        {{ format_wttj_salary('income') }} as salary,
        NULL as tjm,
        duration,
        {{ normalize_experience('experience_level') }} as experience_level,
        start_date,
        CASE 
            WHEN remote = 'full' THEN 'Télétravail 100%'
            WHEN remote IN ('partial', 'punctual') THEN 'Télétravail partiel'
            WHEN remote = 'no' THEN 'Présentiel'
            ELSE 'Pas d''infos'
        END as remote,
        CASE 
            WHEN contracts = 'full_time' THEN 'CDI'
            WHEN contracts = 'temporary' THEN 'CDD'
            WHEN contracts = 'apprenticeship' THEN 'Alternance'
            WHEN contracts = 'internship' THEN 'Stage'
            WHEN contracts = 'freelance' THEN 'Freelance'
            ELSE contracts
        END as contracts,
        source,
        scraped_at
    from source
)

select * from final
where publication_date is not null