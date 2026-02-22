with source_union as (
    select * from {{ ref('pvt_freework_jobs') }}
    union all
    select * from {{ ref('pvt_wttj_jobs') }}
),

-- Remove potential duplicates (same job posted on multiple platforms)
deduplicated as (
    select
        *,
        row_number() over (
            partition by 
                lower(trim(title)), 
                lower(trim(company)),
                city
            order by publication_date desc
        ) as rank
    from source_union
),

final as (
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
        scraped_at,
        {{ datediff('publication_date', current_timestamp(), 'day') }} as days_since_publication
    from deduplicated
    where rank = 1
)

select * from final