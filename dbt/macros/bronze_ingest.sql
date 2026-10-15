{#
    Copies a source table as-is into Bronze and adds the load timestamp.
    Nothing is renamed, cast or filtered: Bronze is a faithful copy of the source.
#}
{% macro bronze_ingest(table_name) %}
select
    *,
    current_timestamp()::timestamp_ntz as _ingested_at
from {{ source('tpch', table_name) }}
{% endmacro %}
