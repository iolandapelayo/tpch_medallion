"""Generates the trilingual (EN / ES / CA) Key Account Health Cockpit PBIP, with Propelling Tech colours."""
import json
import shutil
import sys
import uuid
from pathlib import Path

OUT = Path(sys.argv[1])
BASE_THEME = Path(sys.argv[2])
FLAGS = Path(sys.argv[3])
SERVER = "rqimbac-jl36167.snowflakecomputing.com"
NAME = "KAM_Health"
SM = OUT / f"{NAME}.SemanticModel"
RP = OUT / f"{NAME}.Report"
S = "https://developer.microsoft.com/json-schemas/fabric"

# Propelling Tech brand (careers.propellingtech.com)
SLATE, TURQUOISE, TEAL, TURQ_LIGHT = "#2D3540", "#6BD9DE", "#176366", "#AAE9EC"
TEXT, GREY, BG = "#292626", "#AAA4A4", "#EDEBEB"
# Chart palette (decluttering rule: everything grey except what we want to highlight).
# Blues match the turquoise of the Propelling logo (#6BD9DE); the greys are blue-tinted to stay in the family.
NAVY, BLUE, BLUE_PALE = "#0E3A5B", "#2B7BB9", "#C9D6DF"
# High risk is the message, so it is the only coloured level; the rest go from dark to light grey (still ordinal)
RISK_HIGH, RISK_MEDIUM, RISK_LOW, RISK_INACTIVE = NAVY, "#8FA3B3", "#B8C6D1", "#DDE5EB"
BAR_GREY = BLUE_PALE   # non-highlighted bars
# the site uses Inter for text and Roboto for big headings; Segoe UI is the fallback where they are not installed
FONT_TEXT = "Inter, 'Segoe UI', sans-serif"
FONT_HEAD = "Roboto, 'Segoe UI Semibold', sans-serif"

if OUT.exists():
    shutil.rmtree(OUT)


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, (dict, list)):
        content = json.dumps(content, indent=2, ensure_ascii=False)
    path.write_text(content, encoding="utf-8", newline="\n")


# ============================================================================ translations
LANGS = ["en", "es", "ca"]
T = {
    "page": {"en": "Account health", "es": "Salud de cuentas", "ca": "Salut dels comptes"},
    "title": {"en": "Key Account Health Cockpit", "es": "Panel de salud de cuentas clave",
              "ca": "Quadre de salut dels comptes clau"},
    "subtitle": {
        "en": "Furniture accounts in the United Kingdom · which are cooling down, why, and how much revenue is at stake · as of 1998-08-02",
        "es": "Cuentas de mobiliario del Reino Unido · cuáles se enfrían, por qué y cuántos ingresos están en juego · a 1998-08-02",
        "ca": "Comptes de mobiliari del Regne Unit · quins es refreden, per què i quants ingressos hi ha en joc · a 1998-08-02"},
    "tier": {"en": "Account tier", "es": "Categoría de cuenta", "ca": "Categoria del compte"},
    "risk": {"en": "Risk level", "es": "Nivel de riesgo", "ca": "Nivell de risc"},
    "segment": {"en": "Market segment", "es": "Segmento", "ca": "Segment"},
    "region": {"en": "Region", "es": "Región", "ca": "Regió"},
    "nation": {"en": "Country", "es": "País", "ca": "País"},
    "active": {"en": "Active accounts", "es": "Cuentas activas", "ca": "Comptes actius"},
    "highrisk": {"en": "High-risk accounts", "es": "Cuentas en riesgo alto", "ca": "Comptes en risc alt"},
    "atrisk": {"en": "Revenue at risk", "es": "Ingresos en riesgo", "ca": "Ingressos en risc"},
    "pctrisk": {"en": "% of revenue at risk", "es": "% de ingresos en riesgo", "ca": "% d'ingressos en risc"},
    "accounts": {"en": "Accounts", "es": "Cuentas", "ca": "Comptes"},
    "revenue": {"en": "Revenue", "es": "Ingresos", "ca": "Ingressos"},
    "month": {"en": "Month", "es": "Mes", "ca": "Mes"},
    "c_tierrisk": {"en": "Accounts by tier and risk level", "es": "Cuentas por categoría y nivel de riesgo",
                   "ca": "Comptes per categoria i nivell de risc"},
    "c_tier_rev": {"en": "Revenue at risk by tier", "es": "Ingresos en riesgo por categoría",
                   "ca": "Ingressos en risc per categoria"},
    "c_trend": {"en": "Monthly revenue (click an account in the table to see its history)",
                "es": "Ingresos mensuales (haz clic en una cuenta de la tabla para ver su historia)",
                "ca": "Ingressos mensuals (fes clic en un compte de la taula per veure'n l'historial)"},
    "c_table": {"en": "Worklist for this week - accounts ordered by revenue at risk",
                "es": "Lista de la semana - cuentas ordenadas por ingresos en riesgo",
                "ca": "Llista de la setmana - comptes ordenats per ingressos en risc"},
    "customer": {"en": "Customer", "es": "Cliente", "ca": "Client"},
    "tier_short": {"en": "Tier", "es": "Categoría", "ca": "Categoria"},
    "change": {"en": "Revenue change %", "es": "Variación ingresos %", "ca": "Variació ingressos %"},
    "days_since": {"en": "Days since last order", "es": "Días sin pedir", "ca": "Dies sense comanda"},
    "usual_days": {"en": "Usual days between orders", "es": "Días habituales entre pedidos",
                   "ca": "Dies habituals entre comandes"},
    "overdue": {"en": "Overdue", "es": "Retrasada", "ca": "Endarrerit"},
    "declining": {"en": "Declining", "es": "En caída", "ca": "En caiguda"},
    "service": {"en": "Service issues", "es": "Problemas de servicio", "ca": "Problemes de servei"},
    "flag_tip": {"en": "English", "es": "Español", "ca": "Català"},
    "why": {"en": "Why", "es": "Por qué", "ca": "Per què"},
    "chg_12m": {"en": "12m revenue vs previous 12m", "es": "Ingresos 12m vs 12m anteriores",
                "ca": "Ingressos 12m vs 12m anteriors"},
    "of_revenue": {"en": "of last-12-month revenue", "es": "de los ingresos de 12 meses",
                   "ca": "dels ingressos de 12 mesos"},
    "c_trend_risk": {"en": "Monthly revenue by risk level, 1998", "es": "Ingresos mensuales por nivel de riesgo, 1998",
                     "ca": "Ingressos mensuals per nivell de risc, 1998"},
    "s_trend_risk": {"en": "Data until 2 Aug 1998 · click an account to see its months",
                     "es": "Datos hasta el 2 ago 1998 · clic en una cuenta para ver sus meses",
                     "ca": "Dades fins al 2 ago 1998 · clic en un compte per veure'n els mesos"},
    "c_worklist": {"en": "Worklist for this week", "es": "Lista de la semana", "ca": "Llista de la setmana"},
    "s_worklist": {"en": "Ordered by revenue at risk", "es": "Ordenada por ingresos en riesgo",
                   "ca": "Ordenada per ingressos en risc"},
    "s_tierrisk": {"en": "High risk highlighted; other levels in grey", "es": "Riesgo alto resaltado; el resto, en gris",
                   "ca": "Risc alt destacat; la resta, en gris"},
    "s_tier_rev": {"en": "The tier with the most revenue at risk is highlighted",
                   "es": "La categoría con más ingresos en riesgo, resaltada",
                   "ca": "La categoria amb més ingressos en risc, destacada"},
    # short labels for the filter pills, so they are never cut with "..."
    "f_tier": {"en": "Tier", "es": "Categoría", "ca": "Categoria"},
    "f_risk": {"en": "Risk", "es": "Riesgo", "ca": "Risc"},
    "f_segment": {"en": "Segment", "es": "Segmento", "ca": "Segment"},
    "f_region": {"en": "Region", "es": "Región", "ca": "Regió"},
    "f_nation": {"en": "Country", "es": "País", "ca": "País"},
    "change_short": {"en": "Change 12m", "es": "Variación 12m", "ca": "Variació 12m"},
    "story": {
        "en": "How to read it: every account gets three warning signals - overdue (much later than its usual ordering "
              "rhythm), declining (12-month revenue down more than 30%) and service issues (worst 25% for late "
              "deliveries). Two or more signals = High risk. Start with Tier A accounts in navy: they hold most of "
              "the revenue at stake.",
        "es": "Cómo leerlo: cada cuenta tiene tres señales de alarma - retraso (pide mucho más tarde de lo habitual), "
              "caída (los ingresos de 12 meses bajan más de un 30 %) y problemas de servicio (peor 25 % en entregas "
              "tardías). Dos o más señales = riesgo alto. Empieza por las cuentas de categoría A en azul marino: concentran "
              "la mayor parte de los ingresos en juego.",
        "ca": "Com llegir-ho: cada compte té tres senyals d'alarma - retard (demana molt més tard del que és "
              "habitual), caiguda (els ingressos de 12 mesos baixen més d'un 30 %) i problemes de servei (pitjor 25 % "
              "en lliuraments tardans). Dos o més senyals = risc alt. Comença pels comptes de categoria A en blau marí: "
              "concentren la major part dels ingressos en joc."},
}
# short words for the "Why" column (one word each, joined with " · ")
SIGNAL_WORDS = {"en": ("Overdue", "Declining", "Service"), "es": ("Retraso", "Caída", "Servicio"),
                "ca": ("Retard", "Caiguda", "Servei")}
