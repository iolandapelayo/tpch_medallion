select
    l_orderkey                                              as order_id,
    l_linenumber                                            as line_number,
    l_partkey                                               as part_id,
    l_suppkey                                               as supplier_id,
    l_quantity                                              as quantity,
    l_extendedprice                                         as gross_amount,
    l_discount                                              as discount_rate,
    l_tax                                                   as tax_rate,
    l_shipdate                                              as ship_date,
    l_commitdate                                            as commit_date,
    l_receiptdate                                           as receipt_date,
    initcap({{ clean_string('l_shipmode') }})               as ship_mode,
    {{ map_values('l_returnflag', {
        'R': 'Returned',
        'A': 'Accepted',
        'N': 'Not returned'
    }) }}                                                   as return_status,

    -- Revenue rules (TPC-H specification), defined once so every Gold model shares them
    round(l_extendedprice * l_discount, 2)                          as discount_amount,
    round(l_extendedprice * (1 - l_discount), 2)                    as net_amount,
    round(l_extendedprice * (1 - l_discount) * (1 + l_tax), 2)      as billed_amount,

    -- Delivery rule: late = received after the date committed to the customer
    l_receiptdate > l_commitdate                            as is_late_delivery
from {{ ref('brz_tpch__lineitem') }}
