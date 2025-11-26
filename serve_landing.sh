#!/bin/bash
# Serve the AI Certification Prep Assistant (integrated landing page + app)
echo "🎯 Starting AI Certification Prep Assistant..."
echo "📱 App URL: http://localhost:8501"
echo ""
echo "Features:"
echo "  • Modern Tailwind CSS landing page"
echo "  • Google OAuth authentication"
echo "  • Multi-agent AI system"
echo "  • Certification exam preparation"
echo ""
echo "Press Ctrl+C to stop the server"
streamlit run app.py --server.port 8501 --server.address 0.0.0.0