VALUES = {  # data values translated with DAX calculated columns
    "risk": {"High": ("Alto", "Alt"), "Medium": ("Medio", "Mitjà"), "Low": ("Bajo", "Baix"),
             "Inactive": ("Inactivo", "Inactiu")},
    "segment": {"Automobile": ("Automoción", "Automoció"), "Building": ("Construcción", "Construcció"),
                "Furniture": ("Mobiliario", "Mobiliari"), "Household": ("Hogar", "Llar"),
                "Machinery": ("Maquinaria", "Maquinària")},
    "region": {"Africa": ("África", "Àfrica"), "America": ("América", "Amèrica"), "Asia": ("Asia", "Àsia"),
               "Europe": ("Europa", "Europa"), "Middle East": ("Oriente Medio", "Orient Mitjà")},
    # the five European nations of TPC-H (the portfolio is Furniture in Europe)
    "nation": {"France": ("Francia", "França"), "Germany": ("Alemania", "Alemanya"), "Romania": ("Rumanía", "Romania"),
               "Russia": ("Rusia", "Rússia"), "United Kingdom": ("Reino Unido", "Regne Unit")},
}
YES_NO = {"en": ("Yes", "No"), "es": ("Sí", "No"), "ca": ("Sí", "No")}

# ============================================================================ project
write(OUT / f"{NAME}.pbip", {
    "$schema": f"{S}/pbip/pbipProperties/1.0.0/schema.json",
    "version": "1.0",
    "artifacts": [{"report": {"path": f"{NAME}.Report"}}],
    "settings": {"enableAutoRecovery": True},
})

# ============================================================================ semantic model (TMDL)
write(SM / "definition.pbism", {"$schema": f"{S}/item/semanticModel/definitionProperties/1.0.0/schema.json",
                                "version": "4.1", "settings": {}})


def q(name):
    return name if name.replace("_", "").isalnum() and name != "Date" else f"'{name}'"


def switch(ref, mapping, idx):
    pairs = ", ".join(f'"{k}", "{v[idx]}"' for k, v in mapping.items())
    return f"SWITCH({ref}, {pairs}, {ref})"


