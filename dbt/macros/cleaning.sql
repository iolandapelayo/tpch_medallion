{# Trims whitespace and turns empty strings into NULL. #}
{% macro clean_string(column) -%}
    nullif(trim({{ column }}), '')
{%- endmacro %}


{#
    Translates source codes into readable labels.
    Usage: {{ map_values('l_returnflag', {'R': 'Returned', 'A': 'Accepted'}) }}
#}
{% macro map_values(column, mapping) -%}
    case trim({{ column }})
        {%- for code, label in mapping.items() %}
        when '{{ code }}' then '{{ label }}'
        {%- endfor %}
        else 'Unknown'
    end
{%- endmacro %}


{# Integer key YYYYMMDD used to join facts with dim_date. #}
{% macro date_key(column) -%}
    to_number(to_char({{ column }}, 'YYYYMMDD'))
{%- endmacro %}
