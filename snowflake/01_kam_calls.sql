-- Call log of the Key Account Manager: the only data in this project that people write.
-- It lives in its own schema, outside BRONZE / SILVER / GOLD, because dbt rebuilds those layers
-- and must never drop what the KAM has typed. dbt reads it as a source (kam_input.call_log).
-- Rows are added by the Streamlit form KAM_CALLS (snowflake/streamlit/kam_calls.py).
-- Run as TRANSFORMER (it owns the database objects); already run on 2026-10-20.

use role transformer;
use database tpch_medallion;

create schema if not exists kam_input
    comment = 'Data typed by people (not rebuilt by dbt): the KAM call log and its Streamlit form';

create table if not exists kam_input.call_log (
    call_id       number autoincrement start 1 increment 1 primary key,
    customer_key  number not null comment 'Customer called (customer_key of GOLD.DIM_CUSTOMER)',
    called_at     timestamp_ntz not null default current_timestamp()::timestamp_ntz comment 'When the call was logged',
    notes         varchar comment 'Free text: what was agreed',
    logged_by     varchar default current_user() comment 'Snowflake user who logged the call'
)
comment = 'One row per call made by the Key Account Manager';

-- stage that holds the Streamlit app file
create stage if not exists kam_input.streamlit_stage
    comment = 'Source code of the KAM_CALLS Streamlit form';
