"""
Multi-Agent Architecture for CertAgent

Implements 3 specialized agents:
1. Content Curator Agent - Fetches and organizes study materials
2. Assessment Engine Agent - Generates adaptive certification questions
3. Learning Coach Agent - Provides personalized recommendations
"""
from typing import Dict, List, Any, Optional
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.genai import types
from pymongo import MongoClient
from datetime import datetime
import json
import asyncio


# Retry configuration for API calls
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)


class AgentOrchestrator:
    """Orchestrates the 3-agent system"""
    
    def __init__(self, mongo_client: MongoClient, gemini_api_key: str, db_name: str = "campus-plateform"):
        self.db = mongo_client[db_name]
        self.agent_logs = self.db["agent_logs"]
        self.gemini_api_key = gemini_api_key
        
        # Initialize agents
        self.content_curator = ContentCuratorAgent(mongo_client, gemini_api_key, db_name)
        self.assessment_engine = AssessmentEngineAgent(mongo_client, gemini_api_key, db_name)
        self.learning_coach = LearningCoachAgent(mongo_client, gemini_api_key, db_name)
    
    def log_agent_activity(
        self,
        agent_name: str,
        action: str,
        user_id: str,
        details: Dict[str, Any],
        status: str = "success"
    ):
        """Log agent activity for monitoring"""
        
        log_entry = {
            "timestamp": datetime.now(),
            "agent_name": agent_name,
            "action": action,
            "user_id": user_id,
            "details": details,
            "status": status
        }
        
        self.agent_logs.insert_one(log_entry)
    
    async def generate_quiz(
        self,
        user_id: str,
        certification_id: str,
        topics: List[str],
        num_questions: int,
        difficulty: str
    ) -> Dict[str, Any]:
        """
        Orchestrate quiz generation using all 3 agents
        
        Flow:
        1. Content Curator: Fetch relevant documentation
        2. Assessment Engine: Generate questions
        3. Learning Coach: Adjust difficulty based on user history
        """
        
        try:
            # Step 1: Content Curator fetches relevant materials
            self.log_agent_activity(
                "ContentCuratorAgent",
                "fetch_materials",
                user_id,
                {"certification_id": certification_id, "topics": topics}
            )
            
            study_materials = await self.content_curator.fetch_study_materials(
                certification_id=certification_id,
                topics=topics
            )
            
            # Step 2: Learning Coach adjusts difficulty
            self.log_agent_activity(
                "LearningCoachAgent",
                "adjust_difficulty",
                user_id,
                {"certification_id": certification_id, "requested_difficulty": difficulty}
            )
            
            adjusted_difficulty = await self.learning_coach.adjust_difficulty_for_user(
                user_id=user_id,
                certification_id=certification_id,
                requested_difficulty=difficulty
            )
            
            # Step 3: Assessment Engine generates questions
            self.log_agent_activity(
                "AssessmentEngineAgent",
                "generate_questions",
                user_id,
                {
                    "certification_id": certification_id,
                    "topics": topics,
                    "num_questions": num_questions,
                    "difficulty": adjusted_difficulty
                }
            )
            
            questions = await self.assessment_engine.generate_questions(
                certification_id=certification_id,
                topics=topics,
                num_questions=num_questions,
                difficulty=adjusted_difficulty,
                context=study_materials
            )
            
            return {
                "success": True,
                "questions": questions,
                "difficulty_adjusted": adjusted_difficulty != difficulty,
                "original_difficulty": difficulty,
                "final_difficulty": adjusted_difficulty,
                "materials_fetched": len(study_materials) > 0
            }
            
        except Exception as e:
            self.log_agent_activity(
                "AgentOrchestrator",
                "generate_quiz",
                user_id,
                {"error": str(e)},
                status="error"
            )
            raise
    
    async def get_study_recommendations(
        self,
        user_id: str,
        certification_id: str
    ) -> Dict[str, Any]:
        """Get personalized study recommendations from Learning Coach"""
        
        return await self.learning_coach.generate_study_plan(user_id, certification_id)


