-- Deploys the Streamlit form KAM_CALLS (source: snowflake/streamlit/kam_calls.py).
-- The PUT command uploads the local file, so run this from SnowSQL / a Python connector, not Snowsight.
-- Already deployed on 2026-10-20. To open it: Snowsight -> Projects -> Streamlit -> KAM_CALLS.

use role transformer;
use database tpch_medallion;

put 'file://streamlit/kam_calls.py' @kam_input.streamlit_stage overwrite = true auto_compress = false;

create or replace streamlit kam_input.kam_calls
    from '@tpch_medallion.kam_input.streamlit_stage'
    main_file = 'kam_calls.py'
    query_warehouse = tpch_wh
    title = 'KAM call log'
    comment = 'Form where the Key Account Manager marks customers as called';
