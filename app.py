"""
AI-powered Course Quiz Streamlit App

Features:
- Reads all .txt files from ./data and combines them as the context for quiz generation.
- Uses Google's Generative AI (Gemini) to generate quizzes (JSON output expected).
- Stores generated quizzes and scores in MongoDB Atlas (via MONGO_URI env var).
- Streamlit frontend: nickname, topics (comma-separated), difficulty, quiz display, submit, review.

Run:
1) pip install -r requirements.txt
2) export GEMINI_API_KEY="..."
3) export MONGO_URI="..."
4) streamlit run app.py
"""
import os
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio

import streamlit as st
import streamlit.components.v1 as components
from pymongo import MongoClient
from google.adk.agents import Agent, LlmAgent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.models.google_llm import Gemini
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools.tool_context import ToolContext
from google.genai import types
import hashlib

# Import MongoDB quiz modules
from mongo_fetcher import fetch_docs_for_topics, get_available_mongo_topics, format_docs_for_context
from exam_loader import load_exam_guide, get_exam_info, extract_requirements
from mongo_question_generator import (
    create_mongo_question_prompt,
    validate_mongo_questions,
    grade_mongo_quiz
)

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

# Global session service - will be initialized with MongoDB connection
GLOBAL_SESSION_SERVICE = None

# ------------------------- Configuration / Constants -------------------------
DATA_DIR = Path(__file__).parent.joinpath("data/ai")
MONGO_EXAM_GUIDE = Path(__file__).parent.joinpath("data/mongo/mongo-developer-exam-guide.txt")
DEFAULT_NUM_QUESTIONS = 5
QUIZZES_COLL = "quizzes"
SCORES_COLL = "scores"
USERS_COLL = "users"
SESSIONS_COLL = "agent_sessions"
MAX_RETAKES = 5

# Quiz types
QUIZ_TYPE_AI_COURSE = "AI Agent Course"
QUIZ_TYPE_MONGO_EXAM = "MongoDB Developer Associate Exam"

# Curated list of topics from the Gen AI course materials
AVAILABLE_TOPICS = [
    "AI Agents",
    "Agent Architecture",
    "Agentic Problem-Solving",
    "Core Reasoning Systems",
    "Agent Quality",
    "Connected Problem-Solvers",
    "Strategic Problem-Solving",
    "Multi-Agent Systems",
    "Self-Evolving Systems",
    "Model Context Protocol (MCP)",
    "Tool Calling",
    "Function Calling",
    "Agent Tools",
    "Built-in Tools",
    "MCP Servers and Clients",
    "JSON-RPC",
    "Context Engineering",
    "Sessions",
    "Memory Systems",
    "Memory Types",
    "Memory Extraction",
    "Multimodal Memory",
    "Long Context Management",
    "Agent Orchestration",
    "Domain Knowledge",
    "Prompting Strategies",
    "Security and Privacy",
    "Ai agent Risk",
    "Production",
    "CI/CD",
    "Deployment"
]


# ------------------------- Utility Functions ---------------------------------
def safe_error_display(error_message: str = "An error occurred. Please try again later."):
    """Display a generic error message without exposing stack traces or credentials."""
    st.error(error_message)


def load_text_corpus(data_dir: Path = DATA_DIR) -> str:
    """Read all .txt files in the data directory and return combined text.

    Returns empty string if no files found.
    """
    parts = []
    if not data_dir.exists():
        return ""
    for p in sorted(data_dir.glob("*.txt")):
        try:
            parts.append(p.read_text(encoding="utf-8"))
        except Exception:
            # Skip bad files silently
            continue
    return "\n\n".join(parts)


# Global MongoDB client for connection pooling
_MONGO_CLIENT = None

def get_mongo_db() -> Any:
    """Return a pymongo database object using MONGO_URI env var with connection pooling."""
    global _MONGO_CLIENT
    
    try:
        if _MONGO_CLIENT is None:
            mongo_uri = os.environ.get("MONGO_URI")
            if not mongo_uri:
                raise RuntimeError("Database configuration error")
            # Use connection pooling for better performance
            _MONGO_CLIENT = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=3000,
                maxPoolSize=10,
                minPoolSize=1
            )
        # Use the campus-plateform database
        db_name = "campus-plateform"
        return _MONGO_CLIENT[db_name]
    except Exception:
        raise RuntimeError("Database connection failed")


def get_session_service() -> Any:
    """Get or initialize the global session service with MongoDB persistence."""
    global GLOBAL_SESSION_SERVICE
    
    if GLOBAL_SESSION_SERVICE is not None:
        return GLOBAL_SESSION_SERVICE
    
    # Note: DatabaseSessionService only supports SQL databases (SQLite, PostgreSQL, etc.)
    # For MongoDB, we use InMemorySessionService
    # Session history is maintained in memory during app runtime
    GLOBAL_SESSION_SERVICE = InMemorySessionService()
    print("✅ InMemorySessionService initialized - sessions active during runtime")
    
    return GLOBAL_SESSION_SERVICE


