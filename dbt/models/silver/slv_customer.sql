select
    c_custkey                                       as customer_id,
    {{ clean_string('c_name') }}                    as customer_name,
    c_nationkey                                     as nation_id,
    c_acctbal                                       as account_balance,
    initcap({{ clean_string('c_mktsegment') }})     as market_segment,
    {{ clean_string('c_phone') }}                   as phone,
    {{ clean_string('c_address') }}                 as address,
    -- SYNTHETIC, for the demo: TPC-H has no contact person, so each customer gets two initials
    -- derived from its id (always the same ones). With real data this would come from the CRM.
    chr(65 + mod(c_custkey, 26)) || '. ' || chr(65 + mod(floor(c_custkey / 26), 26)) || '.'
                                                    as contact_person
from {{ ref('brz_tpch__customer') }}
