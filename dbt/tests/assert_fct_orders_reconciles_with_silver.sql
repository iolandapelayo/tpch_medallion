-- The Gold aggregation must not lose or duplicate lines:
-- fct_orders must hold the same number of lines and net revenue as the Silver lines
-- of the portfolio's customers (computed here straight from Silver, independently of dim_customer).
with silver as (
    select count(*) as n_lines, sum(l.net_amount) as revenue
    from {{ ref('slv_lineitem') }} as l
    join {{ ref('slv_orders') }} as o on l.order_id = o.order_id
    join {{ ref('slv_customer') }} as c on o.customer_id = c.customer_id
    join {{ ref('slv_nation') }} as n on c.nation_id = n.nation_id
    join {{ ref('slv_region') }} as r on n.region_id = r.region_id
    where c.market_segment = '{{ var("portfolio_segment") }}'
      and r.region_name = '{{ var("portfolio_region") }}'
),

gold as (
    select sum(order_lines) as n_lines, sum(net_revenue) as revenue from {{ ref('fct_orders') }}
)

select *
from silver, gold
where silver.n_lines != gold.n_lines
   or silver.revenue != gold.revenue
