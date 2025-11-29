"""
AI Certification Prep Assistant - Universal AI-Assisted Exam Preparation

Intelligent multi-agent system for personalized exam preparation across all domains.
Supports: MongoDB, AWS, Azure, GCP, Terraform, language tests, and licensing exams.
"""
import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

import streamlit as st
from pymongo import MongoClient
from google.adk.models.google_llm import Gemini
from dotenv import load_dotenv
import structlog

# Load environment
load_dotenv()

# Import our new modules
from certifications.certification_packs import CertificationPackLoader, get_available_certifications_simple
from agents.multi_agent_system import AgentOrchestrator
from memory.unified_memory import UnifiedMemorySystem
from memory.embedding_store import EmbeddingStore
from auth.google_auth import GoogleAuthManager

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Page config
st.set_page_config(
    page_title="AI Certification Prep Assistant - Universal AI-Assisted Exam Prep",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .cert-card {
        padding: 1rem;
        border-radius: 8px;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
    }
    .metric-card {
        text-align: center;
        padding: 1rem;
        border-radius: 8px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .question-card {
        padding: 1.5rem;
        border-radius: 8px;
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ==================== Database Connection ====================

def init_mongodb():
    """Initialize MongoDB connection"""
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        st.error("❌ MONGO_URI not set in environment variables")
        st.stop()
    
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()  # Test connection
        return client
    except Exception as e:
        st.error(f"❌ MongoDB connection failed: {e}")
        st.stop()

def init_gemini():
    """Initialize Gemini model"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ GEMINI_API_KEY not set in environment variables")
        st.stop()
    
    return Gemini(model="gemini-2.5-flash-lite", api_key=api_key)

# Initialize services
mongo_client = init_mongodb()
gemini_model = init_gemini()

# Initialize system components
cert_loader = CertificationPackLoader(mongo_client)
orchestrator = AgentOrchestrator(mongo_client, gemini_model)
memory_system = UnifiedMemorySystem(mongo_client)
embedding_store = EmbeddingStore(mongo_client)
auth_manager = GoogleAuthManager(mongo_client)

# ==================== Session State ====================

def init_session_state():
    """Initialize session state variables"""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "current_cert" not in st.session_state:
        st.session_state.current_cert = None
    
    if "current_quiz" not in st.session_state:
        st.session_state.current_quiz = None
    
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}

init_session_state()

# ==================== Session Persistence ====================

def check_existing_session():
    """Check for existing session in browser storage"""
    # Try to get session from query params (for persistence across refreshes)
    query_params = st.query_params
    session_token = query_params.get("session")
    
    if session_token and not st.session_state.authenticated:
        # Verify session in database
        sessions_coll = mongo_client["campus-plateform"]["sessions"]
        session_doc = sessions_coll.find_one({
            "_id": session_token,
            "expires_at": {"$gt": datetime.now()}
        })
        
        if session_doc:
            # Restore user session
            st.session_state.user_id = session_doc["user_id"]
            st.session_state.user_email = session_doc["user_email"]
            st.session_state.user_name = session_doc["user_name"]
            st.session_state.authenticated = True
            logger.info("session_restored", user_id=session_doc["user_id"])
            
            # Keep session in URL for persistence
            if "page" not in st.query_params:
                st.query_params["page"] = "app"
            
            return True
    
    return False

# Check for existing session
check_existing_session()

# ==================== Authentication ====================

# Check for OAuth callback
query_params = st.query_params
if "code" in query_params and not st.session_state.authenticated:
    # Show loading message
    with st.spinner("🔄 Completing sign in..."):
        try:
            code = query_params["code"]
            logger.info("oauth_callback_received", code_length=len(code))
            
            user_info = auth_manager.handle_callback(code)
            logger.info("oauth_callback_success", user_id=user_info["_id"])
            
            # Store user info in session
            st.session_state.user_id = user_info["_id"]
            st.session_state.user_email = user_info["email"]
            st.session_state.user_name = user_info["name"]
            st.session_state.authenticated = True
            
            # Create persistent session in database
            import hashlib
            from datetime import timedelta
            session_token = hashlib.sha256(f"{user_info['_id']}{datetime.now().isoformat()}".encode()).hexdigest()
            sessions_coll = mongo_client["campus-plateform"]["sessions"]
            sessions_coll.insert_one({
                "_id": session_token,
                "user_id": user_info["_id"],
                "user_email": user_info["email"],
                "user_name": user_info["name"],
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(days=7)
            })
            
            # Add session token and redirect to app page
            st.query_params.clear()
            st.query_params["session"] = session_token
            st.query_params["page"] = "app"
            
            # Store session in browser localStorage via JavaScript
            st.markdown(f"""
            <script>
                localStorage.setItem('ai_cert_prep_session', '{session_token}');
                localStorage.setItem('ai_cert_prep_session_expires', '{(datetime.now() + timedelta(days=7)).isoformat()}');
            </script>
            """, unsafe_allow_html=True)
            
            st.success("✅ Successfully signed in!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Authentication failed: {str(e)}")
            logger.error("oauth_callback_failed", error=str(e), error_type=type(e).__name__)
            
            # Show retry button
            if st.button("Try Again"):
                st.query_params.clear()
                st.rerun()

# Check for page parameter (routing)
page = st.query_params.get("page", "home")

# If not authenticated and trying to access app, redirect to home
if not st.session_state.authenticated and page == "app":
    st.query_params["page"] = "home"
    st.rerun()

# If authenticated and on home page, redirect to app
if st.session_state.authenticated and page == "home":
    st.query_params["page"] = "app"
    st.rerun()

# Show landing page for unauthenticated users
if not st.session_state.authenticated:
    # Hide Streamlit UI elements for full-page landing experience
    st.markdown("""
    <style>
    [data-testid="stHeader"] {
        display: none;
    }
    [data-testid="stSidebar"] {
        display: none;
    }
    [data-testid="stToolbar"] {
        display: none;
    }
    .main {
        padding: 0 !important;
        margin: 0 !important;
    }
    body {
        margin: 0 !important;
        padding: 0 !important;
    }
    @media (min-width: calc(736px + 8rem)) {
        .st-emotion-cache-zy6yx3 {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }
    }
    .st-emotion-cache-zy6yx3 {
        width: 100% !important;
        padding: 0 !important;
        max-width: initial !important;
        min-width: auto !important;
    }
    /* Hide the Streamlit login button */
    button[kind="primary"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add hidden login trigger button (invisible but clickable by JavaScript)
    if st.button("🔐 Continue to App", type="primary", key="hidden_trigger", help="Click to sign in"):
        auth_url = auth_manager.get_google_login_url()
        st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
        st.stop()
    
    # Check localStorage for existing session
    st.markdown("""
    <script>
        const sessionToken = localStorage.getItem('ai_cert_prep_session');
        const expiresAt = localStorage.getItem('ai_cert_prep_session_expires');
        
        if (sessionToken && expiresAt) {
            const now = new Date();
            const expires = new Date(expiresAt);
            
            // If session is still valid, redirect to app with session token
            if (now < expires) {
                window.location.href = '?session=' + sessionToken + '&page=app';
            } else {
                // Clear expired session
                localStorage.removeItem('ai_cert_prep_session');
                localStorage.removeItem('ai_cert_prep_session_expires');
            }
        }
    </script>
    """, unsafe_allow_html=True)
    
    # Load and display the landing page HTML
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Inject JavaScript to trigger Streamlit button
        login_script = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            const loginLinks = document.querySelectorAll('a[href="/auth/login"]');
            loginLinks.forEach(function(link) {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    // Find and click the Streamlit button in parent
                    const buttons = window.parent.document.querySelectorAll('button[kind="primary"]');
                    if (buttons.length > 0) {
                        buttons[0].click();
                    }
                });
            });
        });
        </script>
        """
        
        html_content = html_content.replace('</body>', login_script + '</body>')
        
        # Render the full HTML page
        import streamlit.components.v1 as components
        components.html(html_content, height=3500, scrolling=False)
            
    except FileNotFoundError:
        st.error("Landing page not found. Please ensure index.html exists.")
        # Fallback to simple login
        st.markdown("### Welcome to AI Certification Prep Assistant! 👋")
        if st.button("🔐 Sign in with Google", type="primary"):
            auth_url = auth_manager.get_google_login_url()
            st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
    
    st.stop()

# ==================== Main App ====================

# Header
st.markdown('<div class="main-header">🎯 AI Certification Prep Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Universal AI-Assisted Exam Preparation</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("📚 Navigation")
    
    # User info
    st.divider()
    st.subheader("👤 User Profile")
    st.write(f"**{st.session_state.user_name}**")
    st.caption(st.session_state.user_email)
    
    if st.button("🚪 Sign Out", use_container_width=True):
        # Delete session from database
        session_token = st.query_params.get("session")
        if session_token:
            sessions_coll = mongo_client["campus-plateform"]["sessions"]
            sessions_coll.delete_one({"_id": session_token})
        
        # Clear localStorage
        st.markdown("""
        <script>
            localStorage.removeItem('ai_cert_prep_session');
            localStorage.removeItem('ai_cert_prep_session_expires');
        </script>
        """, unsafe_allow_html=True)
        
        # Clear query params and session state, redirect to home
        st.query_params.clear()
        st.query_params["page"] = "home"
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    st.divider()
    
    # Quick stats
    user_state = memory_system.get_user_state(st.session_state.user_id)
    st.metric("Recent Activities", len(user_state.get("recent_activity", [])))
    st.metric("Weak Topics", len(user_state.get("weak_concepts", [])))
    st.metric("Due Reviews", len(user_state.get("due_reviews", [])))
    
    st.divider()
    
    # Links
    st.page_link("pages/1_📊_Monitoring_Dashboard.py", label="📊 Monitoring Dashboard")
    
    st.divider()
    
    # System status
    st.caption("🟢 All agents operational")
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

# ==================== Main Content ====================

# Certification Selection
st.header("1️⃣ Select Certification")

available_certs = get_available_certifications_simple()
cert_options = list(available_certs.keys())

selected_cert_id = st.selectbox(
    "Choose your certification",
    options=cert_options,
    format_func=lambda x: available_certs[x],
    key="cert_selector"
)

if selected_cert_id:
    # Load certification pack
    cert_pack = cert_loader.get_pack(selected_cert_id)
    
    if cert_pack:
        # Display cert info
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Questions", cert_pack["blueprint"]["total_questions"])
        
        with col2:
            st.metric("Duration", f"{cert_pack['blueprint']['duration_minutes']} min")
        
        with col3:
            st.metric("Passing Score", f"{cert_pack['blueprint']['passing_score']}%")
        
        with col4:
            st.metric("Level", cert_pack["level"])
        
        # Store in session
        st.session_state.current_cert = cert_pack
        
        st.divider()
        
        # Topic Selection
        st.header("2️⃣ Select Topics")
        
        topics = cert_pack["topics"]
        selected_topics = st.multiselect(
            "Choose topics to focus on",
            options=topics,
            default=topics[:3] if len(topics) >= 3 else topics,
            help="Select the areas you want to practice"
        )
        
        if selected_topics:
            st.success(f"✅ {len(selected_topics)} topics selected")
            
            # Exams Configuration
            st.header("3️⃣ Exams Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                num_questions = st.slider(
                    "Number of questions",
                    min_value=5,
                    max_value=20,
                    value=10,
                    step=5
                )
            
            with col2:
                difficulty = st.select_slider(
                    "Difficulty",
                    options=["easy", "medium", "hard"],
                    value="medium",
                    help="Adaptive: System will adjust based on your performance"
                )
            
            # Exam Instructions
            st.info("""
            **📋 Exam Instructions**
            
            - **Question Format**: Multiple choice questions with one or more correct answers
            - **Code Snippets**: Some questions include code examples - analyze carefully
            - **Timer**: Countdown timer based on official exam duration (practice mode allows submission after time)
            - **Scoring**: Each question is worth equal points
            - **Navigation**: Answer all questions before submitting
            - **Review**: Detailed explanations provided after submission
            - **Performance**: Your results will be saved and used to personalize future exams
            
            ✅ **Ready to begin? Click the button below to generate your personalized exam.**
            """)
            
            # Generate Exam Questions Button
            if not st.session_state.quiz_started:
                if st.button("🚀 Generate Exam Questions", type="primary", use_container_width=True):
                    try:
                        with st.spinner("📚 Content Curator is fetching study materials..."):
                            # Step 1: Use Content Curator Agent to fetch materials
                            materials_result = asyncio.run(orchestrator.process_user_request(
                                user_id=st.session_state.user_id,
                                cert_id=selected_cert_id,
                                request_type="fetch_materials",
                                params={
                                    "topics": selected_topics
                                }
                            ))
                            
                            # Store curated materials in memory for context
                            if materials_result["success"]:
                                memory_system.store_episode(
                                    user_id=st.session_state.user_id,
                                    event_type="materials_fetched",
                                    data={
                                        "cert_id": selected_cert_id,
                                        "topics": selected_topics,
                                        "materials_count": materials_result["data"].get("materials_count", 0)
                                    }
                                )
                        
                        with st.spinner("🎯 Assessment Engine is generating personalized questions..."):
                            # Step 2: Use Assessment Engine Agent to generate questions
                            result = asyncio.run(orchestrator.process_user_request(
                                user_id=st.session_state.user_id,
                                cert_id=selected_cert_id,
                                request_type="generate_quiz",
                                params={
                                    "topics": selected_topics,
                                    "num_questions": num_questions,
                                    "difficulty": difficulty
                                }
                            ))
                            
                            if result["success"]:
                                st.session_state.current_quiz = result["data"]
                                st.session_state.quiz_started = True
                                st.session_state.user_answers = {}
                                st.session_state.quiz_submitted = False
                                
                                # Store in memory
                                memory_system.store_episode(
                                    user_id=st.session_state.user_id,
                                    event_type="quiz_started",
                                    data={
                                        "cert_id": selected_cert_id,
                                        "topics": selected_topics,
                                        "num_questions": num_questions,
                                        "difficulty": difficulty
                                    }
                                )
                                
                                st.rerun()
                            else:
                                st.error(f"❌ Failed to generate quiz: {result.get('error', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        logger.error("quiz_generation_failed", error=str(e))
            
            # Display Exam
            if st.session_state.quiz_started and st.session_state.current_quiz:
                st.divider()
                
                # Initialize exam start time
                if 'exam_start_time' not in st.session_state:
                    st.session_state.exam_start_time = datetime.now().isoformat()
                
                # Calculate exam duration from blueprint
                exam_duration_minutes = cert_pack.get('blueprint', {}).get('duration_minutes', 90)
                
                # Client-side timer (JavaScript)
                st.markdown(f"""
                <div style="position: sticky; top: 0; z-index: 999; background: white; padding: 10px; border-bottom: 2px solid #e0e0e0; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h2>4️⃣ Take Your Exam</h2>
                        <div id="timer" style="font-size: 24px; font-weight: bold; color: #667eea; padding: 10px 20px; background: #f0f2f6; border-radius: 8px;">
                            <span id="timer-display">⏱️ {exam_duration_minutes}:00</span>
                        </div>
                    </div>
                </div>
                <script>
                    // Timer implementation (client-side, no Streamlit rerenders)
                    const examStartTime = new Date("{st.session_state.exam_start_time}");
                    const durationMinutes = {exam_duration_minutes};
                    const durationMs = durationMinutes * 60 * 1000;
                    
                    function updateTimer() {{
                        const now = new Date();
                        const elapsed = now - examStartTime;
                        const remaining = Math.max(0, durationMs - elapsed);
                        
                        const minutes = Math.floor(remaining / 60000);
                        const seconds = Math.floor((remaining % 60000) / 1000);
                        
                        const display = document.getElementById('timer-display');
                        if (display) {{
                            const timeStr = minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');
                            
                            // Color coding
                            if (remaining === 0) {{
                                display.innerHTML = '⏰ TIME UP!';
                                display.style.color = '#ff0000';
                                display.style.animation = 'blink 1s infinite';
                                clearInterval(timerInterval);
                            }} else if (remaining < 5 * 60 * 1000) {{
                                display.innerHTML = '⏱️ ' + timeStr;
                                display.style.color = '#ff6b6b';
                            }} else if (remaining < 15 * 60 * 1000) {{
                                display.innerHTML = '⏱️ ' + timeStr;
                                display.style.color = '#ffa500';
                            }} else {{
                                display.innerHTML = '⏱️ ' + timeStr;
                                display.style.color = '#667eea';
                            }}
                        }}
                    }}
                    
                    // Update timer every second
                    updateTimer();
                    const timerInterval = setInterval(updateTimer, 1000);
                    
                    // Blink animation for time up
                    const style = document.createElement('style');
                    style.textContent = '@keyframes blink {{ 0%, 50% {{ opacity: 1; }} 25%, 75% {{ opacity: 0.3; }} }}';
                    document.head.appendChild(style);
                </script>
                """, unsafe_allow_html=True)
                
                questions = st.session_state.current_quiz.get("questions", [])
                
                if not questions:
                    st.warning("No questions were generated. Please try again.")
                else:
                    # Exam Info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Certification", cert_pack["name"])
                    with col2:
                        st.metric("Questions", len(questions))
                    with col3:
                        st.metric("Difficulty", difficulty.title())
                    
                    st.info(f"**Topics**: {', '.join(selected_topics)}")
                    
                    st.warning("""
                    **⚠️ Before You Begin:**
                    - Read each question carefully
                    - For code questions, analyze the syntax and logic
                    - Some questions may have multiple correct answers
                    - Select ALL correct options when applicable
                    - You can review and change answers before submitting
                    - Timer is for practice - submission allowed after time expires
                    """)
                    
                    st.divider()
                    
                    # Exam form
                    for idx, question in enumerate(questions):
                        st.markdown(f'<div class="question-card">', unsafe_allow_html=True)
                        
                        st.subheader(f"Question {idx + 1}")
                        st.write(question.get("question", ""))
                        
                        # Display code if present
                        if "code" in question:
                            code_language = question.get("language", "python")
                            st.code(question["code"], language=code_language)
                        
                        # Answer options
                        question_type = question.get("type", "mcq")
                        options = question.get("options", [])
                        
                        if question_type == "mcq":
                            answer = st.radio(
                                "Select your answer:",
                                options=options,
                                key=f"q_{idx}",
                                disabled=st.session_state.quiz_submitted
                            )
                            if answer:
                                st.session_state.user_answers[idx] = [answer]
                        
                        else:  # msq
                            answers = st.multiselect(
                                "Select ALL correct answers:",
                                options=options,
                                key=f"q_{idx}",
                                disabled=st.session_state.quiz_submitted
                            )
                            if answers:
                                st.session_state.user_answers[idx] = answers
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Submit exams responses
                    if not st.session_state.quiz_submitted:
                        col1, col2, col3 = st.columns([1, 1, 1])
                        
                        with col2:
                            if st.button("📝 Submit Answers", type="primary", use_container_width=True):
                                if len(st.session_state.user_answers) < len(questions):
                                    st.warning("⚠️ Please answer all questions before submitting.")
                                else:
                                    # Grade quiz
                                    correct_count = 0
                                    results = []
                                    
                                    for idx, question in enumerate(questions):
                                        user_answer = st.session_state.user_answers.get(idx, [])
                                        correct_answer = question.get("correct_answer", [])
                                        
                                        if isinstance(correct_answer, str):
                                            correct_answer = [correct_answer]
                                        
                                        # Extract just the letter (A, B, C, D) from answers
                                        def extract_letter(answer):
                                            if isinstance(answer, list):
                                                return [a.split(')')[0].strip() if ')' in a else a.strip() for a in answer]
                                            else:
                                                return answer.split(')')[0].strip() if ')' in answer else answer.strip()
                                        
                                        user_letters = extract_letter(user_answer)
                                        correct_letters = extract_letter(correct_answer)
                                        
                                        is_correct = set(user_letters) == set(correct_letters)
                                        
                                        if is_correct:
                                            correct_count += 1
                                        
                                        results.append({
                                            "question": question["question"],
                                            "user_answer": user_answer,
                                            "correct_answer": correct_answer,
                                            "is_correct": is_correct,
                                            "explanation": question.get("explanation", ""),
                                            "topic": question.get("topic", "general")
                                        })
                                    
                                    score = correct_count / len(questions)
                                    
                                    # Calculate actual duration
                                    exam_start = datetime.fromisoformat(st.session_state.exam_start_time)
                                    duration_minutes = (datetime.now() - exam_start).total_seconds() / 60
                                    
                                    # Store results
                                    db = mongo_client["campus-plateform"]
                                    db["scores"].insert_one({
                                        "user_id": st.session_state.user_id,
                                        "cert_id": selected_cert_id,
                                        "score": score,
                                        "correct": correct_count,
                                        "total": len(questions),
                                        "difficulty": difficulty,
                                        "topics": selected_topics,
                                        "answers": results,
                                        "duration_minutes": round(duration_minutes, 2),
                                        "submitted_at": datetime.now()
                                    })
                                    
                                    # Store in memory
                                    memory_system.store_episode(
                                        user_id=st.session_state.user_id,
                                        event_type="quiz_attempt",
                                        data={
                                            "cert_id": selected_cert_id,
                                            "score": score,
                                            "difficulty": difficulty,
                                            "topics": selected_topics,
                                            "duration_minutes": round(duration_minutes, 2)
                                        }
                                    )
                                    
                                    st.session_state.quiz_submitted = True
                                    st.session_state.quiz_results = results
                                    st.session_state.quiz_score = score
                                    st.rerun()
                    
                    # Show Results
                    if st.session_state.quiz_submitted:
                        st.divider()
                        st.header("5️⃣ Results & Coaching")
                        
                        score = st.session_state.quiz_score
                        results = st.session_state.quiz_results
                        
                        # Score display
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Your Score", f"{score * 100:.1f}%")
                        
                        with col2:
                            correct = sum(1 for r in results if r["is_correct"])
                            st.metric("Correct Answers", f"{correct}/{len(results)}")
                        
                        with col3:
                            passing_score = cert_pack["blueprint"]["passing_score"]
                            status = "✅ PASS" if score * 100 >= passing_score else "❌ FAIL"
                            st.metric("Status", status)
                        
                        # Get coaching from Learning Coach Agent
                        with st.spinner("🤖 Learning Coach is analyzing your performance..."):
                            coaching_result = asyncio.run(orchestrator.process_user_request(
                                user_id=st.session_state.user_id,
                                cert_id=selected_cert_id,
                                request_type="get_coaching",
                                params={}
                            ))
                            
                            if coaching_result["success"]:
                                coaching = coaching_result["data"]
                                
                                st.subheader("📊 Performance Analysis")
                                st.info(coaching.get("coaching_advice", "Keep practicing!"))
                                
                                # Weak topics
                                weak_topics = coaching.get("weak_topics", [])
                                if weak_topics:
                                    st.warning(f"**Focus areas:** {', '.join(weak_topics)}")
                        
                        # Detailed Results
                        with st.expander("📋 View Detailed Results"):
                            for idx, result in enumerate(results):
                                st.markdown(f"**Question {idx + 1}:** {result['question']}")
                                
                                # Extract letters for display
                                def get_letter(ans):
                                    return ans.split(')')[0].strip() if ')' in ans else ans.strip()
                                
                                user_letters = [get_letter(a) for a in result['user_answer']]
                                correct_letters = [get_letter(a) for a in result['correct_answer']]
                                
                                status_icon = "✅" if result["is_correct"] else "❌"
                                st.write(f"{status_icon} Your answer: {', '.join(user_letters)}")
                                
                                if not result["is_correct"]:
                                    st.write(f"✓ Correct answer: {', '.join(correct_letters)}")
                                
                                st.caption(result.get("explanation", ""))
                                st.divider()
                        
                        # New Quiz Button
                        if st.button("🔄 Take Another Quiz", use_container_width=True):
                            st.session_state.quiz_started = False
                            st.session_state.current_quiz = None
                            st.session_state.quiz_submitted = False
                            st.session_state.user_answers = {}
                            st.rerun()

# Footer
st.divider()
st.caption("🎯 AI Certification Prep Assistant - Built with multi-agent AI architecture • Powered by Google Gemini & MongoDB")
