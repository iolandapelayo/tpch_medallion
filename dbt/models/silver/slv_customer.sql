select
    c_custkey                                       as customer_id,
    {{ clean_string('c_name') }}                    as customer_name,
    c_nationkey                                     as nation_id,
    c_acctbal                                       as account_balance,
    initcap({{ clean_string('c_mktsegment') }})     as market_segment
from {{ ref('brz_tpch__customer') }}
