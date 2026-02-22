{% macro standardize_skills(skills_field) %}
    (
        select array_agg(distinct lower(trim(skill)))
        from unnest(
            regexp_split_to_array(
                -- Nettoie et normalise le texte
                regexp_replace(
                    lower({{ skills_field }}),
                    '[,.;]',
                    ' '
                ),
                '\s+'
            )
        ) as skill
        where length(skill) > 1  -- Ignore les caractères seuls
    )
{% endmacro %}

{% macro categorize_skills(skills_array) %}
    array_agg(distinct 
        case
            -- Langages
            when skill like any(array['%python%', 'django%', 'flask%']) then 'python'
            when skill like any(array['%java%', 'spring%', 'hibernate%']) then 'java'
            when skill like any(array['%javascript%', '%js%', 'node%', 'react%', 'vue%', 'angular%']) then 'javascript'
            -- Data
            when skill like any(array['%sql%', 'postgresql%', 'mysql%', 'oracle%']) then 'sql'
            when skill like any(array['%data%engineer%', 'etl%', 'airflow%', 'dbt%']) then 'data-engineering'
            when skill like any(array['%data%scien%', 'ml%', 'tensorflow%', 'pytorch%']) then 'data-science'
            -- DevOps
            when skill like any(array['%docker%', '%kubernetes%', 'k8s%', '%aws%', '%azure%', '%gcp%']) then 'cloud'
            when skill like any(array['%ci%cd%', 'github%action%', 'jenkins%', 'gitlab%ci%']) then 'ci-cd'
            -- Autres restent tels quels
            else skill
        end
    )
{% endmacro %}