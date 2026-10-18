# Guía para la demo

## Guion (15 min)

1. **Caso de uso (2 min):** salud de la cuenta y riesgo de pérdida; quién lo usa y para qué.
2. **Snowflake (2 min):** base de datos `TPCH_MEDALLION` con los esquemas BRONZE, SILVER y GOLD.
3. **Lineage en dbt docs (4 min):** fuente → bronze → silver → gold → cockpit del KAM.
4. **Código (5 min):** `bronze_ingest`, `slv_lineitem`, `fct_account_health` (las 3 señales) y los tests.
5. **Query en vivo (2 min):** "la lista de esta semana" del KAM.

## Las 5 preguntas

### 1. ¿Por qué Medallion?

Cada capa tiene un único trabajo:
- **Bronze** guarda una copia fiel de la fuente. Frente a consultar la fuente directamente:
  - la fuente no es mía (es un share de Snowflake; en la vida real sería un ERP o un CRM) y puede cambiar o desaparecer;
  - puedo rehacer Silver y Gold sin volver a tocar la fuente;
  - sé cuándo se cargó cada dato (`_ingested_at`).
- **Silver** da una versión limpia y fiable de cada tabla, que sirve para cualquier caso de uso.
- **Gold** da un modelo preparado para un consumidor concreto (el KAM). El BI lo usa sin transformar nada.

**La mejor prueba de que funciona:** cambié el caso de uso a mitad del proyecto (de rentabilidad
a salud de cuentas) y **solo tuve que tocar Gold**. Bronze y Silver quedaron igual.
Por eso Silver también limpia piezas, proveedores y costes, aunque este caso no los use:
están listos para el siguiente caso de uso.

### 2. ¿Qué va en cada capa?

| Pregunta | Capa |
|---|---|
| ¿Cambio el dato? No, solo añado la fecha de carga | Bronze |
| ¿Arreglo el dato o aplico una regla que vale para cualquier uso? | Silver |
| ¿Depende de este caso de uso (agregar por pedido y por cuenta, señales de riesgo)? | Gold |

Lo que hago en Silver:
- Nombres legibles (`l_extendedprice` → `gross_amount`).
- Texto limpio: quitar espacios y poner las mayúsculas uniformes (`AUTOMOBILE` → `Automobile`).
- Códigos traducidos: `R/A/N` → Returned/Accepted/Not returned, `F/O/P` → estado del pedido, `1-URGENT` → Urgent.
- Códigos compuestos separados: `STANDARD POLISHED BRASS` → clase / acabado / material.
- Reglas de negocio generales: revenue neto, importe facturado, **entrega tardía** (llega después de la fecha comprometida).

¿Por qué en Silver y no en Gold? Para que se definan **una sola vez**. Si el revenue se
calculara en Gold, cada modelo podría calcularlo de una forma distinta.
En cambio, "cuenta en riesgo" es una regla **de este caso de uso**, así que va en Gold.

### 3. Caso de uso y consumidor

**Consumidor:** el Key Account Manager que gestiona las **cuentas de mobiliario (Furniture) en Europa**, y su responsable comercial.

**Pregunta:** *¿qué cuentas de mi cartera se están enfriando, por qué, y cuánto dinero hay en juego?*

**Por qué una cartera concreta:** un KAM no gestiona los 100.000 clientes, sino los suyos. Oro es la capa
"para un consumidor", así que contiene **solo su cartera**: 5.919 clientes de Furniture en Europa (4.024 con pedidos)
en 5 países (Alemania, Francia, Reino Unido, Rumanía y Rusia).
- La cartera se define con **2 variables de dbt** (`portfolio_segment`, `portfolio_region`). Para otro KAM
  basta con cambiarlas: bronce y plata **no se tocan**. Es la mejor prueba de por qué se separan las capas.
- Los rankings (peor 25 % en servicio, tier A/B/C) **comparan sus cuentas entre sí**: "tus 20 % más grandes",
  no las más grandes del mundo.
- La fecha de referencia sigue siendo el último pedido de **todos** los datos (1998-08-02), no el de la cartera.

