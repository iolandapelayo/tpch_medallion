-- One row per call to a customer, with the same customer id as the rest of Silver.
-- A view, like its Bronze source, so new calls are visible straight away.
{{ config(materialized='view') }}

select
    call_id,
    customer_key                    as customer_id,
    called_at,
    {{ clean_string('notes') }}     as notes,
    logged_by
from {{ ref('brz_kam__call_log') }}
