-- The Gold aggregation must not lose or duplicate lines:
-- fct_orders must hold the same number of lines and net revenue as slv_lineitem.
with silver as (
    select count(*) as n_lines, sum(net_amount) as revenue from {{ ref('slv_lineitem') }}
),

gold as (
    select sum(order_lines) as n_lines, sum(net_revenue) as revenue from {{ ref('fct_orders') }}
)

select *
from silver, gold
where silver.n_lines != gold.n_lines
   or silver.revenue != gold.revenue