# (column, SOURCE_COLUMN, dataType, formatString, hidden, extra properties)
# extra "description" becomes a /// line; int64 columns are also typed in Power Query,
# because Snowflake NUMBER arrives as decimal and Desktop would turn them back into double.
AH_COLS = [
    ("Customer key", "CUSTOMER_KEY", "int64", "0", True, {}),
    ("As of date", "AS_OF_DATE", "dateTime", "yyyy-mm-dd", False,
     {"description": "Reference date of the analysis: the last order in the data (1998-08-02)."}),
    ("Account tier", "ACCOUNT_TIER", "string", None, False,
     {"description": "A = top 20% of accounts by lifetime revenue, B = next 30%, C = rest."}),
    ("First order date", "FIRST_ORDER_DATE", "dateTime", "yyyy-mm-dd", False, {}),
    ("Last order date", "LAST_ORDER_DATE", "dateTime", "yyyy-mm-dd", False, {}),
    ("Days since last order", "DAYS_SINCE_LAST_ORDER", "int64", "#,0", False,
     {"description": "Days between the customer's last order and the as-of date."}),
    ("Usual days between orders", "AVG_DAYS_BETWEEN_ORDERS", "double", "#,0", False,
     {"description": "Average number of days between the customer's orders."}),
    ("Lifetime orders", "LIFETIME_ORDERS", "int64", "#,0", False, {}),
    ("Lifetime revenue", "LIFETIME_REVENUE", "double", "#,0", False, {}),
    ("Orders last 12m", "ORDERS_LAST_12M", "int64", "#,0", False, {}),
    ("Revenue last 12m", "REVENUE_LAST_12M", "double", "#,0", False, {}),
    ("Revenue prev 12m", "REVENUE_PREV_12M", "double", "#,0", False, {}),
    ("Revenue change %", "REVENUE_CHANGE_PCT", "double", "0.0%", False,
     {"description": "Revenue of the last 12 months vs the previous 12 months."}),
    ("Late line rate 12m", "LATE_LINE_RATE_12M", "double", "0.0%", False,
     {"description": "Share of the account's order lines received late in the last 12 months."}),
    ("Overdue", "IS_OVERDUE", "boolean", None, False,
     {"description": "No order for more than 2x the customer's usual time between orders."}),
    ("Declining", "IS_DECLINING", "boolean", None, False,
     {"description": "Last-12-month revenue fell more than 30%."}),
    ("Service issues", "HAS_SERVICE_ISSUES", "boolean", None, False,
     {"description": "In the worst 25% of accounts by late line rate."}),
    ("Risk signals", "RISK_SIGNALS", "int64", "0", False,
     {"description": "How many of the three signals (overdue, declining, service issues) are on."}),
    ("Risk level", "RISK_LEVEL", "string", None, False,
     {"sortByColumn": "'Risk order'",
      "description": "Inactive (no order in 12 months), High (2-3 signals), Medium (1), Low (0)."}),
    ("Risk order", "RISK_ORDER", "int64", "0", True, {}),
    ("Revenue at risk", "REVENUE_AT_RISK", "double", "#,0", False,
     {"description": "Last-12-month revenue of active accounts with at least one risk signal."}),
]
RL = "'Account Health'[Risk level]"
AH_CALC = [  # (name, DAX, extra properties)
    ("Risk level ES", switch(RL, VALUES["risk"], 0), {"sortByColumn": "'Risk order'"}),
    ("Risk level CA", switch(RL, VALUES["risk"], 1), {"sortByColumn": "'Risk order'"}),
]
for col in ["Overdue", "Declining", "Service issues"]:
    for lang in LANGS:
        yes, no = YES_NO[lang]
        AH_CALC.append((f"{col} {lang.upper()}", f"IF('Account Health'[{col}], \"{yes}\", \"{no}\")", {}))
for lang in LANGS:  # e.g. "Overdue · Declining" for the worklist
    o, d, s = SIGNAL_WORDS[lang]
    AH_CALC.append((f"Signals {lang.upper()}",
                    f"SUBSTITUTE(TRIM(IF('Account Health'[Overdue], \"{o}\") & \" \" & "
                    f"IF('Account Health'[Declining], \"{d}\") & \" \" & "
                    f"IF('Account Health'[Service issues], \"{s}\")), \" \", \" · \")", {}))

CU_CALC = []
for key, col in [("segment", "Market segment"), ("region", "Region"), ("nation", "Nation")]:
    for idx, lang in enumerate(["ES", "CA"]):
        CU_CALC.append((f"{col} {lang}", switch(f"Customer[{col}]", VALUES[key], idx), {}))

# Risk order is added in Power Query (not DAX) to avoid a circular dependency with sortByColumn
AH_EXTRA_STEP = ('WithOrder = Table.AddColumn(Typed, "RISK_ORDER", each if [RISK_LEVEL] = "High" then 1 '
                 'else if [RISK_LEVEL] = "Medium" then 2 else if [RISK_LEVEL] = "Low" then 3 else 4, Int64.Type)')

