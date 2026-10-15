# TPC-H Medallion Architecture on Snowflake + dbt

Bronze / Silver / Gold data product built on `SNOWFLAKE_SAMPLE_DATA.TPCH_SF1`.
The Gold layer answers one question for **Key Account Managers: which accounts are at risk
of being lost, why, and how much revenue is at stake?**

```
TPCH_SF1 (8 tables) ─▶ BRONZE (brz_tpch__*) ─▶ SILVER (slv_*) ─▶ GOLD (account health) ─▶ KAM cockpit
```

| Layer | What it does |
|---|---|
| **Bronze** | Copies the 8 source tables as they are, plus a load timestamp. |
| **Silver** | Readable names, clean text, decoded codes, split composite codes, revenue and delivery rules. One model per table, independent of any use case. |
| **Gold** | `fct_account_health` (one row per account: activity, revenue trend, service, risk level), `fct_orders` (one row per order, for trends and drill-down), `dim_customer`, `dim_date`. |

## How the risk level is calculated

On the as-of date (last order date in the data), each account gets three signals:

| Signal | Rule |
|---|---|
| **Overdue** | No order for more than 2x the customer's usual time between orders |
| **Declining** | Revenue of the last 12 months is more than 30% below the previous 12 months |
| **Service issues** | Account is in the worst 25% by share of late order lines in the last 12 months |

Risk level: **Inactive** (no order in 12 months), **High** (2-3 signals), **Medium** (1), **Low** (0).
Thresholds are dbt variables in `dbt/dbt_project.yml`, so they can be tuned without touching SQL:
`dbt build --vars '{overdue_factor: 3}'`.

## Project structure

```
snowflake/            00_setup.sql: one-off setup (warehouse, database, role, dbt user)
dbt/                  the dbt project
  dbt_project.yml     project config + risk thresholds
  profiles.yml        Snowflake connection (no secrets inside)
  requirements.txt    dbt-core + dbt-snowflake
  models/bronze/      _sources.yml + 8 models (one line each, using the bronze_ingest macro)
  models/silver/      8 models + tests (_silver.yml)
  models/gold/        fct_account_health, fct_orders, dim_customer, dim_date + tests, unit test and exposure (_gold.yml)
  macros/             bronze_ingest, clean_string, map_values, date_key, generate_schema_name
  macros/tests/       custom generic tests: value_between, unique_combination
  tests/              2 reconciliation tests + 1 business alarm (each risk signal flags 1-60% of accounts)
powerbi/              Bonus: mockup + Power BI Project (PBIP) on the GOLD layer - see powerbi/README.md
docs/                 demo guide
.github/workflows/    ci.yml (build + test on every PR and on every merge)
```

## How to run it

1. **Create a key pair** inside the `dbt/` folder (Git Bash on Windows). First:
   ```bash
   cd dbt
   ```
   Then:
   ```bash
   openssl genrsa 2048 | openssl pkcs8 -topk8 -nocrypt -out rsa_key.p8
   ```
   And finally:
   ```bash
   openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
   ```
   The private key `rsa_key.p8` is git-ignored. Power BI uses the same file.
2. **Prepare Snowflake:**
   - Open a Snowsight worksheet and paste `snowflake/00_setup.sql`.
   - Put the contents of `dbt/rsa_key.pub`, without the BEGIN/END lines, in `rsa_public_key`.
   - Select everything (Ctrl+A) and run it (Ctrl+Enter).
3. **Run dbt** from the `dbt/` folder:
   ```bash
   pip install -r requirements.txt
   export SNOWFLAKE_ACCOUNT=<orgname-accountname>   # PowerShell: $env:SNOWFLAKE_ACCOUNT="..."
   dbt build                                        # builds and tests all three layers
   dbt docs generate --static                       # lineage graph: open target/static_index.html
   ```

The account identifier is shown in Snowsight under your user menu > *Connect a tool to Snowflake*.

## CI/CD

`.github/workflows/ci.yml` runs `dbt build` inside the `dbt/` folder:
- on each **pull request** with the `ci` target → schemas `CI_BRONZE`, `CI_SILVER`, `CI_GOLD`, so nothing reaches the real tables until every test passes;
- on each **merge to main** with the `prod` target → the real `BRONZE`, `SILVER`, `GOLD`.

GitHub secrets needed: `SNOWFLAKE_ACCOUNT` and `SNOWFLAKE_PRIVATE_KEY` (the full contents of `dbt/rsa_key.p8`, including the BEGIN/END lines).
