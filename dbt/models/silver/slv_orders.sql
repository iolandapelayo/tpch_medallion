select
    o_orderkey                                              as order_id,
    o_custkey                                               as customer_id,
    o_orderdate                                             as order_date,
    o_totalprice                                            as order_total_price,
    {{ map_values('o_orderstatus', {
        'F': 'Fulfilled',
        'O': 'Open',
        'P': 'Partially fulfilled'
    }) }}                                                   as order_status,
    -- o_orderpriority looks like '1-URGENT': keep only the label
    initcap(split_part(trim(o_orderpriority), '-', 2))      as order_priority
from {{ ref('brz_tpch__orders') }}
