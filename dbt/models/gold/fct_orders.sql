-- Grain: one row per order of the Key Account Manager's portfolio.
-- Each order with its revenue and whether it was delivered late.
select
    o.order_id,
    o.customer_id                           as customer_key,
    {{ date_key('o.order_date') }}          as order_date_key,
    o.order_date,
    o.order_status,
    o.order_priority,
    count(*)                                as order_lines,
    sum(l.net_amount)                       as net_revenue,
    max(l.receipt_date)                     as delivered_date,     -- when the last line arrived
    count_if(l.is_late_delivery)            as late_lines,
    count_if(l.is_late_delivery) > 0        as is_late             -- at least one line arrived late
from {{ ref('slv_orders') }} as o
join {{ ref('dim_customer') }} as c                -- keeps only the portfolio's customers
    on o.customer_id = c.customer_key
join {{ ref('slv_lineitem') }} as l
    on o.order_id = l.order_id
group by all