CHANGE_FMT = "▲ +0.0%;▼ -0.0%;0.0%"
TABLES = [
    ("Account Health", "FCT_ACCOUNT_HEALTH", AH_COLS, AH_CALC, [  # (name, DAX, format, description)
        ("Accounts", "COUNTROWS('Account Health')", "#,0",
         "Number of accounts (customers with at least one order)."),
        ("Active accounts", "CALCULATE([Accounts], 'Account Health'[Risk level] <> \"Inactive\")", "#,0",
         "Accounts with at least one order in the last 12 months."),
        ("High-risk accounts", "CALCULATE([Accounts], 'Account Health'[Risk level] = \"High\")", "#,0",
         "Active accounts with 2 or 3 risk signals."),
        ("Revenue last 12m total", "SUM('Account Health'[Revenue last 12m])", "#,0",
         "Last-12-month revenue of the accounts."),
        ("Total revenue at risk", "SUM('Account Health'[Revenue at risk])", "#,0",
         "Last-12-month revenue of active accounts with at least one risk signal."),
        ("% of revenue at risk", "DIVIDE([Total revenue at risk], [Revenue last 12m total])", "0.0%",
         "Share of last-12-month revenue that comes from accounts at risk."),
        ("Revenue prev 12m total", "SUM('Account Health'[Revenue prev 12m])", "#,0",
         "Revenue of the 12 months before the last 12 months."),
        ("Revenue change 12m", "DIVIDE([Revenue last 12m total] - [Revenue prev 12m total], [Revenue prev 12m total])",
         CHANGE_FMT, "Last-12-month revenue vs the previous 12 months."),
        ("Revenue change active", "CALCULATE([Revenue change 12m], 'Account Health'[Risk level] <> \"Inactive\")",
         CHANGE_FMT, "Revenue change 12m of the active accounts."),
        ("Revenue change high-risk", "CALCULATE([Revenue change 12m], 'Account Health'[Risk level] = \"High\")",
         CHANGE_FMT, "Revenue change 12m of the high-risk accounts."),
        # bar colour: the tier with the most revenue at risk in blue, the rest in pale blue
        ("Tier bar color", "VAR MaxRevenueAtRisk = MAXX(ALLSELECTED('Account Health'[Account tier]), "
         "[Total revenue at risk]) RETURN IF([Total revenue at risk] = MaxRevenueAtRisk, \"" + BLUE + "\", \"" + BAR_GREY + "\")",
         None, "Highlights the tier with the most revenue at risk."),
    ], AH_EXTRA_STEP),
    ("Customer", "DIM_CUSTOMER", [
        ("Customer key", "CUSTOMER_KEY", "int64", "0", True, {}),
        ("Customer", "CUSTOMER_NAME", "string", None, False, {}),
        ("Market segment", "MARKET_SEGMENT", "string", None, False, {}),
        ("Nation", "CUSTOMER_NATION", "string", None, False, {}),
        ("Region", "CUSTOMER_REGION", "string", None, False, {}),
        ("Account balance", "ACCOUNT_BALANCE", "double", "#,0.00", False, {}),
    ], CU_CALC, [], None),
    ("Orders", "FCT_ORDERS", [
        ("Order id", "ORDER_ID", "int64", "0", False, {}),
        ("Customer key", "CUSTOMER_KEY", "int64", "0", True, {}),
        ("Order date key", "ORDER_DATE_KEY", "int64", "0", True, {}),
        ("Order date", "ORDER_DATE", "dateTime", "yyyy-mm-dd", False, {}),
        ("Order status", "ORDER_STATUS", "string", None, False, {}),
        ("Order priority", "ORDER_PRIORITY", "string", None, False, {}),
        ("Order lines", "ORDER_LINES", "int64", "#,0", False,
         {"description": "Number of lines (products) in the order."}),
        ("Net revenue", "NET_REVENUE", "double", "#,0", True, {}),
        ("Delivered date", "DELIVERED_DATE", "dateTime", "yyyy-mm-dd", False,
         {"description": "Date the last line of the order was received."}),
        ("Late lines", "LATE_LINES", "int64", "#,0", False,
         {"description": "Lines received after the date committed to the customer."}),
        ("Is late", "IS_LATE", "boolean", None, False,
         {"description": "At least one line arrived after the committed date."}),
    ], [], [
        ("Revenue", "SUM(Orders[Net revenue])", "#,0", "Net revenue of the orders (after discount)."),
        # lines, not orders: almost every TPC-H order has some late line, so an order-level rate is ~100%
        ("Late line rate", "DIVIDE(SUM(Orders[Late lines]), SUM(Orders[Order lines]))", "0.0%",
         "Share of order lines received after the date committed to the customer. "
         "Counts lines, not orders: almost every TPC-H order has some late line."),
        # sparklines of the KPI cards: filters on Account Health reach Orders through Customer (both directions)
        ("Revenue active accounts", "CALCULATE([Revenue], 'Account Health'[Risk level] <> \"Inactive\")", "#,0",
         "Monthly revenue of the accounts that are active today."),
        ("Revenue high-risk accounts", "CALCULATE([Revenue], 'Account Health'[Risk level] = \"High\")", "#,0",
         "Monthly revenue of the accounts that are high risk today."),
        ("Revenue accounts at risk", "CALCULATE([Revenue], 'Account Health'[Risk level] IN {\"High\", \"Medium\"})",
         "#,0", "Monthly revenue of the active accounts with at least one risk signal today."),
    ], None),
    ("Date", "DIM_DATE", [
        ("Date key", "DATE_KEY", "int64", "0", True, {}),
        ("Date", "FULL_DATE", "dateTime", "yyyy-mm-dd", False, {"isKey": None}),
        ("Year", "YEAR", "int64", "0", False, {}),
        ("Quarter", "QUARTER", "int64", "0", False, {}),
        ("Month", "MONTH", "int64", "0", False, {}),
        ("Month name", "MONTH_NAME", "string", None, False, {}),
        ("Year month", "YEAR_MONTH", "string", None, False, {}),
        ("Day name", "DAY_NAME", "string", None, False, {}),
        ("Month start", "MONTH_START", "dateTime", "mmm yyyy", False,
         {"description": "First day of the month: a real date, so charts get a continuous axis with whole labels."}),
    ], [], [], 'WithMonth = Table.AddColumn(Typed, "MONTH_START", each Date.StartOfMonth(Date.From([FULL_DATE])), type date)'),
]