def get_browser_fingerprint() -> str:
    """Get or generate a unique session identifier.
    
    Uses browser characteristics for session persistence.
    """
    # Check if we already have a session ID
    if "session_id" in st.session_state:
        return st.session_state["session_id"]
    
    # Generate and retrieve session ID using browser characteristics
    # The component will return the ID from localStorage or generate a new one
    fingerprint_component = components.html(
        """
        <!DOCTYPE html>
        <html>
        <body>
        <script src="https://cdn.jsdelivr.net/npm/@fingerprintjs/fingerprintjs@3/dist/fp.min.js"></script>
        <script>
            async function getAndReturnId() {
                try {
                    // Try to get from localStorage first
                    let stored = localStorage.getItem('app_session_id');
                    if (stored) {
                        // Return immediately if we have it
                        return stored;
                    }
                    
                    // Generate new fingerprint
                    const fp = await FingerprintJS.load();
                    const result = await fp.get();
                    const id = result.visitorId;
                    
                    // Store in localStorage
                    localStorage.setItem('app_session_id', id);
                    return id;
                } catch (error) {
                    // Fallback: create simple browser signature
                    const fallback = 'S_' + navigator.userAgent.length + '_' + 
                                   screen.width + 'x' + screen.height + '_' +
                                   navigator.language + '_' +
                                   new Date().getTimezoneOffset();
                    localStorage.setItem('app_session_id', fallback);
                    return fallback;
                }
            }
            
            // Get the ID and send it back to Streamlit
            getAndReturnId().then(id => {
                // Method 1: Try Streamlit's setComponentValue
                if (window.parent.streamlitSetComponentValue) {
                    window.parent.streamlitSetComponentValue(id);
                }
                
                // Method 2: Send via postMessage
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: id
                }, '*');
                
                // Method 3: Display in the iframe (Streamlit will read this)
                document.body.innerHTML = '<div id="fp-value" style="display:none;">' + id + '</div>';
            });
        </script>
        </body>
        </html>
        """,
        height=0
    )
    
    # Hash and store the session ID if we got it
    if fingerprint_component and isinstance(fingerprint_component, str) and len(fingerprint_component) > 0:
        session_hash = hashlib.sha256(fingerprint_component.encode('utf-8')).hexdigest()
        st.session_state["session_id"] = session_hash
        return session_hash
    
    # Fallback: Generate a persistent session-based ID (less secure but functional)
    # This happens when the component hasn't loaded yet or can't communicate back
    if "persistent_session_id" not in st.session_state:
        # Create a semi-persistent fallback based on session
        session_id = str(uuid.uuid4())
        st.session_state["persistent_session_id"] = session_id
    
    session_hash = hashlib.sha256(
        st.session_state["persistent_session_id"].encode('utf-8')
    ).hexdigest()
    st.session_state["session_id"] = session_hash
    
    return session_hash


def get_or_create_user(db: Any, nickname: str, session_hash: str) -> Dict[str, Any]:
    """Get or create a user based on session identifier.
    
    Session tracking ensures fair usage policies.
    """
    coll = db[USERS_COLL]
    
    # Find existing user by session hash
    user = coll.find_one({"user_id": session_hash})
    
    if user:
        # Update nickname if it changed
        if user.get("nickname") != nickname:
            coll.update_one(
                {"user_id": session_hash},
                {"$set": {"nickname": nickname, "updated_at": datetime.utcnow()}}
            )
            user["nickname"] = nickname
        return user
    
    # Create new user with session hash as user_id
    new_user = {
        "user_id": session_hash,
        "nickname": nickname,
        "created_at": datetime.utcnow(),
        "quiz_attempts": {}
    }
    coll.insert_one(new_user)
    return new_user


def get_quiz_key(topics: List[str], difficulty: str, quiz_type: str = QUIZ_TYPE_AI_COURSE) -> str:
    """Generate a unique key for a quiz configuration."""
    topics_str = "-".join(sorted(topics)) if topics else "general"
    return f"{quiz_type}_{topics_str}_{difficulty}"


def get_attempt_count(db: Any, user_id: str, quiz_key: str) -> int:
    """Get the number of attempts for a specific quiz."""
    coll = db[USERS_COLL]
    user = coll.find_one({"user_id": user_id})
    if not user:
        return 0
    return user.get("quiz_attempts", {}).get(quiz_key, 0)


def increment_attempt_count(db: Any, user_id: str, quiz_key: str) -> None:
    """Increment the attempt count for a specific quiz."""
    coll = db[USERS_COLL]
    coll.update_one(
        {"user_id": user_id},
        {"$inc": {f"quiz_attempts.{quiz_key}": 1}}
    )


