-- TPC-H rule: an order's total price equals the sum of its lines' billed amounts.
-- Returns the orders where the difference exceeds 2 cents per line: the TPC-H generator
-- rounds the discount and the tax separately, so each line can differ by up to 2 cents.
with lines as (

    select order_id, count(*) as n_lines, sum(billed_amount) as lines_total
    from {{ ref('slv_lineitem') }}
    group by order_id

)

select o.order_id, o.order_total_price, l.lines_total
from {{ ref('slv_orders') }} as o
join lines as l on o.order_id = l.order_id
where abs(o.order_total_price - l.lines_total) > 0.02 * l.n_lines
