{% macro normalize_date(date_column) %}
    CASE
        -- YYYY-MM-DD
        WHEN {{ date_column }} ~ '^\d{4}-\d{2}-\d{2}$' THEN to_date({{ date_column }}, 'YYYY-MM-DD')
        
        -- DD/MM/YYYY (French, day > 12 implies clearly DD/MM)
        WHEN {{ date_column }} ~ '^(1[3-9]|2\d|3[01])/(0\d|1[0-2])/\d{4}$' THEN to_date({{ date_column }}, 'DD/MM/YYYY')
        
        -- MM/DD/YYYY (US, month <= 12. If ambiguous 01/01/2026, defaults here, check context)
        -- Free-Work often returns US format 02/13/2026 -> 13 Feb 2026
        WHEN {{ date_column }} ~ '^(0\d|1[0-2])/(0\d|1\d|2\d|3[01])/\d{4}$' THEN to_date({{ date_column }}, 'MM/DD/YYYY')
        
        ELSE NULL
    END
{% endmacro %}