class ContentCuratorAgent:
    """Agent responsible for fetching and organizing study materials"""
    
    def __init__(self, mongo_client: MongoClient, gemini_api_key: str, db_name: str = "campus-plateform"):
        self.db = mongo_client[db_name]
        self.embeddings_collection = self.db["embeddings"]
        self.certifications_collection = self.db["certifications"]
        
        # Initialize Gemini for content summarization
        self.llm = Gemini(
            model_name="gemini-2.0-flash-lite",
            api_key=gemini_api_key,
            generation_config=types.GenerationConfig(
                temperature=0.3,
                top_p=0.95,
                max_output_tokens=2048,
            ),
            http_options=retry_config
        )
    
    async def fetch_study_materials(
        self,
        certification_id: str,
        topics: List[str],
        max_docs_per_topic: int = 3
    ) -> str:
        """
        Fetch relevant study materials from embedding store
        
        Uses semantic search to find most relevant documentation
        """
        
        from memory.embedding_store import EmbeddingStore
        
        embedding_store = EmbeddingStore(self.db.client)
        
        all_materials = []
        
        for topic in topics:
            # Semantic search for this topic
            results = embedding_store.semantic_search(
                query=topic,
                certification_id=certification_id,
                topic=topic,
                top_k=max_docs_per_topic
            )
            
            for result in results:
                all_materials.append(f"### Topic: {topic}\n{result['content']}\n")
        
        # If no materials found in embeddings, get from certification pack
        if not all_materials:
            cert_doc = self.certifications_collection.find_one({"_id": certification_id})
            if cert_doc:
                all_materials.append(f"Certification: {cert_doc['name']}\nTopics: {', '.join(topics)}")
        
        combined_materials = "\n\n".join(all_materials)
        
        # Summarize if too long (>8000 tokens roughly)
        if len(combined_materials) > 32000:
            summary_prompt = f"""Summarize the following study materials concisely, preserving key technical details:

{combined_materials[:32000]}

Provide a comprehensive but concise summary."""
            
            summary = await self.llm.generate_content_async(summary_prompt)
            return summary.text if hasattr(summary, 'text') else str(summary)
        
        return combined_materials


class AssessmentEngineAgent:
    """Agent responsible for generating certification-grade questions"""
    
    def __init__(self, mongo_client: MongoClient, gemini_api_key: str, db_name: str = "campus-plateform"):
        self.db = mongo_client[db_name]
        self.certifications_collection = self.db["certifications"]
        self.questions_collection = self.db["generated_questions"]
        
        # Initialize Gemini for question generation
        self.agent = LlmAgent(
            name="AssessmentEngineAgent",
            llm=Gemini(
                model_name="gemini-2.0-flash-lite",
                api_key=gemini_api_key,
                generation_config=types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.95,
                    max_output_tokens=8192,
                    response_mime_type="application/json"
                ),
                http_options=retry_config
            ),
            system_instructions="You are an expert certification exam question writer. Generate high-quality, certification-standard questions."
        )
    
    async def generate_questions(
        self,
        certification_id: str,
        topics: List[str],
        num_questions: int,
        difficulty: str,
        context: str = ""
    ) -> List[Dict[str, Any]]:
        """Generate certification-specific questions"""
        
        # Get certification pack
        cert_pack = self.certifications_collection.find_one({"_id": certification_id})
        if not cert_pack:
            raise ValueError(f"Certification {certification_id} not found")
        
        # Build prompt based on certification style
        prompt = self._build_question_prompt(
            cert_pack=cert_pack,
            topics=topics,
            num_questions=num_questions,
            difficulty=difficulty,
            context=context
        )
        
        # Generate questions
        response = await self.agent.generate_response_async(prompt)
        
        # Parse JSON response
        try:
            questions_data = json.loads(response.text)
            questions = questions_data.get("questions", [])
            
            # Store generated questions for quality tracking
            self._store_questions_for_analysis(
                certification_id=certification_id,
                questions=questions,
                difficulty=difficulty
            )
            
            return questions
            
        except json.JSONDecodeError:
            # Fallback: return empty list if parsing fails
            return []
    
    def _build_question_prompt(
        self,
        cert_pack: Dict[str, Any],
        topics: List[str],
        num_questions: int,
        difficulty: str,
        context: str
    ) -> str:
        """Build certification-specific question generation prompt"""
        
        blueprint = cert_pack.get("blueprint", {})
        question_style = cert_pack.get("question_style", "scenario_based")
        code_language = cert_pack.get("code_language")
        
        mcq_count = int(num_questions * blueprint.get("question_types", {}).get("mcq", 0.8))
        msq_count = num_questions - mcq_count
        
        prompt = f"""Generate {num_questions} certification exam questions for {cert_pack['name']}.

CERTIFICATION CONTEXT:
{context[:4000] if context else "No additional context provided."}

TOPICS TO COVER:
{', '.join(topics)}

QUESTION DISTRIBUTION:
- {mcq_count} Multiple Choice Questions (MCQ) - single correct answer
- {msq_count} Multiple Select Questions (MSQ) - 2-3 correct answers

DIFFICULTY: {difficulty}

QUESTION STYLE: {question_style}
"""
        
        if code_language:
            prompt += f"""
CODE REQUIREMENTS:
- Include {code_language} code snippets in 70% of questions
- Use realistic scenarios and proper syntax
- Test code comprehension and debugging skills
"""
        
        prompt += """
OUTPUT FORMAT (JSON):
{
  "questions": [
    {
      "question": "Question text here",
      "type": "mcq" or "msq",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": ["A"] for MCQ or ["A", "C"] for MSQ,
      "explanation": "Why this answer is correct",
      "difficulty": "easy|medium|hard",
      "topic": "Topic name"
    }
  ]
}

Generate high-quality, certification-standard questions now."""
        
        return prompt
    
    def _store_questions_for_analysis(
        self,
        certification_id: str,
        questions: List[Dict[str, Any]],
        difficulty: str
    ):
        """Store questions for quality analysis"""
        
        for question in questions:
            doc = {
                "certification_id": certification_id,
                "question": question,
                "difficulty": difficulty,
                "generated_at": datetime.now(),
                "quality_score": None,  # Will be calculated later
                "usage_count": 0
            }
            self.questions_collection.insert_one(doc)


