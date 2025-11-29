"""
Autonomous Multi-Agent Architecture for Certification Exam Preparation

Enhanced with A2A (Agent-to-Agent) communication patterns and tool integration.
Three specialized agents with autonomous capabilities and inter-agent collaboration.

Agents:
1. Content Curator Agent - Fetches, analyzes, and organizes study materials
2. Assessment Engine Agent - Generates adaptive questions and evaluates performance
3. Learning Coach Agent - Provides personalized guidance and learning analytics

A2A Features:
- Inter-agent communication and task delegation
- Autonomous tool usage for enhanced capabilities
- Collaborative decision making and knowledge sharing
- Dynamic orchestration based on context and performance
"""
from typing import Dict, List, Any, Optional, Callable, Awaitable
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from pymongo import MongoClient
from datetime import datetime, timedelta
import structlog
import json
import asyncio
import os
from dataclasses import dataclass, field
from enum import Enum
from memory.embedding_store import EmbeddingStore

logger = structlog.get_logger()


class MessageType(Enum):
    """Types of messages agents can exchange"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    COLLABORATION = "collaboration"
    DELEGATION = "delegation"


class AgentCapability(Enum):
    """Capabilities that agents can offer"""
    CONTENT_ANALYSIS = "content_analysis"
    QUESTION_GENERATION = "question_generation"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    STUDY_RECOMMENDATION = "study_recommendation"
    DOCUMENT_FETCHING = "document_fetching"
    QUIZ_EVALUATION = "quiz_evaluation"


@dataclass
class AgentMessage:
    """Message structure for A2A communication"""
    sender: str
    receiver: str
    message_type: MessageType
    capability: AgentCapability
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    correlation_id: str = ""
    priority: int = 1  # 1=low, 5=high


class AgentTool:
    """Base class for agent tools"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        raise NotImplementedError


class DatabaseQueryTool(AgentTool):
    """Tool for querying the database autonomously"""

    def __init__(self, mongo_client: MongoClient, db_name: str = "campus-plateform"):
        super().__init__("database_query", "Query MongoDB collections for information")
        self.db = mongo_client[db_name]

    async def execute(self, collection: str, query: Dict, limit: int = 10) -> Dict[str, Any]:
        """Execute database query"""
        try:
            results = list(self.db[collection].find(query).limit(limit))
            return {"success": True, "results": results, "count": len(results)}
        except Exception as e:
            return {"success": False, "error": str(e)}


class ContentAnalysisTool(AgentTool):
    """Tool for analyzing content using Gemini"""

    def __init__(self):
        super().__init__("content_analysis", "Analyze and summarize content using AI")
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')

    async def execute(self, content: str, task: str) -> Dict[str, Any]:
        """Analyze content with specific task"""
        try:
            prompt = f"Task: {task}\n\nContent to analyze:\n{content[:4000]}"
            response = self.model.generate_content(prompt)
            return {"success": True, "analysis": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}


