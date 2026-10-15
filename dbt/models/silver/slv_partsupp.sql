select
    ps_partkey      as part_id,
    ps_suppkey      as supplier_id,
    ps_supplycost   as supply_cost
from {{ ref('brz_tpch__partsupp') }}
