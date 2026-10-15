select
    c.customer_id           as customer_key,
    c.customer_name,
    c.market_segment,
    n.nation_name           as customer_nation,
    r.region_name           as customer_region,
    c.account_balance
from {{ ref('slv_customer') }} as c
join {{ ref('slv_nation') }} as n on c.nation_id = n.nation_id
join {{ ref('slv_region') }} as r on n.region_id = r.region_id
