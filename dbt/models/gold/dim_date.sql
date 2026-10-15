-- One row per day from 1992-01-01 to 1998-12-31 (2,557 days), the full TPC-H date range
with days as (

    select dateadd(day, row_number() over (order by seq4()) - 1, '1992-01-01'::date) as full_date
    from table(generator(rowcount => 2557))

)

select
    {{ date_key('full_date') }}     as date_key,
    full_date,
    year(full_date)                 as year,
    quarter(full_date)              as quarter,
    month(full_date)                as month,
    monthname(full_date)            as month_name,
    to_char(full_date, 'YYYY-MM')   as year_month,
    dayname(full_date)              as day_name
from days