**Decisión que apoya:** a quién llamar esta semana y con qué argumento.
- Si la cuenta está **retrasada**, la llamada es comercial: "hace tiempo que no nos pides".
- Si **cae su revenue**, hay que revisar precio o competencia.
- Si tiene **problemas de servicio**, hay que escalar a operaciones *antes* de llamar.

**Modelo Gold:**
- `fct_account_health`: **una fila por cuenta**. Es la lista de trabajo del KAM. Contiene:
  - actividad: primer y último pedido, días sin pedir, intervalo habitual entre pedidos;
  - tendencia: revenue de los últimos 12 meses frente a los 12 anteriores;
  - servicio: % de **líneas** de pedido que llegaron tarde en los últimos 12 meses;
  - 3 señales, el nivel de riesgo, el **revenue en riesgo** y el **tier A/B/C** (para priorizar las cuentas grandes).
- `fct_orders`: una fila por pedido. Sirve para ver la evolución mensual de una cuenta y bajar al detalle.
- `dim_customer`: **la cartera** (filtrada por segmento y región), con el país de cada cliente; y `dim_date`.

**Por qué estas reglas:**
- **Simples y explicables:** un KAM tiene que entender por qué una cuenta sale en rojo. Un modelo de machine learning sería una caja negra.
- **Retraso relativo a cada cliente:** 60 días sin pedir es mucho para quien pide cada 20, y normal para quien pide cada 90.
- **Umbrales como variables de dbt** (`overdue_factor`, `decline_threshold`): negocio puede ajustarlos sin tocar el SQL.
- **"Inactive" va aparte:** son cuentas ya perdidas, que necesitan una campaña de recuperación y no una llamada de seguimiento.

**Detalles del dataset que tuve en cuenta:**
- La **fecha de referencia** es el último pedido de los datos (1998-08-02), porque los datos no llegan a hoy.
- Para el servicio solo cuento pedidos **ya entregados** en esa fecha.
- **El servicio se mide por línea, no por pedido:** en TPC-H casi todos los pedidos tienen al menos
  una línea tardía, así que el 80 % de las cuentas tenía un 100 % de pedidos tardíos. Con todos empatados
  no se puede saber quién está en el "peor 25 %". Por líneas sí hay diferencias (la media es un 62 %).
  El ranking se hace solo entre las cuentas que tienen entregas que medir.
- **No uso devoluciones:** en TPC-H la marca de devolución solo es válida hasta 1995-06-17 (la "fecha actual" del estándar). Después todo sale como "no devuelto".
- **Un tercio de los clientes nunca ha pedido** (en TPC-H, los que tienen clave múltiplo de 3). No son cuentas, así que no aparecen en `fct_account_health`.
- **Los datos son sintéticos y uniformes,** así que los resultados salen bastante repartidos. Lo importante es el mecanismo, que funcionaría igual con datos reales.

**Resultado** (99.996 cuentas): 9.701 High · 31.716 Medium · 45.245 Low · 13.334 Inactive.
Las señales marcan: overdue 15.673 cuentas, declining 38.267, service issues 18.904.
El revenue en riesgo es el 35 % del revenue de los últimos 12 meses.

**Un fallo que encontré y corregí:** al principio la señal de servicio medía pedidos tardíos y
**no marcaba ninguna cuenta** (por el empate explicado arriba). Los tests no lo detectaban porque
la tabla era técnicamente correcta. Lo arreglé midiendo por líneas y añadí dos tests para que no vuelva
a pasar: una alarma de negocio y un unit test (ver "Tests").

### 4. ¿Qué añadiría en producción?

- **Histórico del score:** guardar la foto cada semana (dbt snapshot o modelo incremental) para ver cómo evoluciona cada cuenta, y **validar el score**: ¿las cuentas marcadas como "High" acabaron dejando de comprar?
- **Más señales** con datos reales: tickets de soporte, NPS, visitas o llamadas del CRM, impagos.
- **Asignar cada cuenta a su KAM** (desde el CRM) para que cada uno vea solo su cartera.
- **Alertas:** avisar al KAM cuando una cuenta A pasa a "High".
- **Orquestación:** ejecución diaria o semanal programada.
- **Observabilidad:** frescura de las fuentes, alertas cuando falla un test, control de volúmenes.
- **Carga incremental** de lineitem en vez de recargarla entera.

