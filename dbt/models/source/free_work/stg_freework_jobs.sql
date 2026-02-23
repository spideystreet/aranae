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
        {{ normalize_city('city') }} as city,
        region,
        location as raw_location,
        url,
        skills,
        -- Sort contract values alphabetically so "CDI, Freelance" and "Freelance, CDI" are treated as the same
        array_to_string(
            array(
                select unnest(string_to_array(contracts, ', '))
                order by 1
            ),
            ', '
        ) as contracts,
        description,
        income as raw_income,
        {{ extract_income('income', 'salary') }} as salary,
        {{ extract_income('income', 'tjm') }} as tjm,
        duration,
        {{ categorize_experience('experience_level') }} as experience_level,
        start_date,
        -- mapping freework remote naming conventions ('%%' escapes literal '%' in LIKE)
        case
            when
                lower(remote) like '%100%%' or lower(remote) like '%total%'
                then 'Télétravail 100%'
            when
                lower(remote) like '%télétravail%'
                or lower(remote) like '%remote%'
                then 'Télétravail partiel'
            else 'Pas d''infos'
        end as remote,
        source,
        scraped_at
    from source
)

select * from final
where
    publication_date is not null
    and title is not null
