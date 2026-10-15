-- Business alarm: each risk signal must single out a minority of accounts.
-- A signal that flags almost nobody (< 1%) or almost everybody (> 60%) does not help a
-- Key Account Manager choose whom to call, and usually means the logic or the thresholds broke.
-- (This test would have caught a bug where service issues flagged 0 accounts.)
with shares as (

    select 'overdue' as signal, avg(iff(is_overdue, 1, 0)) as share_flagged
    from {{ ref('fct_account_health') }}
    union all
    select 'declining', avg(iff(is_declining, 1, 0))
    from {{ ref('fct_account_health') }}
    union all
    select 'service issues', avg(iff(has_service_issues, 1, 0))
    from {{ ref('fct_account_health') }}

)

select *
from shares
where share_flagged < 0.01
   or share_flagged > 0.60