### 5. CI/CD

Un único workflow de GitHub Actions ejecuta `dbt build` (crea los modelos y pasa todos los tests):
- en cada **pull request**, sobre los esquemas `CI_*` (la macro `generate_schema_name` cambia el nombre de los esquemas). Si algo falla, no se hace merge;
- en cada **merge a main**, sobre los esquemas reales.

**Valor:** si alguien cambia una regla del score, no llega a producción sin pasar los tests.
Así los KAM pueden confiar en la lista que reciben.
**Mejora posible:** construir solo los modelos que han cambiado (*Slim CI*).

## Tests (38 tests de datos + 1 unit test)

- Claves únicas y no nulas en todas las tablas de Silver y Gold.
- Valores permitidos: segmentos, estados, prioridades, tier (A/B/C) y nivel de riesgo.
- Dos tests genéricos propios: `value_between` (por ejemplo, de 0 a 3 señales) y `unique_combination`.
- Las facts solo apuntan a clientes y fechas que existen (tests de relación).
- Dos tests de reconciliación:
  - el total de cada pedido coincide con la suma de sus líneas (regla de TPC-H);
  - `fct_orders` tiene las mismas líneas y el mismo revenue que Silver (la agregación no pierde ni duplica nada).
- **Alarma de negocio:** cada señal de riesgo tiene que marcar entre el 1 % y el 60 % de las cuentas.
  Una señal que no marca a nadie (o a casi todos) no ayuda al KAM a decidir a quién llamar.
- **Unit test de `fct_account_health`:** 4 clientes inventados, uno por nivel de riesgo (Low, Inactive,
  High y Medium), con el resultado calculado a mano. Comprueba las reglas sin depender de los datos reales,
  y si falla, dbt no reconstruye la tabla.

## Queries para la demo

```sql
-- 1. La lista de esta semana: cuentas A en riesgo alto, ordenadas por dinero en juego
select c.customer_name, c.customer_nation,
       h.revenue_at_risk, h.days_since_last_order, h.avg_days_between_orders,
       h.revenue_change_pct, h.is_overdue, h.is_declining, h.has_service_issues
from gold.fct_account_health h
join gold.dim_customer c on h.customer_key = c.customer_key
where h.account_tier = 'A' and h.risk_level = 'High'
order by h.revenue_at_risk desc
limit 20;

-- 2. Resumen de la cartera: cuántas cuentas y cuánto revenue hay en cada nivel de riesgo
select account_tier, risk_level, count(*) as accounts,
       sum(revenue_last_12m) as revenue_last_12m
from gold.fct_account_health
group by all order by 1, 2;

-- 3. Detalle de una cuenta: evolución mensual de sus pedidos
select d.year_month, count(*) as orders, sum(f.net_revenue) as revenue,
       sum(f.late_lines) / sum(f.order_lines) as late_line_rate
from gold.fct_orders f
join gold.dim_date d on f.order_date_key = d.date_key
where f.customer_key = 1   -- cambiar por la cuenta que interese
group by all order by 1;
```

## Bonus: dashboard en Power BI

- **Proceso:** prompt → mockup HTML (`powerbi/mockup.html`) → prompt → Power BI Project (`KAM_Health.pbip`).
  Los dos prompts están en `powerbi/README.md`.
- **Por qué PBIP:** el informe y el modelo son archivos de texto (PBIR en JSON y TMDL). Por eso:
  - una IA los puede generar;
  - se versionan en Git junto al proyecto dbt;
  - se revisan en un pull request como cualquier código.
- **Cómo lo comprobé:**
  - cada JSON se validó contra los esquemas oficiales de Microsoft;
  - el modelo TMDL se cargó con la librería oficial de Analysis Services.
- **Qué enseñar:**
  - filtrar el riesgo a "High" y el tier a "A";
  - hacer clic en la primera cuenta de la tabla y ver su histórico en el gráfico de líneas;
  - explicar por qué esa cuenta está en riesgo, mirando las columnas Overdue, Declining y Service issues.

## Datos del dataset

150K clientes (unos 100K con pedidos) · 1,5M pedidos · 6M líneas · pedidos de 1992-01-01 a 1998-08-02.
