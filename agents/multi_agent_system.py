"""
Multi-Agent Architecture for Certification Exam Preparation

Three specialized agents:
1. Content Curator Agent - Fetches and organizes study materials
2. Assessment Engine Agent - Generates adaptive exam questions
3. Learning Coach Agent - Provides personalized guidance and analytics
"""
from typing import Dict, List, Any, Optional
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from pymongo import MongoClient
from datetime import datetime
import structlog
import json

logger = structlog.get_logger()


class AgentOrchestrator:
    """Orchestrates the three specialized agents"""
    
    def __init__(self, mongo_client: MongoClient, gemini_model: Gemini):
        self.db = mongo_client["campus-plateform"]
        self.model = gemini_model
        
        # Collections
        self.agent_logs_coll = self.db["agent_logs"]
        self.agent_metrics_coll = self.db["agent_metrics"]
        
        # Initialize the 3 agents
        self.content_curator = ContentCuratorAgent(mongo_client, gemini_model)
        self.assessment_engine = AssessmentEngineAgent(mongo_client, gemini_model)
        self.learning_coach = LearningCoachAgent(mongo_client, gemini_model)
        
        logger.info("agent_orchestrator_initialized", agents=["content_curator", "assessment_engine", "learning_coach"])
    
    def log_agent_activity(self, agent_name: str, action: str, metadata: Dict):
        """Log agent activity for monitoring"""
        log_entry = {
            "agent_name": agent_name,
            "action": action,
            "metadata": metadata,
            "timestamp": datetime.now()
        }
        self.agent_logs_coll.insert_one(log_entry)
        
        logger.info("agent_activity", **log_entry)
    
    def record_metric(self, agent_name: str, metric_type: str, value: float):
        """Record agent performance metrics"""
        metric = {
            "agent_name": agent_name,
            "metric_type": metric_type,
            "value": value,
            "timestamp": datetime.now()
        }
        self.agent_metrics_coll.insert_one(metric)
    
    async def process_user_request(self, 
                                   user_id: str, 
                                   cert_id: str, 
                                   request_type: str,
                                   params: Dict) -> Dict[str, Any]:
        """
        Main entry point - routes requests to appropriate agents
        
        request_types:
        - "fetch_materials": Content Curator
        - "generate_quiz": Assessment Engine
        - "get_coaching": Learning Coach
        """
        start_time = datetime.now()
        
        try:
            if request_type == "fetch_materials":
                result = await self.content_curator.fetch_materials(cert_id, params.get("topics", []))
                agent_name = "content_curator"
                
            elif request_type == "generate_quiz":
                result = await self.assessment_engine.generate_quiz(
                    user_id, cert_id, params
                )
                agent_name = "assessment_engine"
                
                # Check if result contains error
                if "error" in result:
                    raise Exception(result["error"])
                
            elif request_type == "get_coaching":
                result = await self.learning_coach.provide_coaching(user_id, cert_id)
                agent_name = "learning_coach"
                
            else:
                raise ValueError(f"Unknown request type: {request_type}")
            
            # Log success
            duration = (datetime.now() - start_time).total_seconds()
            self.log_agent_activity(agent_name, request_type, {
                "user_id": user_id,
                "cert_id": cert_id,
                "duration_seconds": duration,
                "status": "success"
            })
            self.record_metric(agent_name, "response_time", duration)
            
            return {"success": True, "data": result, "agent": agent_name}
            
        except Exception as e:
            # Log failure
            duration = (datetime.now() - start_time).total_seconds()
            self.log_agent_activity(agent_name if 'agent_name' in locals() else "unknown", 
                                   request_type, {
                "user_id": user_id,
                "cert_id": cert_id,
                "duration_seconds": duration,
                "status": "error",
                "error": str(e)
            })
            
            logger.error("agent_request_failed", error=str(e), request_type=request_type)
            return {"success": False, "error": str(e)}


