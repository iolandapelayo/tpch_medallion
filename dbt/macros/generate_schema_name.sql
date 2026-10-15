{#
    By default dbt would name schemas <target schema>_<layer> (e.g. PUBLIC_BRONZE).
    We want exactly BRONZE / SILVER / GOLD, except in CI, where the layers get a
    CI_ prefix so pull-request builds never touch the real tables.
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- elif target.name == 'ci' -%}
        CI_{{ custom_schema_name | upper }}
    {%- else -%}
        {{ custom_schema_name | upper }}
    {%- endif -%}
{%- endmacro %}
