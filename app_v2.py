"""
CertAgent - Universal Certification Preparation Platform

Multi-agent AI system for certification exam preparation
Supporting 10+ certifications: AWS, Azure, GCP, MongoDB, Terraform, and more

Agents:
- Content Curator Agent: Fetches and organizes study materials
- Assessment Engine Agent: Generates adaptive certification questions
- Learning Coach Agent: Provides personalized recommendations
"""
import os
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import asyncio
from datetime import datetime
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# Import our modules
from auth.google_auth import GoogleAuthManager
from certifications.pack_loader import CertificationPackLoader
from agents.multi_agent import AgentOrchestrator
from memory.embedding_store import UserMemoryStore

# Configure Streamlit page
st.set_page_config(
    page_title="CertAgent - Certification Preparation",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global MongoDB client
_MONGO_CLIENT = None

def get_mongo_client() -> MongoClient:
    """Get MongoDB client with connection pooling"""
    global _MONGO_CLIENT
    
    if _MONGO_CLIENT is None:
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            st.error("❌ MONGO_URI not configured. Please set in .env file.")
            st.stop()
        
        _MONGO_CLIENT = MongoClient(
            mongo_uri,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1
        )
    
    return _MONGO_CLIENT


def initialize_session_state():
    """Initialize session state variables"""
    if "current_quiz" not in st.session_state:
        st.session_state.current_quiz = None
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = {}
    if "selected_certification" not in st.session_state:
        st.session_state.selected_certification = None


def render_home_page(auth_manager: GoogleAuthManager, pack_loader: CertificationPackLoader):
    """Render the home page with certification selection"""
    
    st.title("🎓 CertAgent - Universal Certification Preparation")
    
    st.markdown("""
    ### Welcome to CertAgent!
    
    Prepare for multiple certifications with our **Multi-Agent AI System**:
    
    - 🤖 **Content Curator Agent**: Fetches relevant study materials
    - 📝 **Assessment Engine Agent**: Generates adaptive certification-grade questions
    - 🎯 **Learning Coach Agent**: Provides personalized study recommendations
    
    ---
    """)
    
    # Get available certifications
    packs = pack_loader.list_available_packs()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📚 Available Certifications")
        
        # Display certification cards
        for i in range(0, len(packs), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(packs):
                    pack_info = packs[i + j]
                    pack = pack_loader.get_pack(pack_info['id'])
                    
                    with col:
                        with st.container():
                            st.markdown(f"### {pack.display_name}")
                            st.markdown(f"**Questions:** {pack.total_questions}")
                            st.markdown(f"**Duration:** {pack.duration_minutes} min")
                            st.markdown(f"**Passing Score:** {pack.passing_score}%")
                            
                            if st.button(f"Start Preparing", key=f"btn_{pack.id}"):
                                st.session_state.selected_certification = pack.id
                                st.rerun()
    
    with col2:
        st.subheader("📊 Your Progress")
        
        # Get user statistics
        user_id = st.session_state.user_id
        memory_store = UserMemoryStore(get_mongo_client())
        
        # Get history for all certifications
        history = memory_store.get_user_history(user_id, limit=10)
        
        if history:
            st.metric("Total Sessions", len(history))
            
            # Show recent activity
            st.markdown("**Recent Activity:**")
            for event in history[:5]:
                cert_id = event.get("certification_id", "Unknown")
                timestamp = event.get("timestamp", datetime.now())
                st.caption(f"• {cert_id} - {timestamp.strftime('%b %d, %Y')}")
        else:
            st.info("Start your first quiz to see progress!")


def render_quiz_page(
    pack_loader: CertificationPackLoader,
    orchestrator: AgentOrchestrator,
    user_id: str
):
    """Render quiz generation and taking page"""
    
    cert_id = st.session_state.selected_certification
    pack = pack_loader.get_pack(cert_id)
    
    if not pack:
        st.error("Certification not found")
        return
    
    st.title(f"📝 {pack.display_name}")
    
    # Back button
    if st.button("← Back to Certifications"):
        st.session_state.selected_certification = None
        st.session_state.current_quiz = None
        st.rerun()
    
    st.markdown("---")
    
    # If no quiz generated yet, show configuration
    if st.session_state.current_quiz is None:
        render_quiz_configuration(pack, orchestrator, user_id)
    else:
        render_quiz_taking(pack, user_id)


def render_quiz_configuration(pack, orchestrator: AgentOrchestrator, user_id: str):
    """Render quiz configuration form"""
    
    st.subheader("🎯 Configure Your Practice Session")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Select Topics:**")
        selected_topics = st.multiselect(
            "Choose topics to focus on",
            options=pack.topics,
            default=pack.topics[:3] if len(pack.topics) >= 3 else pack.topics,
            key="selected_topics"
        )
        
        num_questions = st.slider(
            "Number of Questions",
            min_value=5,
            max_value=min(50, pack.total_questions),
            value=10,
            step=5,
            key="num_questions"
        )
    
    with col2:
        difficulty = st.select_slider(
            "Difficulty Level",
            options=["easy", "medium", "hard"],
            value="medium",
            key="difficulty"
        )
        
        st.info(f"""
        **Note:** Our Learning Coach Agent may adjust difficulty 
        based on your performance history to optimize your learning.
        """)
    
    st.markdown("---")
    
    # Generate quiz button
    if st.button("🚀 Generate Practice Questions", type="primary", use_container_width=True):
        if not selected_topics:
            st.error("Please select at least one topic")
            return
        
        with st.spinner("🤖 Our agents are working..."):
            status_placeholder = st.empty()
            
            try:
                # Show agent activity
                status_placeholder.info("📚 Content Curator Agent: Fetching study materials...")
                
                # Generate quiz using orchestrator
                result = asyncio.run(
                    orchestrator.generate_quiz(
                        user_id=user_id,
                        certification_id=pack.id,
                        topics=selected_topics,
                        num_questions=num_questions,
                        difficulty=difficulty
                    )
                )
                
                if result['success']:
                    status_placeholder.success("✅ Questions generated successfully!")
                    
                    # Store quiz in session state
                    st.session_state.current_quiz = {
                        "certification_id": pack.id,
                        "certification_name": pack.display_name,
                        "questions": result['questions'],
                        "difficulty": result['final_difficulty'],
                        "topics": selected_topics,
                        "started_at": datetime.now()
                    }
                    st.session_state.quiz_submitted = False
                    st.session_state.user_answers = {}
                    
                    # Show difficulty adjustment notification
                    if result['difficulty_adjusted']:
                        st.info(f"""
                        🎯 **Learning Coach Adjustment:**
                        Difficulty changed from {result['original_difficulty']} 
                        to {result['final_difficulty']} based on your performance history.
                        """)
                    
                    st.rerun()
                else:
                    status_placeholder.error("❌ Failed to generate questions")
            
            except Exception as e:
                status_placeholder.error(f"❌ Error: {str(e)}")


def render_quiz_taking(pack, user_id: str):
    """Render quiz questions and answer collection"""
    
    quiz = st.session_state.current_quiz
    questions = quiz['questions']
    
    if st.session_state.quiz_submitted:
        render_quiz_results(pack, user_id)
        return
    
    st.subheader(f"📝 Practice Questions ({len(questions)} questions)")
    st.caption(f"Difficulty: {quiz['difficulty'].title()} | Topics: {', '.join(quiz['topics'])}")
    
    st.markdown("---")
    
    # Display questions
    for idx, question in enumerate(questions):
        st.markdown(f"### Question {idx + 1}")
        st.markdown(question['question'])
        
        if question['type'] == 'mcq':
            answer = st.radio(
                "Select one answer:",
                options=question['options'],
                key=f"q_{idx}",
                index=None
            )
            st.session_state.user_answers[idx] = [answer] if answer else []
        
        else:  # msq
            answers = st.multiselect(
                "Select ALL that apply:",
                options=question['options'],
                key=f"q_{idx}"
            )
            st.session_state.user_answers[idx] = answers
        
        st.markdown("---")
    
    # Submit button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📤 Submit Answers", type="primary", use_container_width=True):
            # Check all questions answered
            unanswered = []
            for idx in range(len(questions)):
                if idx not in st.session_state.user_answers or not st.session_state.user_answers[idx]:
                    unanswered.append(idx + 1)
            
            if unanswered:
                st.error(f"Please answer all questions. Unanswered: {', '.join(map(str, unanswered))}")
            else:
                st.session_state.quiz_submitted = True
                st.rerun()


def render_quiz_results(pack, user_id: str):
    """Render quiz results and analysis"""
    
    quiz = st.session_state.current_quiz
    questions = quiz['questions']
    user_answers = st.session_state.user_answers
    
    # Calculate score
    correct_count = 0
    total_questions = len(questions)
    
    results = []
    for idx, question in enumerate(questions):
        user_ans = user_answers.get(idx, [])
        correct_ans = question['correct_answer']
        
        # Normalize answers for comparison
        user_ans_normalized = [a.split(')')[0] if ')' in a else a for a in user_ans]
        correct_ans_normalized = [a.split(')')[0] if ')' in a else a for a in correct_ans]
        
        is_correct = set(user_ans_normalized) == set(correct_ans_normalized)
        if is_correct:
            correct_count += 1
        
        results.append({
            "question_num": idx + 1,
            "correct": is_correct,
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "explanation": question.get('explanation', '')
        })
    
    score_percentage = (correct_count / total_questions) * 100
    
    # Display score
    st.success(f"""
    ### 🎉 Quiz Complete!
    
    **Score: {correct_count}/{total_questions} ({score_percentage:.1f}%)**
    """)
    
    # Pass/Fail indicator
    if score_percentage >= pack.passing_score:
        st.balloons()
        st.success(f"✅ **PASS** - You exceeded the passing score of {pack.passing_score}%!")
    else:
        st.warning(f"⚠️ Keep practicing! Passing score is {pack.passing_score}%")
    
    # Store results in memory
    memory_store = UserMemoryStore(get_mongo_client())
    memory_store.store_episodic_memory(
        user_id=user_id,
        certification_id=quiz['certification_id'],
        event_type="quiz_completed",
        data={
            "score": score_percentage,
            "correct": correct_count,
            "total": total_questions,
            "difficulty": quiz['difficulty'],
            "topics": quiz['topics'],
            "results": results
        }
    )
    
    st.markdown("---")
    
    # Show detailed results
    with st.expander("📊 Detailed Results", expanded=True):
        for result in results:
            if result['correct']:
                st.success(f"✅ **Question {result['question_num']}** - Correct")
            else:
                st.error(f"❌ **Question {result['question_num']}** - Incorrect")
                st.markdown(f"**Your answer:** {', '.join(result['user_answer'])}")
                st.markdown(f"**Correct answer:** {', '.join(result['correct_answer'])}")
            
            if result['explanation']:
                st.info(f"💡 {result['explanation']}")
            
            st.markdown("---")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Try Again", use_container_width=True):
            st.session_state.current_quiz = None
            st.session_state.quiz_submitted = False
            st.rerun()
    
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.selected_certification = None
            st.session_state.current_quiz = None
            st.rerun()


def main():
    """Main application entry point"""
    
    # Initialize session state
    initialize_session_state()
    
    # Get MongoDB client
    mongo_client = get_mongo_client()
    
    # Initialize managers
    auth_manager = GoogleAuthManager(mongo_client)
    pack_loader = CertificationPackLoader(mongo_client)
    
    # Check authentication
    if not auth_manager.require_authentication():
        return
    
    # Render user profile in sidebar
    auth_manager.render_user_profile()
    
    # Get user ID
    user_id = st.session_state.user_id
    
    # Initialize agent orchestrator
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        st.error("❌ GEMINI_API_KEY not configured")
        st.stop()
    
    orchestrator = AgentOrchestrator(mongo_client, gemini_api_key)
    
    # Sidebar navigation
    st.sidebar.markdown("---")
    st.sidebar.title("📚 Navigation")
    
    page = st.sidebar.radio(
        "Go to",
        ["🏠 Home", "📊 My Progress", "⚙️ Settings"],
        key="navigation"
    )
    
    # Render appropriate page
    if page == "🏠 Home":
        if st.session_state.selected_certification:
            render_quiz_page(pack_loader, orchestrator, user_id)
        else:
            render_home_page(auth_manager, pack_loader)
    
    elif page == "📊 My Progress":
        st.title("📊 My Progress")
        st.info("Progress tracking coming soon!")
    
    elif page == "⚙️ Settings":
        st.title("⚙️ Settings")
        st.info("Settings coming soon!")


if __name__ == "__main__":
    main()
