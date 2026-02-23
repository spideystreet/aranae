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
        -- WTTJ income is structured, so we can trust it more.
        -- If it contains 'EUR', 'k' or looks like a salary, treat as salary.
        -- TJM is rare on WTTJ but possible.
        {{ format_wttj_salary('income') }} as salary,
        -- WTTJ rarely has TJM in the income field the way Freework does
        NULL as tjm,
        duration,
        {{ normalize_experience('experience_level') }},
        start_date,
        -- MAPPING WTTJ REMOTE (RAW -> STANDARD)
        source,
        -- MAPPING WTTJ CONTRACTS (RAW -> STANDARD)
        scraped_at,
        case
            when remote = 'full' then 'Télétravail 100%'
            when remote in ('partial', 'punctual') then 'Télétravail partiel'
            when remote = 'no' then 'Présentiel'
            else 'Pas d''infos'
        end as remote,
        case
            when contracts = 'full_time' then 'CDI'
            when contracts = 'temporary' then 'CDD'
            when contracts = 'apprenticeship' then 'Alternance'
            when contracts = 'internship' then 'Stage'
            when contracts = 'freelance' then 'Freelance'
            else contracts -- Keep raw if unknown
        end as contracts
    from source
)

select * from final
where
    publication_date is not NULL
    and title is not NULL
