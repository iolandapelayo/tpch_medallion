-- Grain: one row per customer that has ever ordered.
-- Health of each account on the "as of" date (the last order date in the data),
-- with three simple, explainable risk signals and a final risk level.

with as_of as (

    select max(order_date) as as_of_date
    from {{ ref('fct_orders') }}

),

orders as (

    select
        f.*,
        a.as_of_date,
        f.order_date > dateadd(month, -12, a.as_of_date)          as in_last_12m,
        f.order_date <= dateadd(month, -12, a.as_of_date)
            and f.order_date > dateadd(month, -24, a.as_of_date)  as in_prev_12m
    from {{ ref('fct_orders') }} as f
    cross join as_of as a

),

accounts as (

    select
        customer_key,
        any_value(as_of_date)                               as as_of_date,
        min(order_date)                                     as first_order_date,
        max(order_date)                                     as last_order_date,
        count(*)                                            as lifetime_orders,
        sum(net_revenue)                                    as lifetime_revenue,
        count_if(in_last_12m)                               as orders_last_12m,
        sum(iff(in_last_12m, net_revenue, 0))               as revenue_last_12m,
        sum(iff(in_prev_12m, net_revenue, 0))               as revenue_prev_12m,
        -- service quality: only orders already fully delivered on the as-of date
        avg(case when in_last_12m and delivered_date <= as_of_date
                 then iff(is_late, 1, 0) end)               as late_order_rate_12m
    from orders
    group by customer_key

),

signals as (

    select
        *,
        datediff(day, last_order_date, as_of_date)                                      as days_since_last_order,
        datediff(day, first_order_date, last_order_date) / nullif(lifetime_orders - 1, 0) as avg_days_between_orders,
        div0(revenue_last_12m - revenue_prev_12m, revenue_prev_12m)                     as revenue_change_pct,
        percent_rank() over (order by lifetime_revenue desc)                            as revenue_percentile
    from accounts

),

flags as (

    select
        *,
        -- 1. Overdue: no order for much longer than this customer usually waits
        coalesce(days_since_last_order > {{ var('overdue_factor') }} * avg_days_between_orders, false)
                                                                        as is_overdue,
        -- 2. Declining: revenue of the last 12 months fell sharply vs the 12 before
        revenue_last_12m < (1 - {{ var('decline_threshold') }}) * revenue_prev_12m
                                                                        as is_declining,
        -- 3. Service issues: among the 25% of accounts with the most late orders
        late_order_rate_12m is not null
            and percent_rank() over (order by late_order_rate_12m nulls first) >= 0.75
                                                                        as has_service_issues
    from signals

),

scored as (

    select
        *,
        iff(is_overdue, 1, 0) + iff(is_declining, 1, 0) + iff(has_service_issues, 1, 0) as risk_signals
    from flags

)

select
    customer_key,
    as_of_date,
    case
        when revenue_percentile < 0.2 then 'A'      -- top 20% of accounts by lifetime revenue
        when revenue_percentile < 0.5 then 'B'
        else 'C'
    end                                             as account_tier,
    first_order_date,
    last_order_date,
    days_since_last_order,
    round(avg_days_between_orders)                  as avg_days_between_orders,
    lifetime_orders,
    lifetime_revenue,
    orders_last_12m,
    revenue_last_12m,
    revenue_prev_12m,
    revenue_change_pct,
    late_order_rate_12m,
    is_overdue,
    is_declining,
    has_service_issues,
    risk_signals,
    case
        when orders_last_12m = 0 then 'Inactive'    -- already stopped buying: win-back list
        when risk_signals >= 2   then 'High'
        when risk_signals = 1    then 'Medium'
        else 'Low'
    end                                             as risk_level,
    iff(risk_signals >= 1 and orders_last_12m > 0, revenue_last_12m, 0)
                                                    as revenue_at_risk
from scored