def table_tmdl(name, source, columns, calc_columns, measures, extra_step):
    lines = [f"table {q(name)}"]
    if name == "Date":
        lines.append("\tdataCategory: Time")  # marked as the model's date table
    lines.append("")
    for m_name, dax, fmt, desc in measures:
        lines += [f"\t/// {desc}", f"\tmeasure {q(m_name)} = {dax}"]
        lines += [f"\t\tformatString: {fmt}", ""] if fmt else [""]
    for c_name, src, dtype, fmt, hidden, extra in columns:
        extra = dict(extra)
        if "description" in extra:
            lines.append(f"\t/// {extra.pop('description')}")
        lines += [f"\tcolumn {q(c_name)}", f"\t\tdataType: {dtype}"]
        if fmt:
            lines.append(f"\t\tformatString: {fmt}")
        if hidden:
            lines.append("\t\tisHidden")
        lines.append("\t\tsummarizeBy: none")
        lines.append(f"\t\tsourceColumn: {src}")
        for k, v in extra.items():
            lines.append(f"\t\t{k}" if v is None else f"\t\t{k}: {v}")
        lines += ["", "\t\tannotation SummarizationSetBy = User", ""]
    for c_name, dax, extra in calc_columns:
        lines += [f"\tcolumn {q(c_name)} = {dax}", "\t\tdataType: string", "\t\tsummarizeBy: none",
                  "\t\tdisplayFolder: Translations"]
        for k, v in extra.items():
            lines.append(f"\t\t{k}: {v}")
        lines += ["", "\t\tannotation SummarizationSetBy = User", ""]
    result = extra_step.split(" = ")[0] if extra_step else "Typed"
    whole = ", ".join(f'{{"{src}", Int64.Type}}' for _, src, dtype, *_ in columns
                      if dtype == "int64" and src != "RISK_ORDER")
    lines += [
        f"\tpartition {q(name)} = m",
        "\t\tmode: import",
        "\t\tsource =",
        "\t\t\t\tlet",
        '\t\t\t\t    Source = Snowflake.Databases(SnowflakeServer, "TPCH_WH", [Role = "TRANSFORMER"]),',
        '\t\t\t\t    Database = Source{[Name = "TPCH_MEDALLION", Kind = "Database"]}[Data],',
        '\t\t\t\t    Gold = Database{[Name = "GOLD", Kind = "Schema"]}[Data],',
        f'\t\t\t\t    Data = Gold{{[Name = "{source}", Kind = "Table"]}}[Data],',
        f"\t\t\t\t    Typed = Table.TransformColumnTypes(Data, {{{whole}}})" + ("," if extra_step else ""),
    ]
    if extra_step:
        lines.append(f"\t\t\t\t    {extra_step}")
    lines += ["\t\t\t\tin", f"\t\t\t\t    {result}", ""]
    return "\n".join(lines)


D = SM / "definition"
write(D / "database.tmdl", "database\n\tcompatibilityLevel: 1601\n")
write(D / "model.tmdl", "\n".join([
    "model Model", "\tculture: en-US", "\tdefaultPowerBIDataSourceVersion: powerBI_V3",
    "\tdiscourageImplicitMeasures", "\tsourceQueryCulture: en-US",
    "\tdataAccessOptions", "\t\tlegacyRedirects", "\t\treturnErrorValuesAsNull", "",
    'annotation PBI_QueryOrder = ["SnowflakeServer","Account Health","Customer","Orders","Date"]', "",
    # no auto date/time: the model already has the Date table from dbt
    "annotation __PBI_TimeIntelligenceEnabled = 0", "",
    *[f"ref table {q(t[0])}" for t in TABLES], "",
]))
write(D / "expressions.tmdl", "\n".join([
    "/// Snowflake account URL, e.g. abcdefg-xy12345.snowflakecomputing.com",
    f'expression SnowflakeServer = "{SERVER}" '
    'meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]',
    "", "\tannotation PBI_ResultType = Text", "",
]))
for t in TABLES:
    write(D / "tables" / f"{t[0]}.tmdl", table_tmdl(*t))


def rel(from_col, to_col, both=False):
    out = [f"relationship {uuid.uuid4()}"]
    if both:
        out.append("\tcrossFilteringBehavior: bothDirections")
    return "\n".join(out + [f"\tfromColumn: {from_col}", f"\ttoColumn: {to_col}", ""])


write(D / "relationships.tmdl", "\n".join([
    rel("'Account Health'.'Customer key'", "Customer.'Customer key'", both=True),
    rel("Orders.'Customer key'", "Customer.'Customer key'"),
    rel("Orders.'Order date key'", "'Date'.'Date key'"),
]))

# ============================================================================ report (PBIR)
write(RP / "definition.pbir", {"$schema": f"{S}/item/report/definitionProperties/2.0.0/schema.json",
                               "version": "4.0",
                               "datasetReference": {"byPath": {"path": f"../{NAME}.SemanticModel"}}})
R = RP / "definition"
write(R / "version.json", {"$schema": f"{S}/item/report/definition/versionMetadata/1.0.0/schema.json",
                           "version": "2.0.0"})
FLAG_FILES = {lang: f"flag_{lang}.png" for lang in LANGS}
write(R / "report.json", {
    "$schema": f"{S}/item/report/definition/report/1.3.0/schema.json",
    "themeCollection": {
        "baseTheme": {"name": "CY24SU10", "reportVersionAtImport": "5.61", "type": "SharedResources"},
        "customTheme": {"name": "KAMTheme.json", "reportVersionAtImport": "5.61", "type": "RegisteredResources"},
    },
    "layoutOptimization": "None",
    "resourcePackages": [
        {"name": "SharedResources", "type": "SharedResources",
         "items": [{"name": "CY24SU10", "path": "BaseThemes/CY24SU10.json", "type": "BaseTheme"}]},
        {"name": "RegisteredResources", "type": "RegisteredResources",
         "items": [{"name": "KAMTheme.json", "path": "KAMTheme.json", "type": "CustomTheme"}]
                  + [{"name": f, "path": f, "type": "Image"} for f in FLAG_FILES.values()]},
    ],
    "settings": {"useStylableVisualContainerHeader": True, "defaultDrillFilterOtherVisuals": True},
})
STATIC = RP / "StaticResources"
(STATIC / "SharedResources/BaseThemes").mkdir(parents=True)
shutil.copy(BASE_THEME, STATIC / "SharedResources/BaseThemes/CY24SU10.json")
for f in FLAG_FILES.values():
    (STATIC / "RegisteredResources").mkdir(parents=True, exist_ok=True)
    shutil.copy(FLAGS / f, STATIC / "RegisteredResources" / f)

