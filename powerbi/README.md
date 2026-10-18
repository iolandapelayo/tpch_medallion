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

Result: [`mockup.html`](mockup.html). The mockup was later restyled together with the report, following two reference dashboards. It now shows:
- **tier A only:** a report-level filter (`tierAOnly`, locked) keeps only the key accounts, on all three pages.
  Tiers are computed in dbt against the whole portfolio, so the Gold layer keeps every account.
- a white header band with the title, the portfolio (Furniture key accounts - tier A - in the United Kingdom), 1 filter pill (risk) and the language flags;
- 3 KPI cards on the left (active accounts, high-risk accounts and revenue at risk). Each card has a sparkline and a comparison line;
- in the centre: key accounts by risk level, and revenue at risk by risk level;
- on the right: monthly revenue by risk level for the last 12 complete months (Aug 1997 - Jul 1998; August 1998 has only 2 days of orders, so it is left out), and a compact worklist with a "Why" column;
- a "how to read it" card at the bottom.

## Step 2 - Power BI Project generated from the mockup

Prompt given to Claude:

> Using `mockup.html` as the layout (same x, y, width and height for every block), generate a
> Power BI Project: a TMDL semantic model that imports the four GOLD tables from Snowflake, with
> friendly names, measures and relationships, and a PBIR report with one visual per mockup block.
> Validate every JSON file against Microsoft's published schemas.

What was generated:
- **Model:**
  - Tables: `Account Health`, `Customer`, `Orders` and `Date`. Gold holds one KAM's portfolio (Furniture, United Kingdom: 801 accounts), so there are no segment or country filters.
  - Main measures: Accounts, Active accounts, High-risk accounts, Total revenue at risk, % of revenue at risk and Revenue.
  - Helper measures for the cards: 12-month revenue change and sparkline revenue.
  - **Lean model:** only what the report uses. Power Query downloads only those columns (`Table.SelectColumns`); everything else (order dates, lifetime figures, late lines...) stays available in the Gold layer.
  - Relationship between `Account Health` and `Customer` in both directions. This way the tier A report filter and the risk slicer also filter the orders behind the monthly revenue line.
- **Report:** visuals placed at the mockup's coordinates. Clicking an account in the worklist shows that account's monthly revenue in the line chart.
- **Look:** the colours and fonts of careers.propellingtech.com, taken from the site's own colour variables. Fonts are Inter and Roboto, with Segoe UI as fallback.
  - White page. White cards with large rounded corners and the site's light grey border (`#EDEBEB`).
  - Title in bold, in the site's dark grey (`#2D3540`, the colour of its dark bands).
- **Chart colours:** shades of the site's turquoise (its buttons and logo, `#6BD9DE`). Risk is ordinal, so the darker the colour, the higher the risk:
  - High `#176366`;
  - Medium `#6BD9DE`;
  - Low `#AAE9EC`;
  - Inactive `#DDF5F6`.
- **Currency:** amounts are shown in pounds sterling (`£#,0`, e.g. £31M), the currency of the portfolio's country (United Kingdom). The TPC-H specification gives no currency, so only the symbol is set: the numbers are not converted.
- **Worklist order:** High risk first, then by revenue at risk.
  - Sorting only by revenue put medium-risk accounts on top: high-risk ones have already lost about 61% of their revenue, so less of it is left "at risk".
  - Calling the high-risk ones first is what the "how to read it" card recommends.
- **Decluttering:**
  - Legends are kept only where the title and the axis do not say what each colour is.
  - Data labels are shown only on the revenue-at-risk chart, which has no value axis.
  - The monthly line starts its Y axis at zero, so that changes are not exaggerated.
- **Languages (English, Spanish, Catalan):**
  - Each language has its own page.
  - The three flags at the top right switch between pages: Ctrl+click in Desktop, a normal click in the service.
  - Data values (risk level and the "Why" signals) are translated with DAX calculated columns in the `Translations` folder.

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
