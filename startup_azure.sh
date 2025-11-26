#!/bin/bash

# Install dependencies if needed
if [ ! -d "/tmp/venv" ]; then
    python3 -m venv /tmp/venv
    source /tmp/venv/bin/activate
    pip install --no-cache-dir -r requirements.txt
else
    source /tmp/venv/bin/activate
fi

# Run Streamlit on port 8000 (Azure default) or the configured PORT
exec python -m streamlit run app.py \
    --server.port=${PORT:-8000} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.serverAddress="0.0.0.0" \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
