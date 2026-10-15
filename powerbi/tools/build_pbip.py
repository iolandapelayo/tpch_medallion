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
RED, AMBER = "#D64545", "#F2B84B"

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
        "en": "Which accounts are cooling down, why, and how much revenue is at stake - TPC-H SF1, as of 1998-08-02",
        "es": "Qué cuentas se están enfriando, por qué y cuántos ingresos están en juego - TPC-H SF1, a 1998-08-02",
        "ca": "Quins comptes s'estan refredant, per què i quants ingressos hi ha en joc - TPC-H SF1, a 1998-08-02"},
    "tier": {"en": "Account tier", "es": "Categoría de cuenta", "ca": "Categoria del compte"},
    "risk": {"en": "Risk level", "es": "Nivel de riesgo", "ca": "Nivell de risc"},
    "segment": {"en": "Market segment", "es": "Segmento", "ca": "Segment"},
    "region": {"en": "Region", "es": "Región", "ca": "Regió"},
    "active": {"en": "Active accounts", "es": "Cuentas activas", "ca": "Comptes actius"},
    "highrisk": {"en": "High-risk accounts", "es": "Cuentas en riesgo alto", "ca": "Comptes en risc alt"},
    "atrisk": {"en": "Revenue at risk", "es": "Ingresos en riesgo", "ca": "Ingressos en risc"},
    "pctrisk": {"en": "% of revenue at risk", "es": "% de ingresos en riesgo", "ca": "% d'ingressos en risc"},
    "accounts": {"en": "Accounts", "es": "Cuentas", "ca": "Comptes"},
    "revenue": {"en": "Revenue", "es": "Ingresos", "ca": "Ingressos"},
    "month": {"en": "Month", "es": "Mes", "ca": "Mes"},
    "c_tierrisk": {"en": "Accounts by tier and risk level", "es": "Cuentas por categoría y nivel de riesgo",
                   "ca": "Comptes per categoria i nivell de risc"},
    "c_region": {"en": "Revenue at risk by region", "es": "Ingresos en riesgo por región",
                 "ca": "Ingressos en risc per regió"},
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
}
VALUES = {  # data values translated with DAX calculated columns
    "risk": {"High": ("Alto", "Alt"), "Medium": ("Medio", "Mitjà"), "Low": ("Bajo", "Baix"),
             "Inactive": ("Inactivo", "Inactiu")},
    "segment": {"Automobile": ("Automoción", "Automoció"), "Building": ("Construcción", "Construcció"),
                "Furniture": ("Mobiliario", "Mobiliari"), "Household": ("Hogar", "Llar"),
                "Machinery": ("Maquinaria", "Maquinària")},
    "region": {"Africa": ("África", "Àfrica"), "America": ("América", "Amèrica"), "Asia": ("Asia", "Àsia"),
               "Europe": ("Europa", "Europa"), "Middle East": ("Oriente Medio", "Orient Mitjà")},
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
AH_COLS = [
    ("Customer key", "CUSTOMER_KEY", "int64", "0", True, {}),
    ("As of date", "AS_OF_DATE", "dateTime", "yyyy-mm-dd", False, {}),
    ("Account tier", "ACCOUNT_TIER", "string", None, False, {}),
    ("First order date", "FIRST_ORDER_DATE", "dateTime", "yyyy-mm-dd", False, {}),
    ("Last order date", "LAST_ORDER_DATE", "dateTime", "yyyy-mm-dd", False, {}),
    ("Days since last order", "DAYS_SINCE_LAST_ORDER", "int64", "#,0", False, {}),
    ("Usual days between orders", "AVG_DAYS_BETWEEN_ORDERS", "double", "#,0", False, {}),
    ("Lifetime orders", "LIFETIME_ORDERS", "int64", "#,0", False, {}),
    ("Lifetime revenue", "LIFETIME_REVENUE", "double", "#,0", False, {}),
    ("Orders last 12m", "ORDERS_LAST_12M", "int64", "#,0", False, {}),
    ("Revenue last 12m", "REVENUE_LAST_12M", "double", "#,0", False, {}),
    ("Revenue prev 12m", "REVENUE_PREV_12M", "double", "#,0", False, {}),
    ("Revenue change %", "REVENUE_CHANGE_PCT", "double", "0.0%", False, {}),
    ("Late line rate 12m", "LATE_LINE_RATE_12M", "double", "0.0%", False, {}),
    ("Overdue", "IS_OVERDUE", "boolean", None, False, {}),
    ("Declining", "IS_DECLINING", "boolean", None, False, {}),
    ("Service issues", "HAS_SERVICE_ISSUES", "boolean", None, False, {}),
    ("Risk signals", "RISK_SIGNALS", "int64", "0", False, {}),
    ("Risk level", "RISK_LEVEL", "string", None, False, {"sortByColumn": "'Risk order'"}),
    ("Risk order", "RISK_ORDER", "int64", "0", True, {}),
    ("Revenue at risk", "REVENUE_AT_RISK", "double", "#,0", False, {}),
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

CU_CALC = []
for key, col in [("segment", "Market segment"), ("region", "Region")]:
    for idx, lang in enumerate(["ES", "CA"]):
        CU_CALC.append((f"{col} {lang}", switch(f"Customer[{col}]", VALUES[key], idx), {}))

# Risk order is added in Power Query (not DAX) to avoid a circular dependency with sortByColumn
AH_EXTRA_STEP = ('WithOrder = Table.AddColumn(Data, "RISK_ORDER", each if [RISK_LEVEL] = "High" then 1 '
                 'else if [RISK_LEVEL] = "Medium" then 2 else if [RISK_LEVEL] = "Low" then 3 else 4, Int64.Type)')

TABLES = [
    ("Account Health", "FCT_ACCOUNT_HEALTH", AH_COLS, AH_CALC, [
        ("Accounts", "COUNTROWS('Account Health')", "#,0"),
        ("Active accounts", "CALCULATE([Accounts], 'Account Health'[Risk level] <> \"Inactive\")", "#,0"),
        ("High-risk accounts", "CALCULATE([Accounts], 'Account Health'[Risk level] = \"High\")", "#,0"),
        ("Total revenue at risk", "SUM('Account Health'[Revenue at risk])", "#,0"),
        ("% of revenue at risk", "DIVIDE([Total revenue at risk], SUM('Account Health'[Revenue last 12m]))",
         "0.0%"),
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
        ("Order lines", "ORDER_LINES", "int64", "#,0", False, {}),
        ("Net revenue", "NET_REVENUE", "double", "#,0", True, {}),
        ("Delivered date", "DELIVERED_DATE", "dateTime", "yyyy-mm-dd", False, {}),
        ("Late lines", "LATE_LINES", "int64", "#,0", False, {}),
        ("Is late", "IS_LATE", "boolean", None, False, {}),
    ], [], [
        ("Revenue", "SUM(Orders[Net revenue])", "#,0"),
        ("Late orders %", "DIVIDE(CALCULATE(COUNTROWS(Orders), Orders[Is late] = TRUE()), COUNTROWS(Orders))",
         "0.0%"),
    ], None),
    ("Date", "DIM_DATE", [
        ("Date key", "DATE_KEY", "int64", "0", True, {}),
        ("Date", "FULL_DATE", "dateTime", "yyyy-mm-dd", False, {}),
        ("Year", "YEAR", "int64", "0", False, {}),
        ("Quarter", "QUARTER", "int64", "0", False, {}),
        ("Month", "MONTH", "int64", "0", False, {}),
        ("Month name", "MONTH_NAME", "string", None, False, {}),
        ("Year month", "YEAR_MONTH", "string", None, False, {}),
        ("Day name", "DAY_NAME", "string", None, False, {}),
    ], [], [], None),
]


def table_tmdl(name, source, columns, calc_columns, measures, extra_step):
    lines = [f"table {q(name)}", ""]
    for m_name, dax, fmt in measures:
        lines += [f"\tmeasure {q(m_name)} = {dax}", f"\t\tformatString: {fmt}", ""]
    for c_name, src, dtype, fmt, hidden, extra in columns:
        lines += [f"\tcolumn {q(c_name)}", f"\t\tdataType: {dtype}"]
        if fmt:
            lines.append(f"\t\tformatString: {fmt}")
        if hidden:
            lines.append("\t\tisHidden")
        lines.append("\t\tsummarizeBy: none")
        lines.append(f"\t\tsourceColumn: {src}")
        for k, v in extra.items():
            lines.append(f"\t\t{k}: {v}")
        lines += ["", "\t\tannotation SummarizationSetBy = User", ""]
    for c_name, dax, extra in calc_columns:
        lines += [f"\tcolumn {q(c_name)} = {dax}", "\t\tdataType: string", "\t\tsummarizeBy: none",
                  "\t\tdisplayFolder: Translations"]
        for k, v in extra.items():
            lines.append(f"\t\t{k}: {v}")
        lines += ["", "\t\tannotation SummarizationSetBy = User", ""]
    result = "WithOrder" if extra_step else "Data"
    lines += [
        f"\tpartition {q(name)} = m",
        "\t\tmode: import",
        "\t\tsource =",
        "\t\t\t\tlet",
        '\t\t\t\t    Source = Snowflake.Databases(SnowflakeServer, "TPCH_WH", [Role = "TRANSFORMER"]),',
        '\t\t\t\t    Database = Source{[Name = "TPCH_MEDALLION", Kind = "Database"]}[Data],',
        '\t\t\t\t    Gold = Database{[Name = "GOLD", Kind = "Schema"]}[Data],',
        f'\t\t\t\t    Data = Gold{{[Name = "{source}", Kind = "Table"]}}[Data]' + ("," if extra_step else ""),
    ]
    if extra_step:
        lines.append(f"\t\t\t\t    {extra_step}")
    lines += ["\t\t\t\tin", f"\t\t\t\t    {result}", ""]
    return "\n".join(lines)


D = SM / "definition"
write(D / "database.tmdl", "database\n\tcompatibilityLevel: 1601\n")
write(D / "model.tmdl", "\n".join([
    "model Model", "\tculture: en-US", "\tdefaultPowerBIDataSourceVersion: powerBI_V3", "\tsourceQueryCulture: en-US",
    "\tdataAccessOptions", "\t\tlegacyRedirects", "\t\treturnErrorValuesAsNull", "",
    'annotation PBI_QueryOrder = ["SnowflakeServer","Account Health","Customer","Orders","Date"]', "",
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
# Risk levels are sorted High, Medium, Low, Inactive (via 'Risk order') -> red, amber, teal, grey
write(STATIC / "RegisteredResources/KAMTheme.json", {
    "name": "Propelling KAM Health",
    "dataColors": [RED, AMBER, TEAL, GREY, SLATE, TURQUOISE, TURQ_LIGHT, "#38414F"],
    "foreground": TEXT, "background": "#FFFFFF", "tableAccent": TURQUOISE,
    "visualStyles": {"*": {"*": {"border": [{"show": True, "color": {"solid": {"color": "#DEDADA"}}, "radius": 12}]}}},
})

write(R / "pages/pages.json", {"$schema": f"{S}/item/report/definition/pagesMetadata/1.0.0/schema.json",
                               "pageOrder": LANGS, "activePageName": "en"})


def lit(value):
    return {"expr": {"Literal": {"Value": value}}}


def text_lit(text):
    return lit("'" + text.replace("'", "''") + "'")


def color(hex_):
    return {"solid": {"color": lit(f"'{hex_}'")}}


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


def title(text):
    return {"title": [{"properties": {"show": lit("true"), "text": text_lit(text)}}]}


def build_page(lang):
    t = {k: v[lang] for k, v in T.items()}
    suffix = "" if lang == "en" else f" {lang.upper()}"
    page_dir = R / "pages" / lang
    page = {
        "$schema": f"{S}/item/report/definition/page/1.4.0/schema.json",
        "name": lang, "displayName": t["page"], "displayOption": "FitToPage", "height": 720, "width": 1280,
        "objects": {"background": [{"properties": {"color": color(BG), "transparency": lit("0D")}}]},
    }
    if lang != "en":
        page["visibility"] = "HiddenInViewMode"   # the flags are the language switch
    write(page_dir / "page.json", page)

    z = [0]

    def visual(name, x, y, w, h, visual_type, query=None, objects=None, container=None, sort=None):
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
        write(page_dir / "visuals" / name / "visual.json", {
            "$schema": f"{S}/item/report/definition/visualContainer/2.0.0/schema.json",
            "name": name,
            "position": {"x": x, "y": y, "z": z[0], "width": w, "height": h, "tabOrder": z[0]},
            "visual": v,
        })

    # Title band (slate) with white title and light turquoise subtitle
    visual("title", 16, 4, 1248, 58, "textbox", objects={"general": [{"properties": {"paragraphs": [
        {"textRuns": [{"value": t["title"], "textStyle": {"fontWeight": "bold", "fontSize": "14pt",
                                                          "color": "#FFFFFF"}}]},
        {"textRuns": [{"value": t["subtitle"], "textStyle": {"fontSize": "8pt", "color": TURQ_LIGHT}}]},
    ]}}]}, container={"background": [{"properties": {"show": lit("true"), "color": color(SLATE),
                                                        "transparency": lit("0D")}}],
                      "border": [{"properties": {"show": lit("false")}}]})

    # Flags (top right): each one navigates to its language page; the current one has a turquoise border
    for i, flag_lang in enumerate(LANGS):
        active = flag_lang == lang
        visual(f"flag_{flag_lang}", 1130 + i * 44, 21, 36, 24, "image",
               objects={"general": [{"properties": {"imageUrl": {"expr": {"ResourcePackageItem": {
                   "PackageName": "RegisteredResources", "PackageType": 1, "ItemName": FLAG_FILES[flag_lang]}}}}}],
                        "imageScaling": [{"properties": {"imageScalingType": lit("'Fit'")}}]},
               container={
                   "background": [{"properties": {"show": lit("false")}}],
                   "padding": [{"properties": {"top": lit("0D"), "bottom": lit("0D"),
                                               "left": lit("0D"), "right": lit("0D")}}],
                   "border": [{"properties": {"show": lit("true" if active else "false"),
                                              "color": color(TURQUOISE), "radius": lit("2D")}}],
                   "visualLink": [{"properties": {"show": lit("true"), "type": lit("'PageNavigation'"),
                                                  "navigationSection": lit(f"'{flag_lang}'"),
                                                  "tooltip": text_lit(T["flag_tip"][flag_lang])}}],
               })

    # Slicers
    cols_x = [16, 332, 648, 964]
    slicers = [("Account Health", "Account tier", t["tier"]), ("Account Health", f"Risk level{suffix}", t["risk"]),
               ("Customer", f"Market segment{suffix}", t["segment"]), ("Customer", f"Region{suffix}", t["region"])]
    for i, (entity, prop, label) in enumerate(slicers):
        visual(f"slicer{i + 1}", cols_x[i], 64, 300, 62, "slicer",
               query={"Values": {"projections": [col(entity, prop, label)]}},
               objects={"data": [{"properties": {"mode": lit("'Dropdown'")}}]})

    # KPI cards
    kpis = [("Active accounts", t["active"], SLATE), ("High-risk accounts", t["highrisk"], RED),
            ("Total revenue at risk", t["atrisk"], RED), ("% of revenue at risk", t["pctrisk"], SLATE)]
    for i, (prop, label, hex_) in enumerate(kpis):
        visual(f"kpi{i + 1}", cols_x[i], 132, 300, 100, "card",
               query={"Values": {"projections": [meas("Account Health", prop, label)]}},
               objects={"labels": [{"properties": {"color": color(hex_), "fontSize": lit("26D")}}],
                        "categoryLabels": [{"properties": {"fontSize": lit("10D")}}]})

    # Charts
    visual("tierRisk", 16, 240, 404, 210, "barChart",
           query={"Category": {"projections": [col("Account Health", "Account tier", t["tier"])]},
                  "Series": {"projections": [col("Account Health", f"Risk level{suffix}", t["risk"])]},
                  "Y": {"projections": [meas("Account Health", "Accounts", t["accounts"])]}},
           container=title(t["c_tierrisk"]),
           sort={"field": field("Column", "Account Health", "Account tier"), "direction": "Ascending"})
    visual("riskRegion", 436, 240, 404, 210, "clusteredBarChart",
           query={"Category": {"projections": [col("Customer", f"Region{suffix}", t["region"])]},
                  "Y": {"projections": [meas("Account Health", "Total revenue at risk", t["atrisk"])]}},
           objects={"dataPoint": [{"properties": {"fill": color(SLATE)}}]},
           container=title(t["c_region"]),
           sort={"field": field("Measure", "Account Health", "Total revenue at risk"), "direction": "Descending"})
    visual("revenueTrend", 856, 240, 408, 210, "lineChart",
           query={"Category": {"projections": [col("Date", "Year month", t["month"])]},
                  "Y": {"projections": [meas("Orders", "Revenue", t["revenue"])]}},
           objects={"dataPoint": [{"properties": {"fill": color(TEAL)}}]},
           container=title(t["c_trend"]),
           sort={"field": field("Column", "Date", "Year month"), "direction": "Ascending"})

    # Worklist table
    visual("worklist", 16, 462, 1248, 246, "tableEx",
           query={"Values": {"projections": [
               col("Customer", "Customer", t["customer"]),
               col("Account Health", "Account tier", t["tier_short"]),
               col("Customer", f"Market segment{suffix}", t["segment"]),
               col("Customer", f"Region{suffix}", t["region"]),
               col("Account Health", f"Risk level{suffix}", t["risk"]),
               col("Account Health", "Revenue at risk", t["atrisk"]),
               col("Account Health", "Revenue change %", t["change"]),
               col("Account Health", "Days since last order", t["days_since"]),
               col("Account Health", "Usual days between orders", t["usual_days"]),
               col("Account Health", f"Overdue {lang.upper()}", t["overdue"]),
               col("Account Health", f"Declining {lang.upper()}", t["declining"]),
               col("Account Health", f"Service issues {lang.upper()}", t["service"]),
           ]}},
           objects={"total": [{"properties": {"totals": lit("false")}}]},
           container=title(t["c_table"]),
           sort={"field": field("Column", "Account Health", "Revenue at risk"), "direction": "Descending"})


for lang in LANGS:
    build_page(lang)
print("PBIP written to", OUT)
