-- Has the Key Account Manager called each portfolio customer recently? One row per customer.
-- "Called" = at least one call in the last 7 days (var called_window_days), so every week
-- an account that was not called again comes back to the worklist.
-- A view: the status is computed when Power BI refreshes, with the calls logged up to that moment.
{{ config(materialized='view') }}

with last_calls as (
    select
        customer_id,
        max(called_at)  as last_called_at,
        count_if(called_at >= dateadd('day', -{{ var('called_window_days') }}, current_timestamp()::timestamp_ntz))
                        as calls_last_window
    from {{ ref('slv_call_log') }}
    group by customer_id
)

select
    c.customer_key,
    l.last_called_at,
    coalesce(l.calls_last_window, 0)                                        as recent_calls,
    iff(coalesce(l.calls_last_window, 0) > 0, 'Called', 'Not called')       as call_status,
    iff(coalesce(l.calls_last_window, 0) > 0, 2, 1)                         as call_status_order
from {{ ref('dim_customer') }} as c
left join last_calls as l on c.customer_key = l.customer_id
