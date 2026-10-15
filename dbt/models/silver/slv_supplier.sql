select
    s_suppkey                                       as supplier_id,
    {{ clean_string('s_name') }}                    as supplier_name,
    s_nationkey                                     as nation_id,
    s_acctbal                                       as account_balance,
    -- TPC-H business rule (query Q16): a comment containing "Customer ... Complaints"
    -- means the supplier has open customer complaints
    s_comment ilike '%customer%complaints%'         as has_customer_complaints
from {{ ref('brz_tpch__supplier') }}