def generate_quiz_with_ai(
    api_key: str,
    user_id: str,
    nickname: str,
    topics: List[str],
    difficulty: str,
    corpus: str,
    num_questions: int = DEFAULT_NUM_QUESTIONS,
) -> List[Dict[str, Any]]:
    """Call Google Generative AI (Gemini) to generate a quiz.

    The function expects the model to return JSON like:
    {"questions": [{"question": "...", "options": ["a","b","c","d"], "correct_index": 2, "explanation": "..."}, ...]}

    If parsing fails, raises a ValueError.
    """
    # Build a clear prompt asking for strict JSON output.
    topics_str = ", ".join(topics) if topics else "general"
    prompt = (
        "You are an expert quiz generator. Using the provided course text, create a multiple-choice quiz. "
        f"Generate {num_questions} questions on the topics: {topics_str}. Difficulty: {difficulty}.\n\n"
        "Constraints:\n"
        "- Output ONLY valid JSON. The top-level object must have a single key `questions` which maps to a list.\n"
        "- Each question object must have: `question` (string), `options` (list of 3-5 strings), "
        "`correct_index` (integer index into options, starting at 0), and `explanation` (string referencing the provided text).\n"
        "- Keep options short (one sentence). Use the text to create distractors.\n"
        "- In the explanation field, ALWAYS include the source document title (found at the beginning of each document in the course text) "
        "followed by the page number or section where the answer can be found. Format: '[Document Title] - Page X' or '[Document Title] - Section: ...'.\n\n"
        "Provide the course text below, delimited by <COURSE_TEXT> tags. When you give explanations, include short references to where in the text the answer comes from.\n\n"
        "<COURSE_TEXT>\n"
        f"{corpus}\n"
        "</COURSE_TEXT>\n\n"
        "Now produce the JSON exactly as stated."
    )

    # Initialize Google ADK Gemini model with correct syntax
    model = Gemini(
        model="gemini-2.5-flash-lite",
        api_key=api_key,
        retry_options=retry_config
    )
    
    # Create the LLM Agent with the Gemini model
    quiz_agent = LlmAgent(
        model=model,
        name="quiz_generator",
        instruction="You are an expert quiz generator that creates multiple-choice quizzes from course text. Always output valid JSON only. Remember previous interactions with the user."
    )
    
    # Use the global session service with MongoDB persistence
    session_service = get_session_service()
    
    # Create the Runner
    runner = Runner(
        agent=quiz_agent,
        app_name="quiz-generator",
        session_service=session_service
    )

    # Generate quiz using the runner (async pattern)
    resp_text = ""
    try:
        # Use async runner to generate content
        async def run_generation():
            # Use consistent session ID based on user_id to maintain history
            session_id = f"user-{user_id}"
            
            # Create or get session
            try:
                session = await session_service.create_session(
                    app_name="quiz-generator",
                    user_id=user_id,
                    session_id=session_id
                )
            except:
                session = await session_service.get_session(
                    app_name="quiz-generator",
                    user_id=user_id,
                    session_id=session_id
                )
            
            # Create message content
            query_content = types.Content(
                role="user",
                parts=[types.Part(text=prompt)]
            )
            
            # Stream agent response
            response_text = ""
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=query_content
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    text = event.content.parts[0].text
                    if text and text != "None":
                        response_text = text
            
            return response_text
        
        # Run async function in event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        resp_text = loop.run_until_complete(run_generation())

    except Exception as e:
        raise RuntimeError(f"AI generation failed: {e}")

    # Extract JSON substring if assistant wrapped it, else try parsing directly
    resp_text = resp_text.strip()
    try:
        data = json.loads(resp_text)
    except Exception:
        # try to find first { ... } block
        start = resp_text.find("{")
        end = resp_text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("AI did not return JSON and no JSON block found in response")
        json_sub = resp_text[start : end + 1]
        try:
            data = json.loads(json_sub)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON from AI response: {e}\nResponse was:\n{resp_text}")

    if "questions" not in data or not isinstance(data["questions"], list):
        raise ValueError("AI JSON did not include 'questions' list")

    # Validate and normalize questions
    questions = []
    for q in data["questions"]:
        if not all(k in q for k in ("question", "options", "correct_index", "explanation")):
            raise ValueError("Each question must include question/options/correct_index/explanation")
        questions.append(
            {
                "question": q["question"].strip(),
                "options": [opt.strip() for opt in q["options"]],
                "correct_index": int(q["correct_index"]),
                "explanation": q["explanation"].strip(),
            }
        )

    return questions


