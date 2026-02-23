{% macro format_wttj_salary(income_column) %}
    CASE
        -- Handle Range: 45000-55000 EUR -> 45K-55K €/an
        WHEN {{ income_column }} ~ '^\d+000-\d+000 EUR$' THEN
            regexp_replace(
                regexp_replace({{ income_column }}, '(\d+)000', '\1K', 'g'),
                ' EUR', ' €/an'
            )
        -- Handle Single: 45000 EUR -> 45K €/an
        WHEN {{ income_column }} ~ '^\d+000 EUR$' THEN
            regexp_replace(
                regexp_replace({{ income_column }}, '(\d+)000', '\1K', 'g'),
                ' EUR', ' €/an'
            )
        -- Handle 'k' notation if present e.g. 45k-55k
        WHEN {{ income_column }} ~ '^\d+k-\d+k EUR$' THEN
            regexp_replace({{ income_column }}, ' EUR', ' €/an', 'i')
        
        -- Fallback: Just replace EUR with €
        ELSE replace({{ income_column }}, ' EUR', ' €')
    END
{% endmacro %}