class ContentCuratorAgent:
    """Agent 1: Curates and organizes study materials"""
    
    def __init__(self, mongo_client: MongoClient, gemini_model: Gemini):
        self.db = mongo_client["campus-plateform"]
        self.model = gemini_model
        self.embeddings_coll = self.db["embeddings"]
        
        # Create LLM agent
        self.agent = LlmAgent(
            name="content_curator",
            model=gemini_model,
            instruction=
            """
            You are an expert Content Curator specializing in certification exam preparation.
Your role is to:
1. Fetch and organize relevant documentation
2. Summarize key concepts
3. Extract important code examples
4. Identify exam-relevant topics

Provide structured, concise summaries that help students focus on exam objectives.
"""
        )
        
        logger.info("content_curator_agent_initialized")
    
    async def fetch_materials(self, cert_id: str, topics: List[str]) -> Dict[str, Any]:
        """Fetch and curate study materials for given topics"""
        logger.info("fetching_materials", cert_id=cert_id, topics=topics)
        
        # Fetch from embeddings (semantic search)
        materials = []
        for topic in topics:
            docs = self.embeddings_coll.find({
                "certification_id": cert_id,
                "topic": topic
            }).limit(5)
            
            for doc in docs:
                materials.append({
                    "topic": topic,
                    "content": doc.get("content", ""),
                    "source": doc.get("metadata", {}).get("source", "")
                })
        
        # Summarize with LLM
        if materials:
            summary_prompt = f"""Summarize these study materials for {', '.join(topics)}:

{json.dumps(materials, indent=2)}

Provide:
1. Key concepts (bullet points)
2. Important code patterns
3. Common exam scenarios"""
            
            # Use Google GenAI SDK directly
            import google.generativeai as genai
            import os
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            gen_model = genai.GenerativeModel('gemini-2.5-flash-lite')
            response = gen_model.generate_content(summary_prompt)
            summary = response.text
            
            return {
                "topics": topics,
                "materials_count": len(materials),
                "summary": summary,
                "raw_materials": materials[:10]  # Limit for response size
            }
        
        return {
            "topics": topics,
            "materials_count": 0,
            "summary": "No materials found. Consider adding documentation to the database.",
            "raw_materials": []
        }


class AssessmentEngineAgent:
    """Agent 2: Generates adaptive exam questions"""
    
    def __init__(self, mongo_client: MongoClient, gemini_model: Gemini):
        self.db = mongo_client["campus-plateform"]
        self.model = gemini_model
        self.quizzes_coll = self.db["quizzes"]
        self.user_performance_coll = self.db["user_performance"]
        
        # Create LLM agent
        self.agent = LlmAgent(
            name="assessment_engine",
            model=gemini_model,
            instruction="""You are an expert Assessment Engine for certification exams.
Your role is to:
1. Generate high-quality exam questions
2. Adapt difficulty based on user performance
3. Follow official exam blueprints
4. Create realistic scenarios

Generate questions in JSON format with:
- question: clear, concise question text
- options: array of choices (4-6 options)
- correct_answer: correct option(s)
- explanation: detailed explanation
- difficulty: easy/medium/hard
- topic: specific exam topic"""
        )
        
        logger.info("assessment_engine_agent_initialized")
    
    async def generate_quiz(self, user_id: str, cert_id: str, params: Dict) -> Dict[str, Any]:
        """Generate adaptive quiz based on user performance"""
        logger.info("generating_quiz", user_id=user_id, cert_id=cert_id)
        
        # Get user's performance history
        performance = self.user_performance_coll.find_one({"user_id": user_id, "cert_id": cert_id})
        
        # Determine difficulty
        if performance:
            avg_score = performance.get("average_score", 0.5)
            if avg_score >= 0.8:
                difficulty = "hard"
            elif avg_score >= 0.6:
                difficulty = "medium"
            else:
                difficulty = "easy"
        else:
            difficulty = params.get("difficulty", "medium")
        
        # Generate questions
        num_questions = params.get("num_questions", 5)
        topics = params.get("topics", [])
        
        prompt = f"""Generate {num_questions} multiple-choice questions for {cert_id} certification exam.

Topics: {', '.join(topics)}
Difficulty: {difficulty}

For technical certifications (MongoDB, AWS, Terraform, GCP, Azure), include code snippets when relevant.

IMPORTANT: Return ONLY a valid JSON array with this exact structure:
[
  {{
    "question": "question text here",
    "code": "optional code snippet (use \\n for newlines)",
    "language": "python|javascript|terraform|yaml|bash",
    "options": ["A) option 1", "B) option 2", "C) option 3", "D) option 4"],
    "correct_answer": "A",
    "explanation": "why this answer is correct",
    "topic": "{topics[0] if topics else 'general'}"
  }}
]

Include 'code' and 'language' fields for questions involving:
- Code analysis
- Configuration examples
- Query syntax
- Infrastructure as Code
- API calls

Do NOT include any markdown, code blocks, or extra text. Return ONLY the JSON array."""
        
        # Use Google GenAI SDK directly
        import google.generativeai as genai
        import os
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        gen_model = genai.GenerativeModel('gemini-2.5-flash-lite')
        llm_response = gen_model.generate_content(prompt)
        response = llm_response.text.strip()
        
        # Remove markdown code blocks if present
        if response.startswith('```'):
            response = response.split('```')[1]
            if response.startswith('json'):
                response = response[4:]
            response = response.strip()
        
        # Parse and validate questions
        try:
            questions = json.loads(response)
            
            # Validate structure
            if not isinstance(questions, list) or len(questions) == 0:
                raise ValueError("Response is not a valid question array")
            
            # Ensure each question has required fields
            for q in questions:
                if not all(k in q for k in ["question", "options", "correct_answer"]):
                    raise ValueError("Question missing required fields")
            
            # Store quiz
            quiz_id = self.quizzes_coll.insert_one({
                "user_id": user_id,
                "cert_id": cert_id,
                "questions": questions,
                "difficulty": difficulty,
                "generated_at": datetime.now(),
                "agent": "assessment_engine"
            }).inserted_id
            
            return {
                "quiz_id": str(quiz_id),
                "questions": questions,
                "difficulty": difficulty,
                "topics": topics
            }
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error("failed_to_parse_questions", error=str(e), response=response[:500])
            return {
                "error": f"Failed to generate valid questions: {str(e)}",
                "raw_response": response[:500]
            }


