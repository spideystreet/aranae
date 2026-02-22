{% macro generate_job_tags(title, description, skills) %}
    array_distinct(array_concat(
        -- Extract seniority
        case 
            when lower({{ title }}) ~ '(senior|lead|principal|architect)' then array['senior']
            when lower({{ title }}) ~ '(junior|graduate|junior)' then array['junior']
            else array[]
        end,
        
        -- Extract tech stack
        array_concat(
            case when lower({{ title }}) ~ '(python|django|flask)' 
                or lower({{ description }}) ~ '(python|django|flask)' 
                or {{ skills }}::text ~ '(python|django|flask)'
                then array['python'] else array[] end,
                
            case when lower({{ title }}) ~ '(js|javascript|node|react|vue|angular)' 
                or lower({{ description }}) ~ '(js|javascript|node|react|vue|angular)'
                or {{ skills }}::text ~ '(js|javascript|node|react|vue|angular)'
                then array['javascript'] else array[] end,
                
            case when lower({{ title }}) ~ '(data.*engineer|etl|pipeline)' 
                or lower({{ description }}) ~ '(data.*engineer|etl|pipeline)'
                or {{ skills }}::text ~ '(data.*engineer|etl|pipeline)'
                then array['data-engineering'] else array[] end
        ),
        
        -- Extract contract type
        case 
            when lower({{ title }}) ~ '(cdi|permanent)' then array['permanent']
            when lower({{ title }}) ~ '(freelance|contractor)' then array['freelance']
            else array[]
        end
    ))
{% endmacro %}