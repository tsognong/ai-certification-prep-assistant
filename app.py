"""
CertAgent - AI-Assisted Certification Preparation

Intelligent multi-agent system for personalized certification exam preparation.
Supports: MongoDB, AWS, Azure, GCP, Terraform, and more.
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
    page_title="CertAgent - AI-Assisted Certification Prep",
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

@st.cache_resource
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

@st.cache_resource
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
            
            # Add session token to URL for persistence
            st.query_params.clear()
            st.query_params["session"] = session_token
            st.success("✅ Successfully signed in!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Authentication failed: {str(e)}")
            logger.error("oauth_callback_failed", error=str(e), error_type=type(e).__name__)
            
            # Show retry button
            if st.button("Try Again"):
                st.query_params.clear()
                st.rerun()

# If not authenticated, show login page
if not st.session_state.authenticated:
    st.markdown('<div class="main-header">🎯 CertAgent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Assisted Certification Preparation</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Welcome message
    st.markdown("""
    ### Welcome to CertAgent! 👋
    
    Your AI-assisted certification preparation platform with:
    - **Multi-Agent System**: Content Curator, Assessment Engine, and Learning Coach
    - **Multiple Certifications**: MongoDB, AWS, Azure, GCP, Terraform, and more
    - **Personalized Learning**: Adaptive questions based on your performance
    - **Memory System**: Tracks your progress and weak areas
    - **Real-time Monitoring**: Observable agent interactions
    
    Sign in with Google to get started!
    """)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🔐 Sign in with Google", type="primary", use_container_width=True):
            auth_url = auth_manager.get_google_login_url()
            st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
            st.markdown(f"[Click here if not redirected]({auth_url})")
    
    st.stop()

# ==================== Main App ====================

# Header
st.markdown('<div class="main-header">🎯 CertAgent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Assisted Certification Preparation</div>', unsafe_allow_html=True)

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
        
        # Clear query params and session state
        st.query_params.clear()
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
            
            # Quiz Configuration
            st.header("3️⃣ Quiz Configuration")
            
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
            - **Time**: No time limit for practice mode (timed mode coming soon)
            - **Scoring**: Each question is worth equal points
            - **Navigation**: Answer all questions before submitting
            - **Review**: Detailed explanations provided after submission
            - **Performance**: Your results will be saved and used to personalize future exams
            
            ✅ **Ready to begin? Click the button below to generate your personalized exam.**
            """)
            
            # Generate Exam Questions Button
            if not st.session_state.quiz_started:
                if st.button("🚀 Generate Exam Questions", type="primary", use_container_width=True):
                    with st.spinner("🤖 Agents are preparing your personalized quiz..."):
                        try:
                            # Use Assessment Engine Agent
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
                st.header("4️⃣ Take Your Exam")
                
                questions = st.session_state.current_quiz.get("questions", [])
                
                if not questions:
                    st.warning("No questions were generated. Please try again.")
                else:
                    # Exam Header
                    st.markdown(f"""
                    **Certification**: {selected_cert["name"]}  
                    **Topics**: {", ".join(selected_topics)}  
                    **Questions**: {len(questions)}  
                    **Difficulty**: {difficulty.title()}
                    """)
                    
                    st.warning("""
                    **⚠️ Before You Begin:**
                    - Read each question carefully
                    - For code questions, analyze the syntax and logic
                    - Some questions may have multiple correct answers
                    - Select ALL correct options when applicable
                    - You can review and change answers before submitting
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
                    
                    # Submit Quiz
                    if not st.session_state.quiz_submitted:
                        col1, col2, col3 = st.columns([1, 1, 1])
                        
                        with col2:
                            if st.button("📝 Submit Quiz", type="primary", use_container_width=True):
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
                                            "duration_minutes": 0  # TODO: Add timer
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
st.caption("🎯 CertAgent - Built with multi-agent AI architecture • Powered by Google Gemini & MongoDB")
