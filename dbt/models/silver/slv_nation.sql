select
    n_nationkey                             as nation_id,
    initcap({{ clean_string('n_name') }})   as nation_name,
    n_regionkey                             as region_id
from {{ ref('brz_tpch__nation') }}