def generate_mongo_quiz_with_ai(
    api_key: str,
    user_id: str,
    nickname: str,
    topics: List[str],
    difficulty: str,
    num_questions: int = DEFAULT_NUM_QUESTIONS,
) -> List[Dict[str, Any]]:
    """Generate MongoDB exam-style quiz using documentation."""
    
    # Fetch MongoDB documentation for selected topics
    docs = fetch_docs_for_topics(topics, max_pages_per_topic=2)
    
    if not docs:
        raise ValueError("Unable to fetch MongoDB documentation")
    
    # Format docs as context
    docs_context = format_docs_for_context(docs)
    
    # Load exam requirements
    exam_guide = load_exam_guide(MONGO_EXAM_GUIDE)
    requirements = extract_requirements(exam_guide.get('content', ''))
    exam_guide_content = exam_guide.get('content', '')
    
    # Create prompt for MongoDB questions
    prompt = create_mongo_question_prompt(
        docs_context=docs_context,
        topics=topics,
        num_questions=num_questions,
        difficulty=difficulty,
        requirements=requirements,
        exam_guide_content=exam_guide_content
    )
    
    # Initialize Gemini model
    model = Gemini(
        model="gemini-2.5-flash-lite",
        api_key=api_key,
        retry_options=retry_config
    )
    
    # Create agent
    mongo_agent = LlmAgent(
        model=model,
        name="mongo_quiz_generator",
        instruction="You are an expert MongoDB certification exam question writer. Generate questions based strictly on official MongoDB documentation. Always output valid JSON only."
    )
    
    # Get session service
    session_service = get_session_service()
    
    # Create runner
    runner = Runner(
        agent=mongo_agent,
        app_name="mongo-quiz-generator",
        session_service=session_service
    )
    
    # Generate quiz
    resp_text = ""
    try:
        async def run_generation():
            session_id = f"user-{user_id}-mongo"
            
            try:
                session = await session_service.create_session(
                    app_name="mongo-quiz-generator",
                    user_id=user_id,
                    session_id=session_id
                )
            except:
                session = await session_service.get_session(
                    app_name="mongo-quiz-generator",
                    user_id=user_id,
                    session_id=session_id
                )
            
            query_content = types.Content(
                role="user",
                parts=[types.Part(text=prompt)]
            )
            
            response_text = ""
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session.id,
                new_message=query_content
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    text = event.content.parts[0].text
                    if text and text != "None":
                        response_text = text
            
            return response_text
        
        # Run async generation
        resp_text = asyncio.run(run_generation())
        
    except Exception as e:
        raise ValueError(f"AI generation failed: {str(e)}")
    
    if not resp_text:
        raise ValueError("No response from AI")
    
    # Parse JSON response
    resp_text = resp_text.strip()
    # Remove markdown code blocks if present
    if resp_text.startswith("```"):
        lines = resp_text.split("\n")
        resp_text = "\n".join(lines[1:-1]) if len(lines) > 2 else resp_text
    
    try:
        data = json.loads(resp_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI returned invalid JSON: {str(e)}")
    
    # Handle both array and object with "questions" key
    if isinstance(data, list):
        questions = data
    elif isinstance(data, dict) and "questions" in data:
        questions = data["questions"]
    else:
        raise ValueError("Unexpected JSON structure")
    
    # Validate MongoDB questions
    validated_questions = validate_mongo_questions(questions)
    
    if not validated_questions:
        raise ValueError("No valid questions generated")
    
    return validated_questions


def get_or_create_quiz(
    db: Any, user_id: str, nickname: str, topics: List[str], difficulty: str, corpus: str, api_key: str, 
    quiz_type: str = QUIZ_TYPE_AI_COURSE, is_full_exam: bool = False
) -> Dict[str, Any]:
    """Return existing quiz for (nickname, topics, difficulty, quiz_type) or generate & store one."""
    coll = db[QUIZZES_COLL]
    query = {"nickname": nickname, "topics": topics, "difficulty": difficulty, "quiz_type": quiz_type, "is_full_exam": is_full_exam}
    doc = coll.find_one(query)
    if doc:
        return doc

    # Determine number of questions
    num_questions = DEFAULT_NUM_QUESTIONS
    if quiz_type == QUIZ_TYPE_MONGO_EXAM and is_full_exam:
        num_questions = 53  # Official MongoDB exam question count
    
    # Generate based on quiz type
    if quiz_type == QUIZ_TYPE_MONGO_EXAM:
        questions = generate_mongo_quiz_with_ai(api_key, user_id, nickname, topics, difficulty, num_questions)
    else:
        # AI course quiz - pass user_id to maintain conversation history
        questions = generate_quiz_with_ai(api_key, user_id, nickname, topics, difficulty, corpus, num_questions)
    
    now = datetime.utcnow()
    quiz_doc = {
        "nickname": nickname,
        "topics": topics,
        "difficulty": difficulty,
        "quiz_type": quiz_type,
        "is_full_exam": is_full_exam,
        "questions": questions,
        "num_questions": len(questions),
        "created_at": now,
    }
    res = coll.insert_one(quiz_doc)
    quiz_doc["_id"] = res.inserted_id
    return quiz_doc


def calculate_score(quiz: Dict[str, Any], user_answers: List[Optional[int]]) -> Dict[str, Any]:
    """Calculate score and return a result dict.

    user_answers: list of indices or None.
    """
    correct = 0
    total = len(quiz["questions"]) if "questions" in quiz else 0
    details = []
    
    for i, q in enumerate(quiz.get("questions", [])):
        correct_idx = int(q["correct_index"])
        ua = user_answers[i] if i < len(user_answers) else None
        is_correct = ua is not None and ua == correct_idx
        if is_correct:
            correct += 1
        details.append({
            "question": q["question"],
            "options": q["options"],
            "correct_index": correct_idx,
            "user_answer": ua,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        })
    
    pct = (correct / total * 100) if total else 0.0
    return {"correct": correct, "total": total, "percent": pct, "details": details}


def save_score(db: Any, user_id: str, nickname: str, quiz_id: Any, score_obj: Dict[str, Any]) -> None:
    coll = db[SCORES_COLL]
    record = {
        "user_id": user_id,
        "nickname": nickname,
        "quiz_id": quiz_id,
        "score": score_obj["correct"],
        "total": score_obj["total"],
        "percent": score_obj["percent"],
        "details": score_obj["details"],
        "taken_at": datetime.utcnow(),
    }
    coll.insert_one(record)


# ------------------------- Streamlit App ------------------------------------
def main():
    st.set_page_config(page_title="5-Day AI Agents Intensive Course Quiz", layout="centered")
    st.title("🤖 5-Day AI Agents Intensive Course Quiz")
    st.caption("📚 Learn and master the course whitepapers through interactive AI-powered quizzes")

    # Load corpus once and cache
    corpus = load_text_corpus()
    if not corpus:
        st.warning("No .txt files found in the `data/` folder. Place pre-converted course text files (e.g., day1.txt) in ./data/")

    # Check environment
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        st.error("GEMINI_API_KEY is not set. Set it in your environment before running the app.")
        # still allow exploring UI but disable generation

    try:
        db = get_mongo_db()
    except Exception:
        safe_error_display("Unable to connect to database. Please try again later.")
        db = None

    # --- Input area ---
    st.header("Start / Resume Quiz")
    
    # Get session identifier
    session_hash = get_browser_fingerprint()
    
    nickname = st.text_input("Enter your nickname:")
    
    # Get or create user
    user = None
    if nickname and db is not None and session_hash:
        try:
            user = get_or_create_user(db, nickname, session_hash)
            st.session_state["current_user"] = user
        except Exception:
            safe_error_display("Unable to initialize user session. Please try again later.")
    
    # Quiz type selection
    st.write("**Select Quiz Type:**")
    quiz_type = st.selectbox(
        "Choose the type of quiz:",
        options=[QUIZ_TYPE_AI_COURSE, QUIZ_TYPE_MONGO_EXAM],
        help="Select 'AI Agent Course' for quizzes on Generative AI topics, or 'MongoDB Developer Associate Exam' for MongoDB certification-style questions."
    )
    
    # Store quiz type in session state
    if "quiz_type" not in st.session_state or st.session_state["quiz_type"] != quiz_type:
        st.session_state["quiz_type"] = quiz_type
        # Clear existing quiz if type changed
        if "current_quiz" in st.session_state:
            st.session_state.pop("current_quiz")
    
    # MongoDB Exam Mode Selection
    is_full_exam = False
    if quiz_type == QUIZ_TYPE_MONGO_EXAM:
        st.write("**MongoDB Exam Mode:**")
        exam_mode = st.radio(
            "Choose exam mode:",
            options=["Practice Mode (Topic-based)", "Full Exam Mode (53 questions, 75 minutes)"],
            help="Practice Mode: Select specific topics. Full Exam Mode: Complete exam with all topics following official syllabus."
        )
        is_full_exam = "Full Exam" in exam_mode
        
        if "exam_mode" not in st.session_state or st.session_state.get("exam_mode") != exam_mode:
            st.session_state["exam_mode"] = exam_mode
            # Clear quiz if mode changed
            if "current_quiz" in st.session_state:
                st.session_state.pop("current_quiz")
    
    # Topic selection based on quiz type
    st.write("**Select topics for your quiz:**")
    
    if quiz_type == QUIZ_TYPE_MONGO_EXAM:
        if is_full_exam:
            # Full exam mode: Use all topics from guide
            try:
                exam_guide = load_exam_guide(MONGO_EXAM_GUIDE)
                mongo_topics = extract_topics_from_guide(exam_guide.get('content', ''))
            except:
                mongo_topics = get_available_mongo_topics()
            
            topics = mongo_topics  # Use all topics
            st.info(f"📋 Full Exam Mode: All {len(topics)} topics will be covered (53 questions, 75 minutes)")
            st.caption(f"Topics: {', '.join(topics)}")
        else:
            # Practice mode: Let user select topics
            try:
                exam_guide = load_exam_guide(MONGO_EXAM_GUIDE)
                mongo_topics = extract_topics_from_guide(exam_guide.get('content', ''))
            except:
                mongo_topics = get_available_mongo_topics()
            
            selected_topics = st.multiselect(
                "Choose one or more MongoDB exam topics:",
                options=mongo_topics,
                default=None,
                help="Select MongoDB topics you want to be tested on."
            )
            topics = list(selected_topics) if selected_topics else []
    else:
        # AI course topics
        selected_topics = st.multiselect(
            "Choose one or more topics from the Gen AI course:",
            options=AVAILABLE_TOPICS,
            default=None,
            help="Select the topics you want to be tested on. If none selected, the quiz will cover general topics."
        )
    
        # Allow users to add custom topics for AI course
        custom_topics_input = st.text_input(
            "Or add custom topics (comma-separated):",
            placeholder="e.g., Agent Planning, Retrieval Systems, Tool Integration",
            help="Type additional topics not in the list above, separated by commas"
        )
        
        # Combine selected and custom topics
        topics = list(selected_topics) if selected_topics else []
        if custom_topics_input:
            custom_topics = [t.strip() for t in custom_topics_input.split(",") if t.strip()]
            topics.extend(custom_topics)
    
    # Show combined topics if any
    if topics:
        st.caption(f"📌 Selected topics: {', '.join(topics)}")
    
    difficulty = st.radio("Select difficulty:", ("easy", "medium", "hard"), index=1)
    
    # Check attempt count (optimized to use cached user data)
    quiz_key = get_quiz_key(topics, difficulty, quiz_type)
    attempts_left = MAX_RETAKES  # Default
    current_attempts = 0
    
    if user and db is not None:
        # Use cached user data if available, otherwise fetch
        if "cached_user_attempts" not in st.session_state or st.session_state.get("cache_user_id") != user["user_id"]:
            current_attempts = get_attempt_count(db, user["user_id"], quiz_key)
            st.session_state["cached_user_attempts"] = {quiz_key: current_attempts}
            st.session_state["cache_user_id"] = user["user_id"]
        else:
            current_attempts = st.session_state["cached_user_attempts"].get(quiz_key, 0)
        
        attempts_left = MAX_RETAKES - current_attempts

    start_col, load_col = st.columns(2)
    start_clicked = start_col.button("Start Quiz", disabled=(attempts_left <= 0))
    load_clicked = load_col.button("Load Recent Quiz")

    # Try to load most recent quiz when requested
    if load_clicked and db is not None and user:
        try:
            coll = db[QUIZZES_COLL]
            # Find the most recent quiz for this user (by user_id, not nickname)
            # We need to find quizzes where the nickname matches (since quizzes are stored by nickname)
            # But we should match the current user's data
            recent_quiz = coll.find_one(
                {"nickname": nickname},
                sort=[("created_at", -1)]  # Sort by most recent first
            )
            
            if recent_quiz:
                st.success(f"Loaded most recent quiz: {len(recent_quiz.get('questions', []))} questions on {', '.join(recent_quiz.get('topics', ['general']))} ({recent_quiz.get('difficulty', 'medium')} difficulty)")
                st.session_state["current_quiz"] = recent_quiz
                # initialize answers
                st.session_state["answers"] = [None] * len(recent_quiz.get("questions", []))
                # Clear review and submitted state
                st.session_state["quiz_submitted"] = False
                st.session_state["current_question"] = 0
                st.session_state.pop("last_score", None)
            else:
                st.info("No existing quizzes found. Click 'Start Quiz' to generate a new one.")
        except Exception:
            safe_error_display("Unable to load quiz. Please try again.")

    if start_clicked:
        if not nickname:
            st.warning("Please enter a nickname before starting a quiz.")
        elif db is None:
            st.error("Cannot start quiz without MongoDB connection.")
        elif not user:
            st.error("User session not initialized.")
        else:
            with st.spinner("Generating or retrieving quiz..."):
                try:
                    # Check if this is a new quiz or existing one
                    coll = db[QUIZZES_COLL]
                    existing_quiz = coll.find_one({"nickname": nickname, "topics": topics, "difficulty": difficulty, "quiz_type": quiz_type, "is_full_exam": is_full_exam})
                    
                    quiz_doc = get_or_create_quiz(db, user["user_id"], nickname, topics, difficulty, corpus, gemini_key, quiz_type, is_full_exam)
                    
                    # Increment attempt count and invalidate cache
                    increment_attempt_count(db, user["user_id"], quiz_key)
                    # Invalidate cache to reflect new attempt count
                    if "cached_user_attempts" in st.session_state:
                        st.session_state["cached_user_attempts"][quiz_key] = current_attempts + 1
                    
                    st.session_state["current_quiz"] = quiz_doc
                    st.session_state["answers"] = [None] * len(quiz_doc.get("questions", []))
                    st.session_state["quiz_submitted"] = False
                    st.session_state["current_question"] = 0
                    # Initialize timer for full exam mode
                    if is_full_exam:
                        st.session_state["quiz_start_time"] = time.time()
                        st.session_state["quiz_time_limit"] = 75 * 60  # 75 minutes in seconds
                    else:
                        st.session_state.pop("quiz_start_time", None)
                        st.session_state.pop("quiz_time_limit", None)
                    # Clear any previous review
                    st.session_state.pop("last_score", None)
                    st.success("Quiz ready. Scroll down to take it.")
                except Exception:
                    safe_error_display("Unable to generate quiz. Please try again later.")
                    return

    # Show quiz if present
    quiz = st.session_state.get("current_quiz")
    if quiz:
        # Check if this is a full exam with timer
        is_timed_exam = "quiz_start_time" in st.session_state and "quiz_time_limit" in st.session_state
        
        if is_timed_exam and not st.session_state.get("quiz_submitted", False):
            # Calculate elapsed and remaining time
            start_timestamp = st.session_state["quiz_start_time"]
            time_limit = st.session_state["quiz_time_limit"]
            
            # Client-side JavaScript timer that doesn't cause page refresh
            timer_placeholder = st.empty()
            with timer_placeholder.container():
                timer_col, header_col = st.columns([1, 3])
                with timer_col:
                    components.html(
                        f"""
                        <div id="timer-display">
                            <style>
                                .timer-box {{
                                    padding: 10px;
                                    border-radius: 5px;
                                    text-align: center;
                                    font-family: monospace;
                                    font-size: 18px;
                                    font-weight: bold;
                                }}
                                .timer-green {{ background-color: #d4edda; color: #155724; }}
                                .timer-yellow {{ background-color: #fff3cd; color: #856404; }}
                                .timer-red {{ background-color: #f8d7da; color: #721c24; }}
                            </style>
                            <div id="timer" class="timer-box timer-green">
                                <div id="elapsed">⏱️ 0:00</div>
                                <div id="remaining" style="font-size: 12px; margin-top: 5px;">Remaining: 75:00</div>
                            </div>
                            <script>
                                var startTime = {start_timestamp};
                                var timeLimit = {time_limit};
                                
                                function updateTimer() {{
                                    var now = Date.now() / 1000;
                                    var elapsed = Math.floor(now - startTime);
                                    var remaining = Math.max(0, timeLimit - elapsed);
                                    
                                    var elapsedMins = Math.floor(elapsed / 60);
                                    var elapsedSecs = elapsed % 60;
                                    var remainingMins = Math.floor(remaining / 60);
                                    var remainingSecs = remaining % 60;
                                    
                                    var timerDiv = document.getElementById('timer');
                                    document.getElementById('elapsed').innerHTML = '⏱️ ' + elapsedMins + ':' + (elapsedSecs < 10 ? '0' : '') + elapsedSecs;
                                    document.getElementById('remaining').innerHTML = 'Remaining: ' + remainingMins + ':' + (remainingSecs < 10 ? '0' : '') + remainingSecs;
                                    
                                    if (remaining > 600) {{
                                        timerDiv.className = 'timer-box timer-green';
                                    }} else if (remaining > 300) {{
                                        timerDiv.className = 'timer-box timer-yellow';
                                    }} else {{
                                        timerDiv.className = 'timer-box timer-red';
                                    }}
                                    
                                    if (remaining === 0) {{
                                        alert("⏰ Time's up! Your quiz will be auto-submitted.");
                                        // Set quiz submitted flag and trigger form submission
                                        const submitBtn = window.parent.document.querySelector('[data-testid="stButton"] button[kind="primary"]');
                                        if (submitBtn) {{
                                            submitBtn.click();
                                        }} else {{
                                            window.parent.location.reload();
                                        }}
                                    }}
                                }}
                                
                                updateTimer();
                                setInterval(updateTimer, 1000);
                            </script>
                        </div>
                        """,
                        height=100
                    )
                
                with header_col:
                    st.header("MongoDB Developer Associate Exam (Java)")
        else:
            st.header("Take Quiz")
        
        questions = quiz.get("questions", [])
        answers = st.session_state.get("answers", [None] * len(questions))

        # Initialize current question index
        if "current_question" not in st.session_state:
            st.session_state["current_question"] = 0
        
        current_q_index = st.session_state["current_question"]
        total_questions = len(questions)
        
        # Question navigation slider
        st.write(f"### Question {current_q_index + 1} of {total_questions}")
        
        # Display current question
        q = questions[current_q_index]
        question_type = q.get("type", "mcq")
        st.markdown(f"**{q['question']}**")
        
        opts = q.get("options", [])
        
        # Render based on question type
        if question_type == "msq":
            # Multi-select question: use checkboxes
            st.info("📌 **Select ALL that apply** (multiple correct answers)")
            
            # Get current answer as list
            current_answer = answers[current_q_index]
            if current_answer is None:
                current_answer = []
            elif not isinstance(current_answer, list):
                current_answer = [current_answer]
            
            # Render checkboxes
            selected_indices = []
            for idx, opt in enumerate(opts):
                is_checked = idx in current_answer
                if st.checkbox(
                    opt,
                    value=is_checked,
                    key=f"q_{current_q_index}_opt_{idx}"
                ):
                    selected_indices.append(idx)
            
            # Store list of selected indices
            answers[current_q_index] = selected_indices
        else:
            # Single-choice question: use radio buttons for clear UX
            st.info("📌 **Select ONE answer** (single correct answer)")
            
            # Get current answer
            current_answer = answers[current_q_index]
            if current_answer is None:
                current_answer = 0
            
            # Use radio button for single selection
            choice = st.radio(
                "Choose your answer:",
                options=list(range(len(opts))),
                format_func=lambda x: opts[x],
                key=f"q_{current_q_index}_radio",
                index=current_answer if isinstance(current_answer, int) and 0 <= current_answer < len(opts) else 0
            )
            
            # Store single index
            answers[current_q_index] = int(choice)
        
        # Always update session state
        st.session_state["answers"] = answers
        
        # Submit and Retake buttons
        quiz_submitted = st.session_state.get("quiz_submitted", False)
        
        if not quiz_submitted:
            # Navigation and Submit section
            st.markdown("---")
            
            # Navigation buttons
            nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
            
            with nav_col1:
                if current_q_index > 0:
                    if st.button("⬅️ Previous", key="prev_btn", use_container_width=True):
                        st.session_state["current_question"] = current_q_index - 1
                        st.rerun()
            
            with nav_col2:
                # Progress indicator
                progress = (current_q_index + 1) / total_questions
                st.progress(progress)
                st.caption(f"Question {current_q_index + 1} of {total_questions}")
            
            with nav_col3:
                if current_q_index < total_questions - 1:
                    if st.button("Next ➡️", key="next_btn", use_container_width=True):
                        st.session_state["current_question"] = current_q_index + 1
                        st.rerun()
            
            # Submit button - always visible
            st.markdown("---")
            if st.button("✅ Submit Quiz", type="primary", use_container_width=True, key="submit_btn"):
                try:
                    # Calculate time taken if timed exam
                    time_taken_seconds = None
                    if "quiz_start_time" in st.session_state:
                        time_taken_seconds = int(time.time() - st.session_state["quiz_start_time"])
                    
                    # Grade based on quiz type
                    current_quiz_type = quiz.get("quiz_type", QUIZ_TYPE_AI_COURSE)
                    
                    if current_quiz_type == QUIZ_TYPE_MONGO_EXAM:
                        # Use MongoDB grading for exam questions
                        score_obj = grade_mongo_quiz(questions, answers)
                    else:
                        # Use traditional grading for AI course
                        score_obj = calculate_score(quiz, answers)
                    
                    # Add time taken to score object
                    if time_taken_seconds is not None:
                        score_obj["time_taken_seconds"] = time_taken_seconds
                        score_obj["time_taken_display"] = f"{time_taken_seconds // 60}:{time_taken_seconds % 60:02d}"
                    
                    user = st.session_state.get("current_user")
                    if db is not None and user:
                        save_score(db, user["user_id"], nickname, quiz.get("_id"), score_obj)
                    st.session_state["last_score"] = score_obj
                    st.session_state["quiz_submitted"] = True
                    st.session_state["current_question"] = 0  # Reset to first question
                    
                    # Show result with time if available
                    if time_taken_seconds is not None:
                        st.success(f"You scored {score_obj['correct']} / {score_obj['total']} ({score_obj['percent']:.1f}%) - Time: {score_obj['time_taken_display']}")
                    else:
                        st.success(f"You scored {score_obj['correct']} / {score_obj['total']} ({score_obj['percent']:.1f}%)")
                    st.rerun()
                except Exception as e:
                    safe_error_display(f"Unable to submit quiz: {str(e)}")
        else:
            # Show retake button if attempts left
            user = st.session_state.get("current_user")
            if user and db is not None:
                current_attempt_count = get_attempt_count(db, user["user_id"], quiz_key)
                retakes_left = MAX_RETAKES - current_attempt_count
                
                st.markdown("---")
                col1, col2 = st.columns([1, 3])
                with col1:
                    if retakes_left > 0:
                        if st.button("🔄 Retake Quiz"):
                            # Clear current quiz and score
                            st.session_state.pop("current_quiz", None)
                            st.session_state.pop("last_score", None)
                            st.session_state.pop("answers", None)
                            st.session_state["quiz_submitted"] = False
                            st.session_state["current_question"] = 0
                            st.rerun()
                    else:
                        st.button("🔄 Retake Quiz", disabled=True)
                with col2:
                    if retakes_left > 0:
                        st.info(f"You have **{retakes_left}** retake(s) left for this quiz.")
                    else:
                        st.warning("No retakes left. Try different topics or difficulty.")

    # Show review if available
    if st.session_state.get("last_score"):
        st.header("Review Quiz")
        score_obj = st.session_state["last_score"]
        current_quiz_type = quiz.get("quiz_type", QUIZ_TYPE_AI_COURSE) if quiz else QUIZ_TYPE_AI_COURSE
        
        for i, d in enumerate(score_obj["details"]):
            st.markdown(f"**Q{i+1}. {d['question']}**")
            
            # Check if this is MongoDB exam question (has sources or type field)
            is_mongo_exam = d.get("type") in ["mcq", "msq"] or "sources" in d
            question_type = d.get("type", "mcq")
            
            # Show options with indicators
            for idx, opt in enumerate(d["options"]):
                prefix = ""
                
                if question_type == "msq":
                    # Multi-select question
                    correct_answers = d.get("correct_answers", [])
                    user_answers = d.get("user_answers", [])
                    
                    if idx in correct_answers:
                        prefix = "✅ "
                    if idx in user_answers and idx not in correct_answers:
                        prefix = "❌ "
                else:
                    # Single-choice question
                    if idx == d.get("correct_index"):
                        prefix = "✅ "
                    if d.get("user_answer") is not None and idx == d.get("user_answer") and not d.get("is_correct"):
                        prefix = "❌ "
                
                st.write(f"{prefix}{idx}. {opt}")
            
            # Show answers based on question type
            if question_type == "msq":
                user_answers = d.get("user_answers", [])
                correct_answers = d.get("correct_answers", [])
                st.write(f"**Your answers:** {user_answers} | **Correct:** {correct_answers}")
            else:
                st.write(f"**Your answer:** {d.get('user_answer')} | **Correct:** {d.get('correct_index')}")
            
            # Show explanation
            st.write(f"**Explanation:** {d.get('explanation', 'N/A')}")
            
            # Show sources for MongoDB questions
            if is_mongo_exam and "sources" in d:
                sources = d["sources"]
                if sources:
                    st.caption("**📚 Documentation References:**")
                    for source in sources:
                        st.caption(f"• {source}")
            st.markdown("---")

    # Optional section: list past scores for nickname
    st.sidebar.header("📊 Your Quiz History")
    if user and db is not None:
        # Show current user info
        st.sidebar.write(f"**User:** {nickname}")
        st.sidebar.markdown("---")
        
        # Show score history (limit to 5 most recent)
        try:
            # Ensure we're querying with the current user's ID only
            recs = list(db[SCORES_COLL].find(
                {"user_id": user["user_id"]}  # Explicit filter by current user
            ).sort("taken_at", -1).limit(5))  # Limit to 5 most recent
            
            if not recs:
                st.sidebar.info("No quiz scores yet.")
            else:
                st.sidebar.write("**Recent Scores (Last 5):**")
                for r in recs:
                    # Verify this record belongs to current user (extra safety check)
                    if r.get("user_id") == user["user_id"]:
                        taken = r.get("taken_at")
                        st.sidebar.write(f"📝 {taken.strftime('%m/%d %H:%M')}: {r.get('score')}/{r.get('total')} ({r.get('percent'):.1f}%)")
        except Exception:
            pass  # Silent fail

    st.sidebar.markdown("---")
    
    # Show system info
    st.sidebar.write("**Powered by:**")
    st.sidebar.write("• 🤖 Google Gemini AI")
    st.sidebar.write("• � MongoDB Atlas")
    st.sidebar.write("• 🔒 Secure Session Tracking")
    
    st.sidebar.markdown("---")
    
    # Show session persistence status
    st.sidebar.info("💡 AI Agent Memory\n\nConversation history maintained during your session for personalized quiz generation.")


if __name__ == "__main__":
    main()
