# 🎯 CertAgent - AI-Assisted Certification Preparation

**Intelligent multi-agent system for personalized certification exam preparation**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
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

## ✨ Features

### 🤖 **Multi-Agent AI System**
- **Content Curator Agent**: Fetches and organizes study materials
- **Assessment Engine Agent**: Generates adaptive exam questions
- **Learning Coach Agent**: Provides personalized guidance and analytics

### 📚 **Multi-Certification Support**
- MongoDB Developer Associate
- AWS Solutions Architect
- Azure Fundamentals (AZ-900)
- Google Cloud Associate
- Terraform Associate
- **Extensible**: Easy to add new certifications

### 🧠 **Unified Memory System**
- **Short-term Memory**: Recent 24h activities
- **Episodic Memory**: Quiz history and performance
- **Semantic Memory**: Vector embeddings for content search
- **Procedural Memory**: Learning patterns and habits
- **Prospective Memory**: Scheduled reviews and reminders

### 🎯 **Adaptive Learning**
- Questions adjust based on performance
- Difficulty scales with user progress
- Weak topic identification
- Personalized study plans

### 🔐 **Authentication & Security**
- Google OAuth integration
- Persistent sessions (7-day expiry)
- Browser fingerprinting
- Secure credential management

### 📊 **Real-time Monitoring**
- Agent performance metrics
- Question quality scoring
- User engagement analytics
- Error tracking and logging

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT FRONTEND                           │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────┐  │
│  │  Login Page  │→ │ Cert Selector│→ │  Quiz Interface         │  │
│  │  (OAuth)     │  │ & Topics     │  │  - Questions Display    │  │
│  └──────────────┘  └──────────────┘  │  - Answer Submission    │  │
│                                       │  - Results & Coaching   │  │
│                                       └─────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      AGENT ORCHESTRATOR                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Routes requests to agents                  │  │
│  │              Logs activities & metrics                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│         │                    │                    │                 │
│         ▼                    ▼                    ▼                 │
│  ┌────────────┐      ┌──────────────┐     ┌────────────────┐      │
│  │  Content   │      │  Assessment  │     │   Learning     │      │
│  │  Curator   │      │   Engine     │     │    Coach       │      │
│  │  Agent     │      │   Agent      │     │    Agent       │      │
│  └─────┬──────┘      └──────┬───────┘     └────────┬───────┘      │
│        │                    │                      │                │
│        │ • Fetch materials  │ • Generate quiz      │ • Analyze perf│
│        │ • Summarize docs   │ • Adaptive diff.     │ • Study plan  │
│        │ • Semantic search  │ • Validate qs        │ • Coaching    │
│        │                    │                      │                │
└────────┼────────────────────┼──────────────────────┼────────────────┘
         │                    │                      │
         ▼                    ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        GOOGLE GEMINI API                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Configurable Models:                                         │  │
│  │  • Generation: gemini-2.5-flash-lite, gemini-pro, etc.       │  │
│  │  • Embeddings: text-embedding-004, text-embedding-005        │  │
│  │  • Content generation   • Question creation                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      MONGODB ATLAS DATABASE                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ certifications│  │    users     │  │      quizzes            │  │
│  │ - packs       │  │ - profiles   │  │  - questions            │  │
│  │ - topics      │  │ - OAuth data │  │  - user_answers         │  │
│  │ - blueprints  │  │ - sessions   │  │  - scores               │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  embeddings  │  │ agent_logs   │  │   memory_*              │  │
│  │ - semantic   │  │ - activities │  │  - episodic             │  │
│  │ - vectors    │  │ - metrics    │  │  - procedural           │  │
│  │              │  │              │  │  - prospective          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. USER LOGIN
   User → Streamlit → Google OAuth → MongoDB (users, sessions)

2. CERT SELECTION
   User → Streamlit → MongoDB (certifications) → Display options

3. QUIZ GENERATION
   User Request → Orchestrator → Assessment Engine Agent
                                     ↓
                                 Gemini API (generate questions)
                                     ↓
                                 MongoDB (store quiz)
                                     ↓
                                 Streamlit (display)

4. ANSWER SUBMISSION
   User Answers → Orchestrator → Learning Coach Agent
                                     ↓
                                 Gemini API (analyze performance)
                                     ↓
                                 MongoDB (store results + memory)
                                     ↓
                                 Streamlit (show results + coaching)
```

---

## 🛠️ Tech Stack

### **Backend**
- **Python 3.10+**: Core language
- **Streamlit**: Web framework
- **Google ADK**: Agent framework
- **Google Gemini API**: LLM and embeddings
- **PyMongo**: MongoDB driver
- **Asyncio**: Async operations

### **Database**
- **MongoDB Atlas**: NoSQL database
- **GridFS**: Media file storage (images, audio)
- **Vector Embeddings**: Semantic search

### **AI/ML**
- **Google Gemini API**: Configurable models (gemini-pro, gemini-flash, etc.)
- **Text Embeddings**: text-embedding-004/005 for semantic search
- **Structured Logging**: Observability

### **Authentication**
- **Google OAuth 2.0**: User authentication
- **Session Management**: MongoDB-backed sessions

### **Monitoring**
- **Structlog**: JSON logging
- **Plotly**: Visualizations
- **Textstat**: Quality metrics

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
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

5. **Initialize the system**
   ```bash
   python initialize_system.py
   ```

6. **Run the application**
   ```bash
   streamlit run app_v3.py
   ```

7. **Access the app**
   Open http://localhost:8501 in your browser

---

## 🌐 Deployment

### Option 1: Azure App Service (Recommended)

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
     --resource-group quiz-ai-rg \
     --name your-app-name \
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
   docker build -t certagent:latest .
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
     certagent:latest
   ```

### Option 3: Heroku

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Set config vars**
   ```bash
   heroku config:set GEMINI_API_KEY="your-key"
   heroku config:set MONGO_URI="your-mongo-uri"
   heroku config:set GOOGLE_CLIENT_ID="your-client-id"
   heroku config:set GOOGLE_CLIENT_SECRET="your-secret"
   heroku config:set GOOGLE_REDIRECT_URI="https://your-app.herokuapp.com"
   ```

3. **Deploy**
   ```bash
   git push heroku develop:main
   ```

### Option 4: Streamlit Cloud

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

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | ✅ |
| `MONGO_URI` | MongoDB connection string | ✅ |
| `GOOGLE_CLIENT_ID` | OAuth client ID | ✅ |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret | ✅ |
| `GOOGLE_REDIRECT_URI` | OAuth redirect URI | ✅ |
| `APP_ENV` | Environment (dev/prod) | ❌ |
| `DEBUG` | Debug mode (true/false) | ❌ |

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
├── data/                      # Study materials
│   ├── ai/                   # AI course data
│   └── mongo/                # MongoDB docs
├── terraform/                 # Infrastructure as Code
├── app_v3.py                 # Main application
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

## 🔮 Roadmap

- [ ] Multimodal support (images, audio, code snippets)
- [ ] More certification providers
- [ ] Mobile app
- [ ] Collaborative study sessions
- [ ] Spaced repetition algorithm
- [ ] AI-powered study material generation
- [ ] Integration with official exam providers

---

**Made with ❤️ for certification prep**