# Look of the reference dashboard: dark header band, light grey rounded frame, white cards with big
# rounded corners and no shadow, one accent colour (turquoise) and grey for the rest.
FRAME, CARD_RADIUS = "#DEDADA", 22
# Risk levels are sorted High, Medium, Low, Inactive (via 'Risk order') -> navy, then three greys
write(STATIC / "RegisteredResources/KAMTheme.json", {
    "name": "Propelling KAM Health",
    "dataColors": [RISK_HIGH, RISK_MEDIUM, RISK_LOW, RISK_INACTIVE, "#1B5F8C", "#4FA9D6", TURQ_LIGHT, SLATE],
    "foreground": TEXT, "background": "#FFFFFF", "tableAccent": BLUE,
    "textClasses": {
        "callout": {"fontFace": FONT_HEAD, "fontSize": 26, "color": NAVY},
        "title": {"fontFace": FONT_HEAD, "fontSize": 12, "color": NAVY},
        "header": {"fontFace": FONT_HEAD, "fontSize": 10, "color": NAVY},
        "label": {"fontFace": FONT_TEXT, "fontSize": 9, "color": TEXT},
    },
    "visualStyles": {"*": {"*": {
        "background": [{"show": True, "color": {"solid": {"color": "#FFFFFF"}}, "transparency": 0}],
        # a border in the card's own colour makes the rounded corners visible in every Desktop version
        "border": [{"show": True, "color": {"solid": {"color": "#FFFFFF"}}, "radius": CARD_RADIUS}],
        "dropShadow": [{"show": False}],
        "padding": [{"top": 12, "bottom": 10, "left": 14, "right": 14}],
        "title": [{"fontFamily": FONT_HEAD, "fontSize": 12, "fontColor": {"solid": {"color": NAVY}}, "bold": True}],
        "subTitle": [{"fontFamily": FONT_TEXT, "fontSize": 8, "fontColor": {"solid": {"color": "#7A7575"}}}],
    }}},
})

write(R / "pages/pages.json", {"$schema": f"{S}/item/report/definition/pagesMetadata/1.0.0/schema.json",
                               "pageOrder": LANGS, "activePageName": "en"})


def lit(value):
    return {"expr": {"Literal": {"Value": value}}}


def text_lit(text):
    return lit("'" + text.replace("'", "''") + "'")


def color(hex_):
    return {"solid": {"color": lit(f"'{hex_}'")}}


def resource(item):
    return {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1,
                                             "ItemName": item}}}


