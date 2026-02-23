{% macro normalize_date(date_column) %}
    CASE
        -- YYYY-MM-DD (ISO simple)
        WHEN {{ date_column }} ~ '^\d{4}-\d{2}-\d{2}$' THEN to_date({{ date_column }}, 'YYYY-MM-DD')
        
        -- YYYY-MM-DDTHH:MM:SS... (ISO Timestamp)
        WHEN {{ date_column }} ~ '^\d{4}-\d{2}-\d{2}T.*$' THEN cast({{ date_column }} as date)
        
        -- DD/MM/YYYY (French)
        WHEN {{ date_column }} ~ '^(1[3-9]|2\d|3[01])/(0\d|1[0-2])/\d{4}$' THEN to_date({{ date_column }}, 'DD/MM/YYYY')
        
        -- MM/DD/YYYY (US format — Free-Work always sends this format e.g. 02/13/2026 -> 13 Feb 2026)
        -- NOTE: dates with day <= 12 (e.g. 01/03/2026) are ambiguous and assumed US here.
        -- This is intentional: Free-Work is the only source using this branch and it is US-formatted.
        WHEN {{ date_column }} ~ '^(0\d|1[0-2])/(0\d|1\d|2\d|3[01])/\d{4}$' THEN to_date({{ date_column }}, 'MM/DD/YYYY')
        
        ELSE cast(NULL as date)
    END
{% endmacro %}
