select
    r_regionkey                             as region_id,
    initcap({{ clean_string('r_name') }})   as region_name
from {{ ref('brz_tpch__region') }}
