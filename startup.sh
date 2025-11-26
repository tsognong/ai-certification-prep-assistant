#!/bin/bash

# Startup script for Azure App Service - Optimized version
# This script is executed when the container starts

echo "🚀 Starting Quiz AI Agent..."

# Use Python's built-in venv for faster startup
VENV_PATH="/tmp/venv"

# Check if dependencies are already installed in persistent storage
if [ ! -d "$VENV_PATH" ]; then
    echo "📦 Setting up Python environment (first time only)..."
    python3 -m venv $VENV_PATH --system-site-packages
    source $VENV_PATH/bin/activate
    
    echo "📥 Installing dependencies with pip cache..."
    pip install --no-cache-dir --upgrade pip setuptools wheel
    pip install --no-cache-dir -r requirements.txt
    
    echo "✅ Environment ready"
else
    echo "✅ Using cached environment"
    source $VENV_PATH/bin/activate
fi

# Start Streamlit with optimized settings
echo "🌐 Starting Streamlit on port 8501..."
exec streamlit run app.py \
  --server.port=8501 \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --browser.gatherUsageStats=false \
  --server.fileWatcherType=none

