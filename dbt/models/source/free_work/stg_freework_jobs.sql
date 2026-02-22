with source as (
    select * from {{ source('free_work', 'RAW_FREEWORK') }}
    where source = 'free-work'
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
        contracts,
        description,
        income as raw_income,
        {{ extract_income('income', 'salary') }} as salary,
        {{ extract_income('income', 'tjm') }} as tjm,
        duration,
        experience_level,
        start_date,
        CASE 
            WHEN lower(remote) LIKE '%100%%' OR lower(remote) LIKE '%total%' THEN 'Télétravail 100%'
            WHEN lower(remote) LIKE '%télétravail%' OR lower(remote) LIKE '%remote%' THEN 'Télétravail partiel'
            ELSE 'Pas d''infos'
        END as remote,
        source,
        scraped_at
    from source
)

select * from final
where publication_date is not null