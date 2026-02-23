{% macro categorize_experience(exp_column) %}
CASE
    WHEN {{ exp_column }} IS NULL
        THEN NULL

    -- "X mois…" patterns are always sub-1-year → Junior
    -- Must be checked first to avoid "6 mois" being parsed as 6 years
    WHEN {{ exp_column }} ~* '\d+\s*mois'
        THEN 'Junior'

    -- Extract the lower-bound year number and classify
    WHEN (regexp_match({{ exp_column }}, '(\d+)'))[1]::int < 3
        THEN 'Junior'

    WHEN (regexp_match({{ exp_column }}, '(\d+)'))[1]::int BETWEEN 3 AND 4
        THEN 'Confirmé'

    WHEN (regexp_match({{ exp_column }}, '(\d+)'))[1]::int BETWEEN 5 AND 7
        THEN 'Senior'

    WHEN (regexp_match({{ exp_column }}, '(\d+)'))[1]::int >= 8
        THEN 'Lead / Expert'

    ELSE NULL
END
{% endmacro %}
