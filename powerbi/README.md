# Key Account Health Cockpit (Power BI Project)

A one-page Power BI dashboard on top of the GOLD schema, built in two AI-assisted steps:
**prompt → visual mockup → prompt → Power BI Project (PBIP)**.

```
powerbi/
  mockup.html                     step 1: visual mockup (open it in a browser)
  KAM_Health.pbip                 step 2: open this file in Power BI Desktop
  KAM_Health.SemanticModel/       data model in TMDL (tables, measures, relationships, Snowflake queries)
  KAM_Health.Report/              report in PBIR (one JSON file per page and per visual)
  tools/build_pbip.py             generator that writes the two folders above
  tools/validate_pbip.py          checks every JSON file against Microsoft's published schemas
  tools/flags.py                  draws the three flag images
```

## Step 1 - mockup

Prompt given to Claude:

> Design a one-page Power BI dashboard (1280 x 720) for Key Account Managers on top of
> `GOLD.FCT_ACCOUNT_HEALTH`, `FCT_ORDERS`, `DIM_CUSTOMER` and `DIM_DATE`. It must answer:
> which accounts are at risk, why, and how much revenue is at stake. Return a static HTML mockup
> with illustrative numbers where every block has an absolute position in pixels.

Result: [`mockup.html`](mockup.html). From top to bottom:
- title;
- 4 slicers: tier, risk level, segment and region;
- 4 KPI cards: active accounts, high-risk accounts, revenue at risk and % of revenue at risk;
- 3 charts: accounts by tier and risk level, revenue at risk by region, and monthly revenue;
- the worklist table, ordered by revenue at risk.

## Step 2 - Power BI Project generated from the mockup

Prompt given to Claude:

> Using `mockup.html` as the layout (same x, y, width and height for every block), generate a
> Power BI Project: a TMDL semantic model that imports the four GOLD tables from Snowflake, with
> friendly names, measures and relationships, and a PBIR report with one visual per mockup block.
> Validate every JSON file against Microsoft's published schemas.

What was generated:
- **Model:**
  - Tables: `Account Health`, `Customer`, `Orders` and `Date`.
  - Measures: Accounts, Active accounts, High-risk accounts, Total revenue at risk, % of revenue at risk, Revenue and Late orders %.
  - Relationship between `Account Health` and `Customer` in both directions. This way a risk or tier slicer also filters the orders behind the monthly revenue line.
- **Report:** 15 visuals placed at the mockup's coordinates. Clicking an account in the worklist shows that account's monthly revenue in the line chart.
- **Theme colours:** Propelling Tech brand colours, taken from careers.propellingtech.com:
  - slate `#2D3540`, turquoise `#6BD9DE` and teal `#176366`;
  - risk levels: red (High), amber (Medium), teal (Low) and grey (Inactive).
- **Languages (English, Spanish, Catalan):**
  - Each language has its own page.
  - The three flags at the top right switch between pages: Ctrl+click in Desktop, a normal click in the service.
  - Data values (risk level, segment, region, Yes/No) are translated with DAX calculated columns in the `Translations` folder.

**Validation done:**
- Every JSON file was checked against Microsoft's published schemas.
- The TMDL model was loaded with Microsoft's Analysis Services library (AMO).

The report has not been opened in Power BI Desktop yet.

## How to open it

1. Build the dbt project first so that `TPCH_MEDALLION.GOLD` exists.
2. Open `KAM_Health.pbip` in Power BI Desktop. Use a short folder path: Windows has a 260-character path limit.
3. Go to **Transform data → Edit parameters** and set `SnowflakeServer` to `<your-account>.snowflakecomputing.com`.
4. When asked for credentials, choose **Key-pair**: user `DBT_USER` and the file `dbt/rsa_key.p8`.
5. Click **Refresh**.
