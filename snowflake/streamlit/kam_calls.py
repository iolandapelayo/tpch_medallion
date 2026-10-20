"""KAM call log: the Key Account Manager marks a customer as called.

Streamlit in Snowflake app (KAM_INPUT.KAM_CALLS). It writes one row per call into KAM_INPUT.CALL_LOG;
dbt reads that table through views (Bronze -> Silver -> Gold), so the Power BI worklist shows the new
status after a refresh, without running dbt. Deployed with snowflake/02_kam_calls_app.sql.
"""
import streamlit as st
from snowflake.snowpark.context import get_active_session

session = get_active_session()
CALLED_WINDOW_DAYS = 7      # same as the dbt var called_window_days

st.title("KAM call log")
st.caption("Furniture · United Kingdom · key accounts (tier A). "
           f"An account counts as **Called** if it was called in the last {CALLED_WINDOW_DAYS} days.")

# Same order as the Power BI worklist: High risk first, then by revenue at risk
WORKLIST = """
    select c.customer_key, c.customer_name, c.contact_person, c.phone,
           h.risk_level, h.revenue_at_risk, s.call_status, s.last_called_at
    from tpch_medallion.gold.fct_account_health h
    join tpch_medallion.gold.dim_customer c on c.customer_key = h.customer_key
    join tpch_medallion.gold.dim_customer_call_status s on s.customer_key = h.customer_key
    where h.account_tier = 'A'
    order by case h.risk_level when 'High' then 1 when 'Medium' then 2 when 'Low' then 3 else 4 end,
             h.revenue_at_risk desc
"""
accounts = session.sql(WORKLIST).to_pandas()

only_not_called = st.toggle("Show only accounts not called", value=True)
shown = accounts[accounts["CALL_STATUS"] == "Not called"] if only_not_called else accounts
st.dataframe(
    shown.rename(columns={"CUSTOMER_NAME": "Customer", "CONTACT_PERSON": "Contact", "PHONE": "Phone",
                          "RISK_LEVEL": "Risk", "REVENUE_AT_RISK": "Revenue at risk",
                          "CALL_STATUS": "Call status", "LAST_CALLED_AT": "Last call"})
         .drop(columns=["CUSTOMER_KEY"]),
    hide_index=True, use_container_width=True,
    column_config={"Revenue at risk": st.column_config.NumberColumn(format="$%d")},
)

st.subheader("Log a call")
with st.form("log_call", clear_on_submit=True):
    labels = {row.CUSTOMER_KEY: f"{row.CUSTOMER_NAME} · {row.RISK_LEVEL} · contact {row.CONTACT_PERSON}"
              for row in shown.itertuples()}
    customer = st.selectbox("Customer", options=list(labels), format_func=labels.get)
    notes = st.text_area("Notes (optional)", placeholder="What did you agree?")
    if st.form_submit_button("Mark as called", type="primary") and customer is not None:
        session.sql("insert into tpch_medallion.kam_input.call_log (customer_key, notes) values (?, ?)",
                    params=[int(customer), notes or None]).collect()
        st.success(f"Call logged: {labels[customer].split(' · ')[0]}. Refresh Power BI to see it.")
        st.rerun()

st.subheader("Latest calls")
calls = session.sql("""
    select l.call_id, l.called_at, c.customer_name, l.notes, l.logged_by
    from tpch_medallion.kam_input.call_log l
    left join tpch_medallion.gold.dim_customer c on c.customer_key = l.customer_key
    order by l.called_at desc
    limit 20
""").to_pandas()
st.dataframe(calls.rename(columns={"CALLED_AT": "Called at", "CUSTOMER_NAME": "Customer", "NOTES": "Notes",
                                   "LOGGED_BY": "Logged by"}).drop(columns=["CALL_ID"]),
             hide_index=True, use_container_width=True)

# For demos: undo a call logged by mistake
with st.expander("Remove a call logged by mistake"):
    if calls.empty:
        st.write("No calls yet.")
    else:
        options = {row.CALL_ID: f"{row.CALLED_AT:%Y-%m-%d %H:%M} · {row.CUSTOMER_NAME}" for row in calls.itertuples()}
        call_id = st.selectbox("Call", options=list(options), format_func=options.get)
        if st.button("Remove this call"):
            session.sql("delete from tpch_medallion.kam_input.call_log where call_id = ?",
                        params=[int(call_id)]).collect()
            st.rerun()
