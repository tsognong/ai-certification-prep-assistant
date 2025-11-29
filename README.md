
# AI Certification Prep Assistant

This project is designed for competitive exam preparation across professional certifications, language proficiency, and licensing tests. It uses a modular, multi-agent system to deliver realistic practice exams, personalized study plans, and performance analytics. All content is sourced from official documentation and APIs, with no reliance on generic AI-generated material.

[![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-red.svg)](https://streamlit.io/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green.svg)](https://www.mongodb.com/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini_API-orange.svg)](https://ai.google.dev/)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Deployment](#-deployment)
- [Configuration](#-configuration)

---

## Features

- Modern, responsive landing page (Tailwind CSS)
- Practice exams aligned to official certification blueprints
- Timed sessions and instant scoring
- Code-based and scenario questions for technical certifications
- Modular agent system:
   - Content Curator: Scrapes and organizes official documentation and guides
   - Assessment Engine: Generates adaptive questions based on user performance
   - Learning Coach: Tracks progress and recommends study plans
- Coverage for IT certifications, language proficiency, and licensing exams
- Extensible: Add new certifications via configuration
- Secure authentication (Google OAuth 2.0), encrypted sessions, HTTPS
- Performance analytics dashboard

---

## Architecture

The system is organized into three main agents:
- Content Curator: Scrapes and summarizes official documentation using Firecrawl and Google Search API.
- Assessment Engine: Generates exam questions, adapts difficulty, and aligns with certification blueprints.
- Learning Coach: Tracks user performance, analyzes results, and recommends study plans.

Agents communicate via an orchestrator and store all data in MongoDB. The platform supports A2A (agent-to-agent) messaging for dynamic collaboration. All diagrams are generated using Mermaid MCP for clarity and reproducibility.

---

## Tech Stack

- Python 3.14+
- Streamlit (web UI)
- Google ADK (agent framework)
- Google Gemini API (LLM, embeddings)
- PyMongo (MongoDB driver)
- Asyncio (async operations)
- MongoDB Atlas (NoSQL database)
- GridFS (media storage)
- Firecrawl (web scraping)
- Google Search API (content retrieval)
- Structlog (logging)
- Plotly (visualizations)
- Textstat (quality metrics)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.14 or higher
- MongoDB Atlas account
- Google Cloud project with Gemini API
- Google OAuth credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tsognong/ai-certification-prep-assistant.git
   cd ai-certification-prep-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

   Required variables:
   ```env
   GEMINI_API_KEY=your-gemini-api-key
   MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/database
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8501
   ```

6. **Load Runtime Content**
   ```bash
   python load_ai_content.py [certification-id]
   # Examples:
   # python load_ai_content.py ai-fundamentals
   # python load_ai_content.py aws-solutions-architect
   # python load_ai_content.py mongodb-developer
   ```

   This dynamically scrapes content from official documentation websites and APIs, keeping the knowledge base current.

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

7. **Access the app**
   Open http://localhost:8501 in your browser

   **🎨 Landing Page**: For the professional landing page, open `index.html` in your browser or serve it with a local web server:
   ```bash
   python -m http.server 8000
   # Then visit http://localhost:8000/index.html
   ```

   Or use the convenience script:
   ```bash
   ./serve_landing.sh
   ```

---

## 🌐 Deployment

### Option 1: Azure App Service

1. **Prepare deployment**
   ```bash
   chmod +x deploy.sh
   ```

2. **Configure Azure CLI**
   ```bash
   az login
   az account set --subscription "your-subscription-id"
   ```

3. **Deploy**
   ```bash
   ./deploy.sh
   ```

   The script will:
   - Create resource group
   - Create App Service plan (Free tier)
   - Create Web App
   - Configure environment variables
   - Deploy from local Git

4. **Set environment variables in Azure**
   ```bash
   az webapp config appsettings set \
     --resource-group cert-prep-rg \
     --name your-app-name \\
     --settings \
       GEMINI_API_KEY="your-key" \
       MONGO_URI="your-mongo-uri" \
       GOOGLE_CLIENT_ID="your-client-id" \
       GOOGLE_CLIENT_SECRET="your-secret" \
       GOOGLE_REDIRECT_URI="https://your-app.azurewebsites.net"
   ```

5. **Update OAuth redirect URI**
   - Go to Google Cloud Console
   - Add: `https://your-app.azurewebsites.net` to authorized redirect URIs

### Option 2: Docker

1. **Build image**
   ```bash
   docker build -t ai-cert-prep-assistant:latest .
   ```

2. **Run container**
   ```bash
   docker run -d \
     -p 8501:8501 \
     -e GEMINI_API_KEY="your-key" \
     -e MONGO_URI="your-mongo-uri" \
     -e GOOGLE_CLIENT_ID="your-client-id" \
     -e GOOGLE_CLIENT_SECRET="your-secret" \
     -e GOOGLE_REDIRECT_URI="http://localhost:8501" \
     ai-cert-prep-assistant:latest
   ```

### Option 3: Streamlit Cloud

1. Fork this repository
2. Go to https://share.streamlit.io/
3. Click "New app"
4. Select your repository and branch
5. Add secrets in Streamlit Cloud dashboard

---

## ⚙️ Configuration

### Adding New Certifications

Edit `certifications/certification_packs.py`:

```python
CERTIFICATION_PACKS = {
    "your-cert-id": {
        "name": "Your Certification Name",
        "provider": "Provider Name",
        "level": "Associate/Professional",
        "topics": ["Topic 1", "Topic 2", ...],
        "blueprint": {
            "total_questions": 50,
            "duration_minutes": 90,
            "passing_score": 70,
            "sections": {...}
        }
    }
}
```

Then run:
```bash
python initialize_system.py
```

### Environment Variables

| Variable              | Description                                 | Required |
|-----------------------|---------------------------------------------|----------|
| GEMINI_API_KEY        | Google Gemini API key                       | Yes      |
| MONGO_URI             | MongoDB connection string                   | Yes      |
| GOOGLE_CLIENT_ID      | OAuth client ID                             | Yes      |
| GOOGLE_CLIENT_SECRET  | OAuth client secret                         | Yes      |
| GOOGLE_REDIRECT_URI   | OAuth redirect URI                          | Yes      |
| FIRECRAWL_API_KEY     | Firecrawl web scraping API key              | Yes      |
| APP_ENV               | Environment (development/production)        | No       |
| DEBUG                 | Debug mode (true/false)                     | No       |

---

## 📊 Project Structure

```
.
├── agents/                    # Multi-agent system
│   ├── multi_agent_system.py # 3 specialized agents
│   └── __init__.py
├── auth/                      # Authentication
│   ├── google_auth.py        # OAuth integration
│   └── __init__.py
├── certifications/            # Certification configs
│   ├── certification_packs.py # Pre-configured certs
│   └── __init__.py
├── memory/                    # Memory system
│   ├── unified_memory.py     # 5-type memory
│   ├── embedding_store.py    # Semantic search
│   └── __init__.py
├── pages/                     # Streamlit pages
│   └── 1_📊_Monitoring_Dashboard.py
├── data/                      # Static data (deprecated - now runtime-based)
│   ├── ai/                   # AI course data (removed)
│   └── mongo/                # MongoDB docs (removed)
├── terraform/                 # Infrastructure as Code
├── app.py                    # Main application
├── initialize_system.py      # Setup script
├── requirements.txt          # Dependencies
├── deploy.sh                 # Deployment script
├── .env.example              # Environment template
└── README.md                 # This file
```

---

## 📈 Monitoring

Access the monitoring dashboard at:
```
http://localhost:8501/1_📊_Monitoring_Dashboard
```

Metrics include:
- Agent response times
- Question quality scores
- User engagement rates
- Error tracking
- Memory usage

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 👥 Authors

- **Tsognong Fidele** - [@tsognong](https://github.com/tsognong)

---

## 🙏 Acknowledgments

- Google Gemini AI for powerful language models
- MongoDB Atlas for scalable database
- Streamlit for the amazing web framework
- Google ADK for agent framework

---

## 📞 Support

- **Issues**: https://github.com/tsognong/ai-certification-prep-assistant/issues
- **Email**: tsognong.fidele@gmail.com

---

## 🔮 Future Vision

AI Certification Prep Assistant aims to become the leading AI-powered exam preparation platform by expanding exam coverage across all domains, integrating with official exam providers, and adding mobile support. Planned enhancements include image-based questions for architecture diagrams, video explanations for complex topics, and collaborative study features to build a global community of learners preparing for professional certifications, language exams, and licensing tests.

---

**Made with ❤️ for certification prep**
