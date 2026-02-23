{% macro extract_income(income_column, income_type) %}
    CASE
        {% if income_type == 'salary' %}
            -- Extracts patterns ending with 'an', handles / and ⁄
            WHEN {{ income_column }} ~* '(/|⁄)\s*an' 
            THEN trim(substring({{ income_column }} from '(?i)([^,]*€\s*(/|⁄)\s*an)'))
        {% elif income_type == 'tjm' %}
            -- Extracts patterns ending with 'j', handles / and ⁄
            WHEN {{ income_column }} ~* '(/|⁄)\s*j' 
            THEN trim(substring({{ income_column }} from '(?i)([^,]*€\s*(/|⁄)\s*j)'))
        {% endif %}
        ELSE NULL
    END
{% endmacro %}
