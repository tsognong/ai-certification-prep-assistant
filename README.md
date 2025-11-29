# 🎯 AI Certification Prep Assistant - AI-Powered Exam Preparation Platform

**Universal AI-driven multi-agent platform for adaptive exam preparation. Covers professional certifications (AWS, Azure, MongoDB), language proficiency tests (TCF, IELTS, TOEFL, DELF), driver's license exams, and more. Delivers personalized coaching with real-time performance analytics.**

> **Democratizing Quality Exam Preparation**: Traditional study materials are static, expensive, and impersonal. AI Certification Prep Assistant uses specialized AI agents to deliver adaptive practice exams that mirror real test formats across diverse domains—from cloud architecture certifications to language proficiency and driving theory—making world-class preparation accessible to everyone.

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

## ✨ Features

### 🏠 **Professional Landing Page**
- **Modern Design**: Clean, responsive landing page built with Tailwind CSS
- **Product Overview**: Comprehensive explanation of AI-powered exam preparation across multiple domains
- **Success Statistics**: Real exam failure rates and financial impact of retakes
- **Target Audience**: IT professionals, language learners, students preparing for driver's licenses, career changers, and organizations
- **Capstone-Ready**: Professional presentation suitable for academic competitions

### 🎓 **Exam-Realistic Practice**
- **Mock Exams**: Full-length practice tests mirroring official certification formats
- **Timed Sessions**: Simulate real exam pressure with countdown timers
- **Performance-Based Questions**: Code snippets, configuration scenarios, and hands-on challenges
- **Official Blueprint Alignment**: Questions mapped to actual exam objectives
- **Instant Scoring**: Immediate feedback with detailed explanations

### 🤖 **Multi-Agent AI Intelligence**
### 🤖 **Multi-Agent AI Intelligence**
- **Content Curator Agent**: Automatically fetches and organizes official documentation, exam guides, course syllabi, and study materials from web sources and APIs
  > **ℹ️ The Curator Agent dynamically scrapes content from official sources, ensuring you have the most current materials before your quiz.**
- **Assessment Engine Agent**: Generates adaptive exam questions that adjust difficulty in real-time
- **Learning Coach Agent**: Provides personalized study plans, identifies weak areas, and tracks progress
- **Assessment Engine Agent**: Generates adaptive exam questions that adjust difficulty in real-time
- **Learning Coach Agent**: Provides personalized study plans, identifies weak areas, and tracks progress

### 📚 **Universal Exam Coverage**
- **Professional IT Certifications**: AWS Solutions Architect, Azure Fundamentals, MongoDB Developer, Google Cloud Associate, Terraform Associate
- **Language Proficiency Tests**: TCF (Test de Connaissance du Français), IELTS, TOEFL, DELF/DALF, and other standardized language assessments
- **Driver's License Exams**: Theory tests for various jurisdictions with traffic rules, road signs, and safe driving practices
- **Extensible Framework**: Easily add new exam types through the modular certification pack system
- **Terraform Associate**: Infrastructure as Code, state management, modules
- **Extensible Platform**: Add new certifications in minutes

### 🧠 **Intelligent Memory System**
- **Episodic Memory**: Tracks every practice test, score, and improvement trajectory
- **Semantic Memory**: Vector-based search across thousands of exam concepts
- **Procedural Memory**: Learns your study patterns and optimal learning times
- **Prospective Memory**: Smart reminders for spaced repetition reviews
- **Performance Analytics**: Visual dashboards showing strengths and weaknesses

### 🎯 **Adaptive Learning Engine**
- **Dynamic Difficulty**: Questions automatically adjust based on your performance
- **Personalized Study Paths**: AI recommends next topics based on weak areas
- **Spaced Repetition**: Revisit challenging concepts at optimal intervals
- **Code-First Questions**: Real programming scenarios for technical certifications
- **Progress Tracking**: Visual metrics showing readiness for actual exam

### 🔐 **Enterprise-Grade Security**
- Google OAuth 2.0 authentication
- Encrypted session management (7-day persistence)
- HTTPS-only connections
- MongoDB Atlas encryption at rest
- No credential storage in code

### 📊 **AI for Good Impact**
- **Democratizing Education**: Free/affordable alternative to $500+ boot camps
- **Equal Access**: Anyone with internet can access premium-quality exam prep
- **Career Advancement**: Helps underrepresented groups break into tech
- **Measurable Outcomes**: Track pass rates and career progression

---

## 🏗️ Architecture


### System Architecture Diagram (Generated via Mermaid MCP)

```mermaid
flowchart TB
   %% User Interaction Layer
   U[👤 User] --> API[API Gateway]
   API --> Auth[Authentication Service]
    
   %% Agent Orchestration Layer
   Auth --> AO[Agent Orchestrator]
   AO --> CCA[Content Curator Agent]
   AO --> AEA[Assessment Engine Agent] 
   AO --> LCA[Learning Coach Agent]
    
   %% A2A Communication Layer
   CCA -.->|A2A Messages| AEA
   CCA -.->|A2A Messages| LCA
   AEA -.->|A2A Messages| LCA
   LCA -.->|A2A Messages| CCA
   AEA -.->|A2A Messages| CCA
    
   %% Data Layer
   CCA --> DB[(MongoDB)]
   AEA --> DB
   LCA --> DB
    
   %% External Services
   CCA --> FC[Firecrawl\nWeb Scraping]
   CCA --> GS[Google Search\nAPI]
   AEA --> GEM[GEMINI\nLLM]
   LCA --> GEM
    
   %% Content Sources
   FC --> WEB[Official Docs\nWebsites]
   GS --> SEARCH[Search Results\n& Tutorials]
    
   %% Styling
   classDef userClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px
   classDef agentClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
   classDef serviceClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
   classDef dataClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    
   class U userClass
   class CCA,AEA,LCA,AO agentClass
   class API,Auth,FC,GS,GEM serviceClass
   class DB dataClass
```

**Key Updates:**
- Added `mermaid-mcp` server integration for live architecture diagram generation.
- Agents now communicate via A2A (Agent-to-Agent) messaging for dynamic collaboration.
- Content Curator Agent uses Firecrawl for official documentation scraping and Google Search API for supplementary content.
- All agents interact with MongoDB for persistent storage and memory.

### Data Flow

```
1. USER LOGIN
   User → Streamlit → Google OAuth → MongoDB (users, sessions)

2. CERT SELECTION
   User → Streamlit → MongoDB (certifications) → Display options

3. EXAM GENERATION
   User Request → Orchestrator → Assessment Engine Agent
                                     ↓
                                 Gemini API (generate questions)
                                     ↓
                                 MongoDB (store exam)
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
- **Python 3.14+**: Core language
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