class AgentOrchestrator:
    """Enhanced orchestrator with A2A communication and autonomous capabilities"""

    def __init__(self, mongo_client: MongoClient, gemini_model: Gemini):
        self.db = mongo_client["campus-plateform"]
        self.model = gemini_model

        # Collections
        self.agent_logs_coll = self.db["agent_logs"]
        self.agent_metrics_coll = self.db["agent_metrics"]
        self.agent_messages_coll = self.db["agent_messages"]

        # Autonomous tools available to all agents
        self.shared_tools = {
            "database_query": DatabaseQueryTool(mongo_client),
            "content_analysis": ContentAnalysisTool()
        }

        # Initialize agents with enhanced capabilities
        self.content_curator = ContentCuratorAgent(mongo_client, gemini_model, self)
        self.assessment_engine = AssessmentEngineAgent(mongo_client, gemini_model, self)
        self.learning_coach = LearningCoachAgent(mongo_client, gemini_model, self)

        # Agent registry for A2A communication
        self.agents = {
            "content_curator": self.content_curator,
            "assessment_engine": self.assessment_engine,
            "learning_coach": self.learning_coach
        }

        # Message queue for A2A communication
        self.message_queue: List[AgentMessage] = []

        logger.info("enhanced_agent_orchestrator_initialized",
                   agents=list(self.agents.keys()),
                   tools=list(self.shared_tools.keys()))

    async def send_message(self, message: AgentMessage) -> None:
        """Send message to another agent"""
        # Store message in database for persistence
        message_doc = {
            "sender": message.sender,
            "receiver": message.receiver,
            "message_type": message.message_type.value,
            "capability": message.capability.value,
            "content": message.content,
            "timestamp": message.timestamp,
            "correlation_id": message.correlation_id,
            "priority": message.priority
        }
        self.agent_messages_coll.insert_one(message_doc)

        # Add to in-memory queue
        self.message_queue.append(message)

        logger.info("agent_message_sent",
                   sender=message.sender,
                   receiver=message.receiver,
                   type=message.message_type.value)

    async def receive_messages(self, agent_name: str) -> List[AgentMessage]:
        """Get messages for a specific agent"""
        messages = [msg for msg in self.message_queue if msg.receiver == agent_name]
        # Remove from queue after retrieval
        self.message_queue = [msg for msg in self.message_queue if msg.receiver != agent_name]
        return messages

    async def delegate_task(self, from_agent: str, to_agent: str,
                          capability: AgentCapability, task_data: Dict[str, Any],
                          correlation_id: str = "") -> Dict[str, Any]:
        """Delegate a task from one agent to another"""
        if correlation_id == "":
            correlation_id = f"{from_agent}_{to_agent}_{datetime.now().timestamp()}"

        message = AgentMessage(
            sender=from_agent,
            receiver=to_agent,
            message_type=MessageType.DELEGATION,
            capability=capability,
            content=task_data,
            correlation_id=correlation_id,
            priority=3
        )

        await self.send_message(message)

        # Wait for response (with timeout)
        response = await self.wait_for_response(correlation_id, timeout_seconds=30)
        return response

    async def wait_for_response(self, correlation_id: str, timeout_seconds: int = 30) -> Dict[str, Any]:
        """Wait for a response message with given correlation ID"""
        start_time = datetime.now()

        while (datetime.now() - start_time).seconds < timeout_seconds:
            # Check for response messages
            response_doc = self.agent_messages_coll.find_one({
                "correlation_id": correlation_id,
                "message_type": "response"
            })

            if response_doc:
                return response_doc["content"]

            await asyncio.sleep(1)  # Wait 1 second before checking again

        return {"error": "Timeout waiting for agent response"}

    async def collaborate_on_task(self, requesting_agent: str, capability: AgentCapability,
                                task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Find the best agent for a capability and collaborate"""
        # Determine which agent is best suited for this capability
        capability_mapping = {
            AgentCapability.CONTENT_ANALYSIS: "content_curator",
            AgentCapability.QUESTION_GENERATION: "assessment_engine",
            AgentCapability.PERFORMANCE_ANALYSIS: "learning_coach",
            AgentCapability.STUDY_RECOMMENDATION: "learning_coach",
            AgentCapability.DOCUMENT_FETCHING: "content_curator",
            AgentCapability.QUIZ_EVALUATION: "assessment_engine"
        }

        target_agent = capability_mapping.get(capability, "content_curator")

        if target_agent == requesting_agent:
            # Agent can handle it directly
            return {"action": "handle_directly"}

        # Delegate to appropriate agent
        return await self.delegate_task(requesting_agent, target_agent, capability, task_data)

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
        Enhanced main entry point with autonomous agent collaboration

        request_types:
        - "fetch_materials": Content Curator (may collaborate with others)
        - "generate_quiz": Assessment Engine (may consult Learning Coach)
        - "get_coaching": Learning Coach (may request Assessment data)
        - "study_session": Autonomous multi-agent study session
        """

        start_time = datetime.now()

        try:
            if request_type == "fetch_materials":
                result = await self.content_curator.fetch_materials_autonomous(cert_id, params)
                agent_name = "content_curator"

            elif request_type == "generate_quiz":
                result = await self.assessment_engine.generate_quiz_autonomous(
                    user_id, cert_id, params
                )
                agent_name = "assessment_engine"

            elif request_type == "get_coaching":
                result = await self.learning_coach.provide_coaching_autonomous(user_id, cert_id)
                agent_name = "learning_coach"

            elif request_type == "study_session":
                result = await self.orchestrate_study_session(user_id, cert_id, params)
                agent_name = "orchestrator"

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
            self.log_agent_activity("orchestrator", request_type, {
                "user_id": user_id,
                "cert_id": cert_id,
                "duration_seconds": duration,
                "status": "error",
                "error": str(e)
            })

            logger.error("agent_request_failed", error=str(e), request_type=request_type)
            return {"success": False, "error": str(e)}

    async def orchestrate_study_session(self, user_id: str, cert_id: str, params: Dict) -> Dict[str, Any]:
        """Autonomous multi-agent study session orchestration"""
        logger.info("orchestrating_study_session", user_id=user_id, cert_id=cert_id)

        # Step 1: Learning Coach analyzes user performance
        performance_analysis = await self.learning_coach.analyze_performance(user_id, cert_id)

        # Step 2: Content Curator fetches relevant materials based on weak areas
        weak_topics = performance_analysis.get("weak_topics", [])
        materials = await self.content_curator.fetch_materials_for_topics(cert_id, weak_topics)

        # Step 3: Assessment Engine generates targeted quiz
        quiz = await self.assessment_engine.generate_targeted_quiz(
            user_id, cert_id, weak_topics, performance_analysis
        )

        # Step 4: Learning Coach creates personalized study plan
        study_plan = await self.learning_coach.create_study_plan(
            user_id, cert_id, materials, quiz, performance_analysis
        )

        return {
            "session_type": "autonomous_study",
            "performance_analysis": performance_analysis,
            "materials": materials,
            "quiz": quiz,
            "study_plan": study_plan,
            "agents_involved": ["learning_coach", "content_curator", "assessment_engine"]
        }


class ContentCuratorAgent:
    """Agent 1: Autonomous Content Curator with A2A capabilities"""

    def __init__(self, mongo_client: MongoClient, gemini_model: Gemini, orchestrator: 'AgentOrchestrator'):
        self.db = mongo_client["campus-plateform"]
        self.model = gemini_model
        self.orchestrator = orchestrator
        self.embedding_store = EmbeddingStore(mongo_client, "campus-plateform")
        self.name = "content_curator"

        # Autonomous tools
        self.tools = {
            "database_query": self.orchestrator.shared_tools["database_query"],
            "content_analysis": self.orchestrator.shared_tools["content_analysis"]
        }

        # Create enhanced LLM agent with tool capabilities
        self.agent = LlmAgent(
            name="content_curator",
            model=gemini_model,
            instruction=self._get_agent_instruction()
        )

        logger.info("content_curator_agent_initialized_with_a2a")

    def _get_agent_instruction(self) -> str:
        return """
        You are an autonomous Content Curator Agent specializing in certification exam preparation.

        Your capabilities:
        1. Fetch and organize relevant documentation using semantic search and AI tools
        2. Analyze content quality and relevance using AI tools
        3. Collaborate with other agents for comprehensive content curation
        4. Perform intelligent semantic search to find relevant materials beyond exact keyword matches
        5. Query databases autonomously for existing materials
        6. Summarize and extract key concepts from technical content

        Autonomous behaviors:
        - Use semantic search to find content based on meaning and context, not just keywords
        - Use database_query tool to check existing materials before fetching new ones
        - Use content_analysis tool to evaluate content quality
        - Delegate complex analysis tasks to other agents when needed
        - Maintain content relevance to exam objectives using similarity-based retrieval

        Always provide structured, concise summaries that help students focus on exam objectives.
        When collaborating with other agents, clearly communicate your semantic search capabilities.
        """

    async def fetch_materials_autonomous(self, cert_id: str, params: Dict) -> Dict[str, Any]:
        """Autonomous material fetching with tool usage and A2A collaboration"""
        topics = params.get("topics", [])
        logger.info("autonomous_material_fetch", cert_id=cert_id, topics=topics)

        # Step 1: Check existing materials using database tool
        existing_materials = await self._check_existing_materials(cert_id, topics)

        # Step 2: Analyze what additional content is needed
        content_gaps = await self._analyze_content_gaps(cert_id, topics, existing_materials)

        # Step 3: Collaborate with other agents if needed
        if content_gaps.get("needs_assessment_data", False):
            assessment_data = await self.orchestrator.collaborate_on_task(
                self.name,
                AgentCapability.PERFORMANCE_ANALYSIS,
                {"cert_id": cert_id, "request_type": "content_gaps"}
            )

        # Step 4: Fetch and curate materials
        curated_materials = await self._curate_materials(cert_id, topics, content_gaps)

        # Step 5: Use AI analysis for quality assessment
        quality_analysis = await self._analyze_content_quality(curated_materials)

        return {
            "topics": topics,
            "existing_materials_count": len(existing_materials),
            "new_materials_count": len(curated_materials.get("new_materials", [])),
            "content_gaps": content_gaps,
            "quality_analysis": quality_analysis,
            "curated_content": curated_materials,
            "collaboration_used": content_gaps.get("needs_assessment_data", False)
        }

    async def _check_existing_materials(self, cert_id: str, topics: List[str]) -> List[Dict]:
        """Use semantic search to check existing materials"""
        all_materials = []

        # Create a comprehensive search query based on topics
        search_query = f"certification exam preparation materials for {cert_id} covering topics: {', '.join(topics)}"

        # Perform semantic search across all topics for this certification
        semantic_results = self.embedding_store.semantic_search(
            query=search_query,
            certification_id=cert_id,
            top_k=15  # Get more results for better coverage
        )

        # Convert semantic search results to expected format
        for result in semantic_results:
            all_materials.append({
                "content": result["content"],
                "topic": result["topic"],
                "certification_id": result["certification_id"],
                "similarity": result["similarity"],
                "metadata": result.get("metadata", {})
            })

        return all_materials

    async def _analyze_content_gaps(self, cert_id: str, topics: List[str],
                                  existing_materials: List[Dict]) -> Dict[str, Any]:
        """Analyze what content is missing using AI"""
        analysis_prompt = f"""
        Analyze existing materials for certification {cert_id} and topics: {', '.join(topics)}

        Existing materials count: {len(existing_materials)}
        Topics covered: {set(m.get('topic', '') for m in existing_materials)}

        Determine:
        1. Are there significant content gaps?
        2. Do we need to consult assessment data for learning priorities?
        3. What types of content are most needed?

        Return analysis as JSON with keys: has_gaps, needs_assessment_data, content_types_needed
        """

        analysis_result = await self.tools["content_analysis"].execute(
            content=str(existing_materials[:5]),  # Sample for analysis
            task=analysis_prompt
        )

        if analysis_result["success"]:
            try:
                # Try to parse JSON from analysis
                analysis_text = analysis_result["analysis"]
                # Extract JSON if present
                start = analysis_text.find('{')
                end = analysis_text.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = analysis_text[start:end]
                    return json.loads(json_str)
            except:
                pass

        # Fallback analysis
        return {
            "has_gaps": len(existing_materials) < len(topics) * 2,
            "needs_assessment_data": len(existing_materials) == 0,
            "content_types_needed": ["documentation", "examples", "best_practices"]
        }

    async def _curate_materials(self, cert_id: str, topics: List[str],
                               content_gaps: Dict[str, Any]) -> Dict[str, Any]:
        """Curate materials using semantic search for intelligent retrieval"""
        materials = []

        # For each topic, perform semantic search to find relevant content
        for topic in topics:
            # Create topic-specific search query
            search_query = f"certification exam preparation for {cert_id}: {topic} concepts, examples, and best practices"

            # Perform semantic search for this topic
            topic_results = self.embedding_store.semantic_search(
                query=search_query,
                certification_id=cert_id,
                top_k=8  # Get top 8 most relevant results per topic
            )

            # Add results with topic context
            for result in topic_results:
                materials.append({
                    "content": result["content"],
                    "topic": topic,  # Use requested topic for consistency
                    "certification_id": result["certification_id"],
                    "similarity_score": result["similarity"],
                    "metadata": result.get("metadata", {}),
                    "retrieval_method": "semantic_search"
                })

        return {
            "materials": materials,
            "new_materials": [],  # Would be populated by actual fetching
            "enhancement_applied": "semantic_search_and_quality_filtering",
            "total_materials_found": len(materials)
        }

    async def _analyze_content_quality(self, materials: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze quality of curated content"""
        sample_content = str(materials.get("materials", [])[:3])

        quality_result = await self.tools["content_analysis"].execute(
            content=sample_content,
            task="Assess the quality, relevance, and comprehensiveness of this educational content for certification exam preparation."
        )

        return quality_result

    async def fetch_materials_for_topics(self, cert_id: str, topics: List[str]) -> Dict[str, Any]:
        """Fetch materials specifically for given topics (used by orchestrator)"""
        return await self.fetch_materials_autonomous(cert_id, {"topics": topics})

    async def semantic_search_materials(self, cert_id: str, query: str, top_k: int = 10) -> Dict[str, Any]:
        """Perform semantic search for materials using natural language query"""
        logger.info("semantic_search_materials", cert_id=cert_id, query=query, top_k=top_k)

        # Perform semantic search
        search_results = self.embedding_store.semantic_search(
            query=query,
            certification_id=cert_id,
            top_k=top_k
        )

        # Format results for agent consumption
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                "content": result["content"],
                "topic": result["topic"],
                "similarity_score": result["similarity"],
                "certification_id": result["certification_id"],
                "metadata": result.get("metadata", {}),
                "search_method": "semantic_similarity"
            })

        return {
            "query": query,
            "certification_id": cert_id,
            "results": formatted_results,
            "total_found": len(formatted_results),
            "search_type": "semantic_search"
        }

    # Legacy method for backward compatibility
    async def fetch_materials(self, cert_id: str, topics: List[str]) -> Dict[str, Any]:
        """Legacy method - now uses autonomous fetching"""
        return await self.fetch_materials_autonomous(cert_id, {"topics": topics})


class AssessmentEngineAgent:
    """Agent 2: Autonomous Assessment Engine with A2A capabilities"""

    def __init__(self, mongo_client: MongoClient, gemini_model: Gemini, orchestrator: 'AgentOrchestrator'):
        self.db = mongo_client["campus-plateform"]
        self.model = gemini_model
        self.orchestrator = orchestrator
        self.quizzes_coll = self.db["quizzes"]
        self.user_performance_coll = self.db["user_performance"]
        self.scores_coll = self.db["scores"]
        self.name = "assessment_engine"

        # Autonomous tools
        self.tools = {
            "database_query": self.orchestrator.shared_tools["database_query"],
            "content_analysis": self.orchestrator.shared_tools["content_analysis"]
        }

        # Create enhanced LLM agent
        self.agent = LlmAgent(
            name="assessment_engine",
            model=gemini_model,
            instruction=self._get_agent_instruction()
        )

        logger.info("assessment_engine_agent_initialized_with_a2a")

    def _get_agent_instruction(self) -> str:
        return """
        You are an autonomous Assessment Engine Agent for certification exam preparation.

        Your capabilities:
        1. Generate adaptive, high-quality exam questions using AI analysis
        2. Evaluate user performance and adjust difficulty dynamically
        3. Collaborate with Learning Coach for performance insights
        4. Consult Content Curator for topic relevance and coverage
        5. Query performance databases autonomously for user history

        Autonomous behaviors:
        - Analyze user performance data before generating questions
        - Consult other agents for comprehensive assessment strategy
        - Adapt question difficulty based on real-time performance
        - Ensure questions align with exam blueprints and learning objectives

        Always generate questions in valid JSON format with proper structure.
        Collaborate with other agents to create comprehensive assessment experiences.
        """

    async def generate_quiz_autonomous(self, user_id: str, cert_id: str, params: Dict) -> Dict[str, Any]:
        """Autonomous quiz generation with A2A collaboration"""
        logger.info("autonomous_quiz_generation", user_id=user_id, cert_id=cert_id)

        # Step 1: Analyze user performance using database tool
        performance_data = await self._analyze_user_performance(user_id, cert_id)

        # Step 2: Consult Learning Coach for performance insights
        coaching_insights = await self.orchestrator.collaborate_on_task(
            self.name,
            AgentCapability.PERFORMANCE_ANALYSIS,
            {
                "user_id": user_id,
                "cert_id": cert_id,
                "request_type": "assessment_strategy"
            }
        )

        # Step 3: Get content recommendations from Content Curator
        content_recommendations = await self.orchestrator.collaborate_on_task(
            self.name,
            AgentCapability.CONTENT_ANALYSIS,
            {
                "cert_id": cert_id,
                "request_type": "assessment_topics",
                "performance_data": performance_data
            }
        )

        # Step 4: Generate adaptive quiz based on all insights
        quiz_result = await self._generate_adaptive_quiz(
            user_id, cert_id, params, performance_data,
            coaching_insights, content_recommendations
        )

        return quiz_result

    async def _analyze_user_performance(self, user_id: str, cert_id: str) -> Dict[str, Any]:
        """Analyze user performance using database queries"""
        # Get recent quiz scores
        scores_result = await self.tools["database_query"].execute(
            collection="scores",
            query={"user_id": user_id, "cert_id": cert_id},
            limit=20
        )

        # Get performance tracking
        performance_result = await self.tools["database_query"].execute(
            collection="user_performance",
            query={"user_id": user_id, "cert_id": cert_id},
            limit=1
        )

        scores = scores_result.get("results", []) if scores_result["success"] else []
        performance = performance_result.get("results", [{}]) if performance_result["success"] else [{}]

        return {
            "recent_scores": scores,
            "performance_summary": performance[0] if performance else {},
            "total_quizzes": len(scores),
            "average_score": sum(s.get("score", 0) for s in scores) / len(scores) if scores else 0
        }

    async def _generate_adaptive_quiz(self, user_id: str, cert_id: str, params: Dict,
                                    performance_data: Dict, coaching_insights: Dict,
                                    content_recommendations: Dict) -> Dict[str, Any]:
        """Generate quiz using all available insights"""

        # Determine optimal difficulty and topics
        difficulty = self._calculate_optimal_difficulty(performance_data, coaching_insights)
        topics = self._select_optimal_topics(content_recommendations, params)

        # Generate questions using enhanced prompt
        num_questions = params.get("num_questions", 5)

        enhanced_prompt = self._build_enhanced_quiz_prompt(
            cert_id, topics, difficulty, num_questions,
            performance_data, coaching_insights, content_recommendations
        )

        # Use Gemini for question generation
        import google.generativeai as genai
        import os
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        gen_model = genai.GenerativeModel('gemini-2.5-flash-lite')
        llm_response = gen_model.generate_content(enhanced_prompt)
        response = llm_response.text.strip()

        # Parse and validate questions
        questions = self._parse_questions_response(response)

        if not questions:
            return {"error": "Failed to generate valid questions"}

        # Store quiz with enhanced metadata
        quiz_id = self.quizzes_coll.insert_one({
            "user_id": user_id,
            "cert_id": cert_id,
            "questions": questions,
            "difficulty": difficulty,
            "topics": topics,
            "generated_at": datetime.now(),
            "agent": "assessment_engine",
            "collaboration_data": {
                "performance_insights_used": bool(coaching_insights),
                "content_recommendations_used": bool(content_recommendations),
                "autonomous_generation": True
            }
        }).inserted_id

        return {
            "quiz_id": str(quiz_id),
            "questions": questions,
            "difficulty": difficulty,
            "topics": topics,
            "insights_used": {
                "performance_analysis": bool(coaching_insights),
                "content_recommendations": bool(content_recommendations)
            }
        }

    def _calculate_optimal_difficulty(self, performance_data: Dict, coaching_insights: Dict) -> str:
        """Calculate optimal difficulty based on performance and insights"""
        avg_score = performance_data.get("average_score", 0.5)

        # Consider coaching recommendations
        if isinstance(coaching_insights, dict) and "recommended_difficulty" in coaching_insights:
            return coaching_insights["recommended_difficulty"]

        # Default logic
        if avg_score >= 0.8:
            return "hard"
        elif avg_score >= 0.6:
            return "medium"
        else:
            return "easy"

    def _select_optimal_topics(self, content_recommendations: Dict, params: Dict) -> List[str]:
        """Select optimal topics based on recommendations and params"""
        requested_topics = params.get("topics", [])

        if isinstance(content_recommendations, dict) and "recommended_topics" in content_recommendations:
            recommended = content_recommendations["recommended_topics"]
            if isinstance(recommended, list):
                return recommended[:5]  # Limit to 5 topics

        return requested_topics[:5] if requested_topics else ["general"]

    def _build_enhanced_quiz_prompt(self, cert_id: str, topics: List[str], difficulty: str,
                                  num_questions: int, performance_data: Dict,
                                  coaching_insights: Dict, content_recommendations: Dict) -> str:
        """Build comprehensive quiz generation prompt"""

        context_info = f"""
        User Performance Context:
        - Average Score: {performance_data.get('average_score', 0):.2f}
        - Total Quizzes: {performance_data.get('total_quizzes', 0)}
        - Weak Topics: {performance_data.get('performance_summary', {}).get('weak_topics', [])}

        Coaching Insights: {json.dumps(coaching_insights, indent=2) if coaching_insights else 'None'}

        Content Recommendations: {json.dumps(content_recommendations, indent=2) if content_recommendations else 'None'}
        """

        return f"""Generate {num_questions} adaptive multiple-choice questions for {cert_id} certification exam.

        Context Information:
        {context_info}

        Topics: {', '.join(topics)}
        Target Difficulty: {difficulty}

        Requirements:
        - Questions should be appropriate for the user's skill level
        - Focus on weak areas identified in performance data
        - Include practical scenarios and code examples where relevant
        - Ensure questions align with exam objectives

        IMPORTANT: Return ONLY a valid JSON array with this exact structure:
        [
          {{
            "question": "question text here",
            "code": "optional code snippet",
            "language": "python|javascript|terraform|yaml|bash",
            "options": ["A) option 1", "B) option 2", "C) option 3", "D) option 4"],
            "correct_answer": "A",
            "explanation": "why this answer is correct",
            "topic": "{topics[0] if topics else 'general'}"
          }}
        ]

        Do NOT include any markdown, code blocks, or extra text. Return ONLY the JSON array."""

    def _parse_questions_response(self, response: str) -> List[Dict]:
        """Parse and validate questions from LLM response"""
        # Remove markdown code blocks if present
        if response.startswith('```'):
            response = response.split('```')[1]
            if response.startswith('json'):
                response = response[4:]
            response = response.strip()

        try:
            questions = json.loads(response)

            # Validate structure
            if not isinstance(questions, list) or len(questions) == 0:
                return []

            # Ensure each question has required fields
            for q in questions:
                if not all(k in q for k in ["question", "options", "correct_answer"]):
                    return []

            return questions

        except (json.JSONDecodeError, ValueError):
            logger.error("failed_to_parse_questions", response=response[:500])
            return []

    async def generate_targeted_quiz(self, user_id: str, cert_id: str, weak_topics: List[str],
                                   performance_data: Dict) -> Dict[str, Any]:
        """Generate quiz specifically targeting weak areas (used by orchestrator)"""
        params = {
            "topics": weak_topics,
            "num_questions": min(10, len(weak_topics) * 2),
            "difficulty": "medium"
        }

        return await self.generate_quiz_autonomous(user_id, cert_id, params)

    # Legacy method for backward compatibility
    async def generate_quiz(self, user_id: str, cert_id: str, params: Dict) -> Dict[str, Any]:
        """Legacy method - now uses autonomous generation"""
        return await self.generate_quiz_autonomous(user_id, cert_id, params)


class LearningCoachAgent:
    """Agent 3: Autonomous Learning Coach with A2A capabilities"""

    def __init__(self, mongo_client: MongoClient, gemini_model: Gemini, orchestrator: 'AgentOrchestrator'):
        self.db = mongo_client["campus-plateform"]
        self.model = gemini_model
        self.orchestrator = orchestrator
        self.scores_coll = self.db["scores"]
        self.user_performance_coll = self.db["user_performance"]
        self.name = "learning_coach"

        # Autonomous tools
        self.tools = {
            "database_query": self.orchestrator.shared_tools["database_query"],
            "content_analysis": self.orchestrator.shared_tools["content_analysis"]
        }

        # Create enhanced LLM agent
        self.agent = LlmAgent(
            name="learning_coach",
            model=gemini_model,
            instruction=self._get_agent_instruction()
        )

        logger.info("learning_coach_agent_initialized_with_a2a")

    def _get_agent_instruction(self) -> str:
        return """
        You are an autonomous Learning Coach Agent specializing in certification exam preparation.

        Your capabilities:
        1. Analyze student performance patterns and learning progress
        2. Provide personalized study recommendations and coaching
        3. Collaborate with Assessment Engine for performance insights
        4. Consult Content Curator for learning material recommendations
        5. Create adaptive study plans based on comprehensive data analysis

        Autonomous behaviors:
        - Query performance databases to understand learning patterns
        - Collaborate with other agents for holistic coaching approach
        - Use AI analysis to identify knowledge gaps and learning opportunities
        - Generate personalized study schedules and motivational guidance

        Always provide supportive, specific, and actionable coaching.
        Base recommendations on data-driven insights from user performance.
        Collaborate effectively with other agents for comprehensive learning support.
        """

    async def provide_coaching_autonomous(self, user_id: str, cert_id: str) -> Dict[str, Any]:
        """Autonomous coaching with A2A collaboration"""
        logger.info("autonomous_coaching", user_id=user_id, cert_id=cert_id)

        # Step 1: Analyze comprehensive performance data
        performance_analysis = await self.analyze_performance(user_id, cert_id)

        # Step 2: Consult Assessment Engine for quiz performance insights
        assessment_insights = await self.orchestrator.collaborate_on_task(
            self.name,
            AgentCapability.QUIZ_EVALUATION,
            {
                "user_id": user_id,
                "cert_id": cert_id,
                "request_type": "coaching_insights"
            }
        )

        # Step 3: Get content recommendations from Content Curator
        content_recommendations = await self.orchestrator.collaborate_on_task(
            self.name,
            AgentCapability.STUDY_RECOMMENDATION,
            {
                "user_id": user_id,
                "cert_id": cert_id,
                "performance_data": performance_analysis,
                "request_type": "study_materials"
            }
        )

        # Step 4: Generate comprehensive coaching advice
        coaching_advice = await self._generate_comprehensive_coaching(
            user_id, cert_id, performance_analysis, assessment_insights, content_recommendations
        )

        # Step 5: Update performance tracking with new insights
        await self._update_performance_tracking(user_id, cert_id, {
            "last_coaching": datetime.now(),
            "assessment_insights_used": bool(assessment_insights),
            "content_recommendations_used": bool(content_recommendations),
            "autonomous_coaching": True
        })

        return {
            "performance_analysis": performance_analysis,
            "coaching_advice": coaching_advice,
            "recommendations": {
                "study_materials": content_recommendations,
                "assessment_strategy": assessment_insights
            },
            "readiness_level": self._calculate_readiness_level(performance_analysis),
            "collaboration_used": {
                "assessment_engine": bool(assessment_insights),
                "content_curator": bool(content_recommendations)
            }
        }

    async def analyze_performance(self, user_id: str, cert_id: str) -> Dict[str, Any]:
        """Comprehensive performance analysis using database tools"""
        # Get recent quiz scores
        scores_result = await self.tools["database_query"].execute(
            collection="scores",
            query={"user_id": user_id, "cert_id": cert_id},
            limit=20
        )

        # Get performance tracking
        performance_result = await self.tools["database_query"].execute(
            collection="user_performance",
            query={"user_id": user_id, "cert_id": cert_id},
            limit=1
        )

        scores = scores_result.get("results", []) if scores_result["success"] else []
        performance = performance_result.get("results", [{}]) if performance_result["success"] else [{}]

        # Analyze performance patterns
        analysis = await self._analyze_performance_patterns(scores, performance[0] if performance else {})

        return {
            "total_quizzes": len(scores),
            "average_score": sum(s.get("score", 0) for s in scores) / len(scores) if scores else 0,
            "recent_scores": scores[-5:],  # Last 5 quizzes
            "weak_topics": analysis.get("weak_topics", []),
            "strengths": analysis.get("strengths", []),
            "improvement_trend": analysis.get("trend", "stable"),
            "study_streak": analysis.get("streak", 0)
        }

    async def _analyze_performance_patterns(self, scores: List[Dict], performance: Dict) -> Dict[str, Any]:
        """Use AI to analyze performance patterns"""
        if not scores:
            return {"weak_topics": [], "strengths": [], "trend": "no_data", "streak": 0}

        # Prepare data for AI analysis
        performance_summary = {
            "total_quizzes": len(scores),
            "average_score": sum(s.get("score", 0) for s in scores) / len(scores),
            "recent_scores": [s.get("score", 0) for s in scores[-5:]],
            "existing_weak_topics": performance.get("weak_topics", [])
        }

        analysis_prompt = f"""
        Analyze this student's performance data for certification exam preparation:

        {json.dumps(performance_summary, indent=2)}

        Identify:
        1. Weak topic areas that need focus
        2. Strong areas to leverage
        3. Performance trend (improving, declining, stable)
        4. Current study streak (consecutive quizzes with score >= 0.7)

        Return analysis as JSON with keys: weak_topics, strengths, trend, streak
        """

        analysis_result = await self.tools["content_analysis"].execute(
            content=json.dumps(performance_summary),
            task=analysis_prompt
        )

        if analysis_result["success"]:
            try:
                analysis_text = analysis_result["analysis"]
                start = analysis_text.find('{')
                end = analysis_text.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = analysis_text[start:end]
                    return json.loads(json_str)
            except:
                pass

        # Fallback analysis
        avg_score = performance_summary["average_score"]
        return {
            "weak_topics": performance.get("weak_topics", []),
            "strengths": ["general_knowledge"] if avg_score > 0.7 else [],
            "trend": "stable",
            "streak": sum(1 for s in performance_summary["recent_scores"] if s >= 0.7)
        }

    async def _generate_comprehensive_coaching(self, user_id: str, cert_id: str,
                                             performance: Dict, assessment_insights: Dict,
                                             content_recommendations: Dict) -> str:
        """Generate comprehensive coaching advice using all available data"""

        context_data = {
            "performance": performance,
            "assessment_insights": assessment_insights if assessment_insights else {},
            "content_recommendations": content_recommendations if content_recommendations else {},
            "certification": cert_id
        }

        coaching_prompt = f"""
        Provide comprehensive coaching advice for certification exam preparation.

        Student Context:
        {json.dumps(context_data, indent=2)}

        Create personalized coaching that includes:
        1. Performance summary and progress assessment
        2. Specific areas needing improvement
        3. Targeted study recommendations
        4. Weekly study schedule
        5. Motivational guidance and tips
        6. Next steps for immediate action

        Make the advice supportive, specific, and actionable.
        Consider the assessment insights and content recommendations provided.
        """

        # Use Gemini for coaching generation
        import google.generativeai as genai
        import os
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        gen_model = genai.GenerativeModel('gemini-2.5-flash-lite')
        response = gen_model.generate_content(coaching_prompt)

        return response.text

    async def create_study_plan(self, user_id: str, cert_id: str, materials: Dict,
                              quiz: Dict, performance: Dict) -> Dict[str, Any]:
        """Create personalized study plan (used by orchestrator)"""

        plan_context = {
            "performance": performance,
            "available_materials": materials,
            "upcoming_quiz": quiz,
            "weak_topics": performance.get("weak_topics", [])
        }

        plan_prompt = f"""
        Create a 7-day personalized study plan for certification exam preparation.

        Context:
        {json.dumps(plan_context, indent=2)}

        Generate a detailed daily schedule that:
        1. Focuses on weak areas identified in performance data
        2. Incorporates available study materials
        3. Includes time for quiz practice
        4. Balances different types of learning activities
        5. Includes rest and review time

        Return as JSON with keys: daily_schedule (array of 7 days), focus_areas, estimated_time_per_day
        """

        plan_result = await self.tools["content_analysis"].execute(
            content=json.dumps(plan_context),
            task=plan_prompt
        )

        if plan_result["success"]:
            try:
                plan_text = plan_result["analysis"]
                start = plan_text.find('{')
                end = plan_text.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = plan_text[start:end]
                    return json.loads(json_str)
            except:
                pass

        # Fallback plan
        return {
            "daily_schedule": [
                "Review weak topics and practice questions",
                "Study new materials and take notes",
                "Mixed practice: theory + hands-on",
                "Focus on practical scenarios",
                "Comprehensive review session",
                "Mock exam practice",
                "Light review and rest"
            ],
            "focus_areas": performance.get("weak_topics", ["general_review"]),
            "estimated_time_per_day": "2-3 hours"
        }

    async def _update_performance_tracking(self, user_id: str, cert_id: str, updates: Dict):
        """Update performance tracking with new data"""
        self.user_performance_coll.update_one(
            {"user_id": user_id, "cert_id": cert_id},
            {"$set": updates},
            upsert=True
        )

    def _calculate_readiness_level(self, performance: Dict) -> str:
        """Calculate exam readiness level"""
        avg_score = performance.get("average_score", 0)
        total_quizzes = performance.get("total_quizzes", 0)
        streak = performance.get("study_streak", 0)

        if avg_score >= 0.85 and total_quizzes >= 10 and streak >= 3:
            return "exam_ready"
        elif avg_score >= 0.75 and total_quizzes >= 5:
            return "good_progress"
        elif avg_score >= 0.6:
            return "needs_focus"
        else:
            return "needs_improvement"

    # Legacy method for backward compatibility
    async def provide_coaching(self, user_id: str, cert_id: str) -> Dict[str, Any]:
        """Legacy method - now uses autonomous coaching"""
        return await self.provide_coaching_autonomous(user_id, cert_id)
