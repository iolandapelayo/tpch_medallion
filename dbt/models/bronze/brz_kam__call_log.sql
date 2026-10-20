-- Calls logged by the Key Account Manager through the Streamlit form (schema KAM_INPUT).
-- A view, not a table: a call logged a minute ago reaches Gold and Power BI without running dbt.
{{ config(materialized='view') }}

select
    *,
    current_timestamp()::timestamp_ntz as _ingested_at
from {{ source('kam_input', 'call_log') }}
