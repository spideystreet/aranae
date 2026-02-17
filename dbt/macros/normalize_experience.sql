{% macro normalize_experience(exp_column) %}
    CASE
        -- X_TO_Y_YEARS -> X à Y ans d'expérience
        WHEN {{ exp_column }} ~ '^\d+_TO_\d+_YEARS?$' THEN 
            regexp_replace({{ exp_column }}, '^(\d+)_TO_(\d+)_YEARS?$', '\1 à \2 ans d''expérience')
        
        -- MORE_THAN_X_YEARS -> Plus de X ans d'expérience
        WHEN {{ exp_column }} ~ '^MORE_THAN_\d+_YEARS?$' THEN 
            regexp_replace({{ exp_column }}, '^MORE_THAN_(\d+)_YEARS?$', 'Plus de \1 ans d''expérience')

        -- LESS_THAN_X_YEARS -> Moins de X ans d'expérience
        WHEN {{ exp_column }} ~ '^LESS_THAN_\d+_YEARS?$' THEN 
            regexp_replace({{ exp_column }}, '^LESS_THAN_(\d+)_YEARS?$', 'Moins de \1 ans d''expérience')
            
        -- X_MONTHS_TO_Y_YEAR -> X mois à Y ans d'expérience
        WHEN {{ exp_column }} ~ '^\d+_MONTHS_TO_\d+_YEARS?$' THEN 
            regexp_replace({{ exp_column }}, '^(\d+)_MONTHS_TO_(\d+)_YEARS?$', '\1 mois à \2 ans d''expérience')

        -- LESS_THAN_X_MONTHS -> Moins de X mois d'expérience
        WHEN {{ exp_column }} ~ '^LESS_THAN_\d+_MONTHS?$' THEN 
            regexp_replace({{ exp_column }}, '^LESS_THAN_(\d+)_MONTHS?$', 'Moins de \1 mois d''expérience')

        ELSE {{ exp_column }}
    END
{% endmacro %}