class LearningCoachAgent:
    """Agent responsible for personalized learning recommendations"""
    
    def __init__(self, mongo_client: MongoClient, gemini_api_key: str, db_name: str = "campus-plateform"):
        self.db = mongo_client[db_name]
        self.users_collection = self.db["users"]
        
        # Initialize Gemini for recommendations
        self.llm = Gemini(
            model_name="gemini-2.0-flash-lite",
            api_key=gemini_api_key,
            generation_config=types.GenerationConfig(
                temperature=0.5,
                top_p=0.95,
                max_output_tokens=2048,
            ),
            http_options=retry_config
        )
    
    async def adjust_difficulty_for_user(
        self,
        user_id: str,
        certification_id: str,
        requested_difficulty: str
    ) -> str:
        """Adjust difficulty based on user's performance history"""
        
        from memory.embedding_store import UserMemoryStore
        
        memory_store = UserMemoryStore(self.db.client)
        patterns = memory_store.analyze_user_patterns(user_id, certification_id)
        
        average_score = patterns.get("average_score", 0)
        total_sessions = patterns.get("total_sessions", 0)
        
        # No history - use requested difficulty
        if total_sessions == 0:
            return requested_difficulty
        
        # Adjust based on performance
        if average_score >= 85 and requested_difficulty == "easy":
            return "medium"  # Push to next level
        elif average_score >= 90 and requested_difficulty == "medium":
            return "hard"
        elif average_score < 60 and requested_difficulty == "hard":
            return "medium"  # Make it easier
        elif average_score < 50 and requested_difficulty == "medium":
            return "easy"
        
        return requested_difficulty
    
    async def generate_study_plan(
        self,
        user_id: str,
        certification_id: str
    ) -> Dict[str, Any]:
        """Generate personalized study plan"""
        
        from memory.embedding_store import UserMemoryStore
        
        memory_store = UserMemoryStore(self.db.client)
        patterns = memory_store.analyze_user_patterns(user_id, certification_id)
        
        # Get certification info
        cert_doc = self.db["certifications"].find_one({"_id": certification_id})
        
        if not cert_doc:
            return {"error": "Certification not found"}
        
        # Generate recommendations
        prompt = f"""Based on this user's learning data, generate a personalized study plan:

Certification: {cert_doc['name']}
Total Practice Sessions: {patterns['total_sessions']}
Average Score: {patterns['average_score']}%
Weak Topics: {', '.join(patterns['weak_topics'])}
Strong Topics: {', '.join(patterns['strong_topics'])}
Preferred Difficulty: {patterns['preferred_difficulty']}

Provide:
1. Focus areas (2-3 topics to prioritize)
2. Recommended study approach
3. Daily practice goals
4. Estimated time to exam readiness

Format as a brief, actionable plan."""
        
        response = await self.llm.generate_content_async(prompt)
        recommendation = response.text if hasattr(response, 'text') else str(response)
        
        return {
            "recommendation": recommendation,
            "weak_topics": patterns['weak_topics'],
            "strong_topics": patterns['strong_topics'],
            "average_score": patterns['average_score'],
            "total_sessions": patterns['total_sessions']
        }