def field(kind, entity, prop):
    return {kind: {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def proj(kind, entity, prop, display=None):
    p = {"field": field(kind, entity, prop), "queryRef": f"{entity}.{prop}", "nativeQueryRef": prop}
    if display:
        p["displayName"] = display
    return p


def col(entity, prop, display=None):
    return proj("Column", entity, prop, display)


def meas(entity, prop, display=None):
    return proj("Measure", entity, prop, display)


def title(text, subtitle=None):
    out = {"title": [{"properties": {"show": lit("true"), "text": text_lit(text)}}]}
    if subtitle:
        out["subTitle"] = [{"properties": {"show": lit("true"), "text": text_lit(subtitle)}}]
    return out


def box(hex_, radius=CARD_RADIUS):
    """A plain coloured, rounded rectangle (frame, header band)."""
    return {"background": [{"properties": {"show": lit("true"), "color": color(hex_), "transparency": lit("0D")}}],
            "border": [{"properties": {"show": lit("true"), "color": color(hex_), "radius": lit(f"{radius}D")}}]}


# for visuals drawn on top of a card: no background, border, title or padding of their own
BARE = {"background": [{"properties": {"show": lit("false")}}],
        "border": [{"properties": {"show": lit("false")}}],
        "title": [{"properties": {"show": lit("false")}}],
        "padding": [{"properties": {"top": lit("0D"), "bottom": lit("0D"), "left": lit("0D"), "right": lit("0D")}}]}

# Month charts show only the last year of the data. Orders end on 1998-08-02, so the lines stop in August,
# but the continuous axis still spans January to December.
LAST_YEAR = 1998
MONTH_AXIS = {"categoryAxis": [{"properties": {
    "axisType": lit("'Continuous'"), "showAxisTitle": lit("false"),
    "start": lit(f"datetime'{LAST_YEAR}-01-01T00:00:00'"), "end": lit(f"datetime'{LAST_YEAR}-12-01T00:00:00'")}}]}
YEAR_FILTER = {"filters": [{
    "name": "lastYear",
    "field": {"Column": {"Expression": {"SourceRef": {"Entity": "Date"}}, "Property": "Year"}},
    "type": "Categorical",
    "filter": {"Version": 2, "From": [{"Name": "d", "Entity": "Date", "Type": 0}],
               "Where": [{"Condition": {"In": {
                   "Expressions": [{"Column": {"Expression": {"SourceRef": {"Source": "d"}}, "Property": "Year"}}],
                   "Values": [[{"Literal": {"Value": f"{LAST_YEAR}L"}}]]}}}]},
}]}


def run(text, size, color_=TEXT, bold=False, font=FONT_TEXT):
    style = {"fontFamily": font, "fontSize": f"{size}pt", "color": color_}
    if bold:
        style["fontWeight"] = "bold"
    return {"value": text, "textStyle": style}


def build_page(lang):
    t = {k: v[lang] for k, v in T.items()}
    suffix = "" if lang == "en" else f" {lang.upper()}"
    page_dir = R / "pages" / lang
    page = {
        "$schema": f"{S}/item/report/definition/page/1.4.0/schema.json",
        "name": lang, "displayName": t["page"], "displayOption": "FitToPage", "height": 720, "width": 1280,
        "objects": {"background": [{"properties": {"color": color("#FFFFFF"), "transparency": lit("0D")}}]},
    }
    if lang != "en":
        page["visibility"] = "HiddenInViewMode"   # the flags are the language switch
    write(page_dir / "page.json", page)

    z = [0]

    def visual(name, x, y, w, h, visual_type, query=None, objects=None, container=None, sort=None, filters=None):
        z[0] += 1000
        v = {"visualType": visual_type}
        if query is not None:
            v["query"] = {"queryState": query}
            if sort:
                v["query"]["sortDefinition"] = {"sort": [sort], "isDefaultSort": False}
        if objects:
            v["objects"] = objects
        if container:
            v["visualContainerObjects"] = container
        v["drillFilterOtherVisuals"] = True
        container_json = {
            "$schema": f"{S}/item/report/definition/visualContainer/2.0.0/schema.json",
            "name": name,
            "position": {"x": x, "y": y, "z": z[0], "width": w, "height": h, "tabOrder": z[0]},
            "visual": v,
        }
        if filters:
            container_json["filterConfig"] = filters
        write(page_dir / "visuals" / name / "visual.json", container_json)

    def textbox(name, x, y, w, h, paragraphs, container=None):
        visual(name, x, y, w, h, "textbox",
               objects={"general": [{"properties": {"paragraphs": paragraphs}}]}, container=container)

    # ---- frame and white header band (drawn first, so they sit behind everything)
    textbox("frame", 8, 8, 1264, 704, [{"textRuns": [run(" ", 8)]}], container=box(FRAME, 28))
    textbox("title", 8, 8, 1264, 86, [
        {"textRuns": [run(t["title"], 20, NAVY, bold=True, font=FONT_HEAD)]},
        {"textRuns": [run(t["subtitle"], 10, BLUE)]},
    ], container={**box("#FFFFFF", 28),
                  "padding": [{"properties": {"top": lit("16D"), "left": lit("26D"), "right": lit("500D")}}]})

    # filters as pills with a pale blue outline inside the band (short labels: never cut with "...")
    # segment and country have a single value in the portfolio (Furniture, United Kingdom): only tier and risk
    slicers = [("Account Health", "Account tier", t["f_tier"]), ("Account Health", f"Risk level{suffix}", t["f_risk"])]
    slicer_x, slicer_w = [896, 1008], [104, 104]   # right-aligned next to the flags
    for i, (entity, prop, label) in enumerate(slicers):
        visual(f"slicer{i + 1}", slicer_x[i], 24, slicer_w[i], 54, "slicer",
               query={"Values": {"projections": [col(entity, prop, label)]}},
               objects={"data": [{"properties": {"mode": lit("'Dropdown'")}}],
                        "header": [{"properties": {"fontFamily": text_lit(FONT_TEXT), "fontSize": lit("8D"),
                                                   "fontColor": color(BLUE), "bold": lit("true")}}],
                        "items": [{"properties": {"fontFamily": text_lit(FONT_TEXT), "fontSize": lit("9D")}}]},
               container={"border": [{"properties": {"show": lit("true"), "color": color(BLUE_PALE),
                                                     "radius": lit("10D")}}],
                          "padding": [{"properties": {"top": lit("4D"), "bottom": lit("4D"),
                                                      "left": lit("8D"), "right": lit("8D")}}]})

    for i, flag_lang in enumerate(LANGS):
        active = flag_lang == lang
        visual(f"flag_{flag_lang}", 1158 + i * 36, 38, 30, 20, "image",
               objects={"general": [{"properties": {"imageUrl": resource(FLAG_FILES[flag_lang])}}],
                        "imageScaling": [{"properties": {"imageScalingType": lit("'Fit'")}}]},
               container={
                   **BARE,
                   "border": [{"properties": {"show": lit("true" if active else "false"),
                                              "color": color(TURQUOISE), "radius": lit("2D")}}],
                   "visualLink": [{"properties": {"show": lit("true"), "type": lit("'PageNavigation'"),
                                                  "navigationSection": lit(f"'{flag_lang}'"),
                                                  "tooltip": text_lit(T["flag_tip"][flag_lang])}}],
               })

    # ---- left column: three KPI cards (icon + label, big number, sparkline, comparison line)
    kpis = [  # (icon, label, value measure, sparkline measure, sub measure, sub label)
        ("◎", t["active"], "Active accounts", "Revenue active accounts", "Revenue change active", t["chg_12m"]),
        ("⚠", t["highrisk"], "High-risk accounts", "Revenue high-risk accounts",
         "Revenue change high-risk", t["chg_12m"]),
        ("◆", t["atrisk"], "Total revenue at risk", "Revenue accounts at risk", "% of revenue at risk",
         t["of_revenue"]),
    ]
    for i, (icon, label, value, spark, sub, sub_label) in enumerate(kpis):
        x, y, w, h = 24, 110 + i * 202, 276, 190
        textbox(f"kpi{i + 1}_card", x, y, w, h,
                [{"textRuns": [run(f"{icon}  ", 13, BLUE, bold=True), run(label, 12, NAVY, bold=True, font=FONT_HEAD)]}],
                container={"padding": [{"properties": {"top": lit("16D"), "left": lit("18D")}}]})
        visual(f"kpi{i + 1}", x + 14, y + 50, 160, 56, "card",
               query={"Values": {"projections": [meas("Account Health", value, label)]}},
               objects={"labels": [{"properties": {"color": color(NAVY), "fontSize": lit("24D"),
                                                   "fontFamily": text_lit(FONT_HEAD)}}],
                        "categoryLabels": [{"properties": {"show": lit("false")}}]},
               container=BARE)
        visual(f"kpi{i + 1}_spark", x + 176, y + 46, 88, 64, "areaChart",
               query={"Category": {"projections": [col("Date", "Month start", t["month"])]},
                      "Y": {"projections": [meas("Orders", spark, t["revenue"])]}},
               objects={"categoryAxis": [{"properties": {
                            **MONTH_AXIS["categoryAxis"][0]["properties"], "show": lit("false")}}],
                        "valueAxis": [{"properties": {"show": lit("false")}}],
                        "legend": [{"properties": {"show": lit("false")}}],
                        "dataPoint": [{"properties": {"fill": color(BLUE)}}],
                        "lineStyles": [{"properties": {"strokeWidth": lit("2D")}}]},
               container=BARE, filters=YEAR_FILTER)
        visual(f"kpi{i + 1}_sub", x + 14, y + 120, 248, 58, "card",
               query={"Values": {"projections": [meas("Account Health", sub, sub_label)]}},
               objects={"labels": [{"properties": {"color": color(BLUE), "fontSize": lit("14D"),
                                                   "fontFamily": text_lit(FONT_HEAD)}}],
                        "categoryLabels": [{"properties": {"show": lit("true"), "color": color("#7A7575"),
                                                           "fontSize": lit("8D"),
                                                           "fontFamily": text_lit(FONT_TEXT)}}]},
               container=BARE)

    # ---- centre: where the risk sits
    visual("tierRisk", 316, 110, 452, 268, "barChart",
           query={"Category": {"projections": [col("Account Health", "Account tier", t["tier"])]},
                  "Series": {"projections": [col("Account Health", f"Risk level{suffix}", t["risk"])]},
                  "Y": {"projections": [meas("Account Health", "Accounts", t["accounts"])]}},
           objects={"legend": [{"properties": {"position": lit("'Top'"), "showTitle": lit("false")}}],
                    "categoryAxis": [{"properties": {"showAxisTitle": lit("false")}}],
                    "valueAxis": [{"properties": {"showAxisTitle": lit("false")}}]},
           container=title(t["c_tierrisk"], t["s_tierrisk"]),
           sort={"field": field("Column", "Account Health", "Account tier"), "direction": "Ascending"})
    bar_color = {"solid": {"color": {"expr": {"Measure": {
        "Expression": {"SourceRef": {"Entity": "Account Health"}}, "Property": "Tier bar color"}}}}}
    visual("riskTier", 316, 392, 452, 238, "clusteredBarChart",
           query={"Category": {"projections": [col("Account Health", "Account tier", t["tier"])]},
                  "Y": {"projections": [meas("Account Health", "Total revenue at risk", t["atrisk"])]}},
           objects={"dataPoint": [{"properties": {"fill": bar_color},
                                   "selector": {"data": [{"dataViewWildcard": {"matchingOption": 1}}]}}],
                    "labels": [{"properties": {"show": lit("true")}}],
                    "categoryAxis": [{"properties": {"showAxisTitle": lit("false")}}],
                    "valueAxis": [{"properties": {"show": lit("false")}}]},
           container=title(t["c_tier_rev"], t["s_tier_rev"]),
           sort={"field": field("Column", "Account Health", "Account tier"), "direction": "Ascending"})

    # ---- right column: trend by risk level and the worklist
    visual("revenueTrend", 784, 110, 472, 268, "lineChart",
           query={"Category": {"projections": [col("Date", "Month start", t["month"])]},
                  "Series": {"projections": [col("Account Health", f"Risk level{suffix}", t["risk"])]},
                  "Y": {"projections": [meas("Orders", "Revenue", t["revenue"])]}},
           objects={**MONTH_AXIS,
                    "legend": [{"properties": {"position": lit("'Top'"), "showTitle": lit("false")}}],
                    # from zero, so ups and downs are not exaggerated; units come from the axis labels (K / M)
                    "valueAxis": [{"properties": {"showAxisTitle": lit("false"), "start": lit("0D")}}],
                    "lineStyles": [{"properties": {"strokeWidth": lit("2D")}}]},
           container=title(t["c_trend_risk"], t["s_trend_risk"]), filters=YEAR_FILTER)
    visual("worklist", 784, 392, 472, 238, "tableEx",
           query={"Values": {"projections": [
               col("Customer", "Customer", t["customer"]),
               col("Account Health", "Account tier", t["tier_short"]),
               col("Account Health", f"Risk level{suffix}", t["f_risk"]),
               col("Account Health", "Revenue at risk", t["atrisk"]),
               col("Account Health", "Revenue change %", t["change_short"]),
               col("Account Health", f"Signals {lang.upper()}", t["why"]),
           ]}},
           objects={"total": [{"properties": {"totals": lit("false")}}],
                    "columnHeaders": [{"properties": {"fontFamily": text_lit(FONT_TEXT), "fontSize": lit("9D"),
                                                      "fontColor": color(NAVY), "bold": lit("true"),
                                                      "wordWrap": lit("true")}}],
                    "values": [{"properties": {"fontFamily": text_lit(FONT_TEXT), "fontSize": lit("9D"),
                                               "wordWrap": lit("true")}}],
                    "grid": [{"properties": {"gridHorizontal": lit("true"), "gridVertical": lit("false"),
                                             "rowPadding": lit("3D")}}]},
           container=title(t["c_worklist"], t["s_worklist"]),
           sort={"field": field("Column", "Account Health", "Revenue at risk"), "direction": "Descending"})

    # ---- bottom card: how to read the cockpit
    textbox("story", 316, 644, 940, 56, [{"textRuns": [run(t["story"], 8, NAVY)]}],
            container={"padding": [{"properties": {"top": lit("8D"), "bottom": lit("6D"),
                                                   "left": lit("16D"), "right": lit("16D")}}]})


for lang in LANGS:
    build_page(lang)
print("PBIP written to", OUT)