class LearningCoachAgent:
    """Agent 3: Provides personalized coaching and analytics"""
    
    def __init__(self, mongo_client: MongoClient, gemini_model: Gemini):
        self.db = mongo_client["campus-plateform"]
        self.model = gemini_model
        self.scores_coll = self.db["scores"]
        self.user_performance_coll = self.db["user_performance"]
        
        # Create LLM agent
        self.agent = LlmAgent(
            name="learning_coach",
            model=gemini_model,
            instruction="""You are an expert Learning Coach for certification exam preparation.
Your role is to:
1. Analyze student performance
2. Identify knowledge gaps
3. Provide personalized study recommendations
4. Create study schedules
5. Motivate and guide students

Be supportive, specific, and actionable in your guidance."""
        )
        
        logger.info("learning_coach_agent_initialized")
    
    async def provide_coaching(self, user_id: str, cert_id: str) -> Dict[str, Any]:
        """Provide personalized coaching based on performance"""
        logger.info("providing_coaching", user_id=user_id, cert_id=cert_id)
        
        # Analyze user's quiz history
        recent_scores = list(self.scores_coll.find({
            "user_id": user_id,
            "cert_id": cert_id
        }).sort("submitted_at", -1).limit(10))
        
        if not recent_scores:
            return {
                "message": "Take your first quiz to receive personalized coaching!",
                "recommendation": "Start with 'easy' difficulty to assess your baseline knowledge."
            }
        
        # Calculate analytics
        total_quizzes = len(recent_scores)
        avg_score = sum(s.get("score", 0) for s in recent_scores) / total_quizzes
        
        # Identify weak topics
        topic_performance = {}
        for score in recent_scores:
            for question in score.get("answers", []):
                topic = question.get("topic", "general")
                if topic not in topic_performance:
                    topic_performance[topic] = {"correct": 0, "total": 0}
                
                topic_performance[topic]["total"] += 1
                if question.get("is_correct", False):
                    topic_performance[topic]["correct"] += 1
        
        weak_topics = [
            topic for topic, perf in topic_performance.items()
            if perf["total"] > 0 and (perf["correct"] / perf["total"]) < 0.6
        ]
        
        # Generate coaching advice
        prompt = f"""Analyze this student's performance and provide coaching:

Certification: {cert_id}
Total Quizzes Taken: {total_quizzes}
Average Score: {avg_score * 100:.1f}%
Weak Topics: {', '.join(weak_topics) if weak_topics else 'None identified'}

Provide:
1. Performance summary
2. Specific areas to focus on
3. Study plan for next 7 days
4. Motivational message"""
        
        # Use Google GenAI SDK directly
        import google.generativeai as genai
        import os
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        gen_model = genai.GenerativeModel('gemini-2.5-flash-lite')
        llm_response = gen_model.generate_content(prompt)
        coaching_advice = llm_response.text
        
        # Update performance tracking
        self.user_performance_coll.update_one(
            {"user_id": user_id, "cert_id": cert_id},
            {
                "$set": {
                    "average_score": avg_score,
                    "total_quizzes": total_quizzes,
                    "weak_topics": weak_topics,
                    "last_coaching": datetime.now()
                }
            },
            upsert=True
        )
        
        return {
            "average_score": avg_score,
            "total_quizzes": total_quizzes,
            "weak_topics": weak_topics,
            "coaching_advice": coaching_advice,
            "readiness_level": "exam_ready" if avg_score >= 0.75 else "needs_practice"
        }
