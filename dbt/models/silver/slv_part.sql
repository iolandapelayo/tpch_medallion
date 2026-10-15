select
    p_partkey                                   as part_id,
    {{ clean_string('p_name') }}                as part_name,
    {{ clean_string('p_mfgr') }}                as manufacturer,
    {{ clean_string('p_brand') }}               as brand,
    -- p_type is a 3-word code such as 'STANDARD POLISHED BRASS': split it to analyse each part
    initcap(split_part(trim(p_type), ' ', 1))   as part_type_class,
    initcap(split_part(trim(p_type), ' ', 2))   as part_finish,
    initcap(split_part(trim(p_type), ' ', 3))   as part_material,
    p_size                                      as part_size,
    -- p_container is a 2-word code such as 'SM CASE'
    split_part(trim(p_container), ' ', 1)       as container_size,
    split_part(trim(p_container), ' ', 2)       as container_type,
    p_retailprice                               as retail_price
from {{ ref('brz_tpch__part') }}
