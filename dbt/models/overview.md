{% docs __overview__ %}
# TPC-H Key Account Health - Medallion architecture

| Layer | Schema | Content |
|---|---|---|
| Bronze | `BRONZE` | Exact copy of the 8 TPC-H tables + load timestamp (`brz_tpch__*`) |
| Silver | `SILVER` | Clean, readable entities + revenue and delivery rules, for any use case (`slv_*`) |
| Gold | `GOLD` | One Key Account Manager's portfolio: `fct_account_health` (one row per account), `fct_orders`, `dim_customer`, `dim_date` |

**Use case:** account health and churn risk for the Key Account Manager of **Furniture accounts in the United Kingdom**
(dbt vars `portfolio_segment` and `portfolio_nation`): which of their accounts are cooling down,
why (overdue, declining revenue, poor service) and how much revenue is at stake.

Open the lineage graph (bottom-right button) to follow source -> Bronze -> Silver -> Gold -> dashboard.
{% enddocs %}
