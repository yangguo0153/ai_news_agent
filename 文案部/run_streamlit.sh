#!/bin/bash
export STREAMLIT_CLIENT_SHOW_ERROR_DETAILS=false
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_HEADLESS=true
.venv/bin/streamlit run web_ui.py > stream_debug.log 2>&1
