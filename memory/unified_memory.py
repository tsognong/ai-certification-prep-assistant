"""
Unified Memory System

Manages different types of memory for personalized learning:
- Short-term: Current session context
- Episodic: Historical quiz attempts
- Semantic: Concept embeddings and relationships
- Procedural: User learning patterns
- Prospective: Scheduled reminders and reviews
"""
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from datetime import datetime, timedelta
import json
import structlog

logger = structlog.get_logger()


class UnifiedMemorySystem:
    """Central memory management for all agents"""
    
    def __init__(self, mongo_client: MongoClient, db_name: str = "campus-plateform"):
        self.db = mongo_client[db_name]
        
        # Memory collections
        self.short_term_coll = self.db["memory_short_term"]
        self.episodic_coll = self.db["memory_episodic"]
        self.semantic_coll = self.db["embeddings"]  # Reuse embeddings
        self.procedural_coll = self.db["memory_procedural"]
        self.prospective_coll = self.db["memory_prospective"]
        
        # Ensure indexes
        self._ensure_indexes()
        
        logger.info("unified_memory_system_initialized")
    
    def _ensure_indexes(self):
        """Create necessary indexes for performance"""
        # Short-term memory (expires after 24 hours)
        self.short_term_coll.create_index("user_id")
        self.short_term_coll.create_index("created_at", expireAfterSeconds=86400)  # 24h TTL
        
        # Episodic memory
        self.episodic_coll.create_index([("user_id", 1), ("timestamp", -1)])
        self.episodic_coll.create_index("event_type")
        
        # Procedural memory
        self.procedural_coll.create_index("user_id", unique=True)
        
        # Prospective memory
        self.prospective_coll.create_index([("user_id", 1), ("scheduled_for", 1)])
        self.prospective_coll.create_index("completed")
    
    # ==================== Short-term Memory ====================
    
    def store_short_term(self, user_id: str, key: str, value: Any):
        """Store temporary session data (expires in 24h)"""
        self.short_term_coll.update_one(
            {"user_id": user_id, "key": key},
            {
                "$set": {
                    "value": value,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            },
            upsert=True
        )
        logger.debug("short_term_stored", user_id=user_id, key=key)
    
    def get_short_term(self, user_id: str, key: str) -> Optional[Any]:
        """Retrieve short-term memory"""
        doc = self.short_term_coll.find_one({"user_id": user_id, "key": key})
        return doc.get("value") if doc else None
    
    def get_session_context(self, user_id: str) -> Dict[str, Any]:
        """Get all short-term memory for current session"""
        context = {}
        for doc in self.short_term_coll.find({"user_id": user_id}):
            context[doc["key"]] = doc["value"]
        return context
    
    # ==================== Episodic Memory ====================
    
    def store_episode(self, user_id: str, event_type: str, data: Dict):
        """Store an event/experience (quiz attempt, study session, etc.)"""
        episode = {
            "user_id": user_id,
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now()
        }
        self.episodic_coll.insert_one(episode)
        logger.info("episode_stored", user_id=user_id, event_type=event_type)
        
        # Trigger memory consolidation periodically
        if self._should_consolidate(user_id):
            self._consolidate_memories(user_id)
    
    def get_recent_episodes(self, user_id: str, event_type: Optional[str] = None, 
                           limit: int = 10) -> List[Dict]:
        """Retrieve recent episodes"""
        query = {"user_id": user_id}
        if event_type:
            query["event_type"] = event_type
        
        return list(self.episodic_coll.find(query).sort("timestamp", -1).limit(limit))
    
    def get_episode_timeline(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get chronological timeline of user's activities"""
        cutoff = datetime.now() - timedelta(days=days)
        return list(self.episodic_coll.find({
            "user_id": user_id,
            "timestamp": {"$gte": cutoff}
        }).sort("timestamp", 1))
    
    # ==================== Semantic Memory ====================
    
    def store_concept(self, user_id: str, concept: str, understanding_level: float,
                     related_topics: List[str], notes: str = ""):
        """Store understanding of a concept"""
        # This integrates with embedding store for semantic search
        self.semantic_coll.update_one(
            {"user_id": user_id, "concept": concept},
            {
                "$set": {
                    "understanding_level": understanding_level,
                    "related_topics": related_topics,
                    "notes": notes,
                    "updated_at": datetime.now()
                }
            },
            upsert=True
        )
    
    def get_concept_understanding(self, user_id: str, concept: str) -> Optional[Dict]:
        """Retrieve user's understanding of a concept"""
        return self.semantic_coll.find_one({"user_id": user_id, "concept": concept})
    
    def get_weak_concepts(self, user_id: str, threshold: float = 0.6) -> List[str]:
        """Identify concepts user struggles with"""
        weak = self.semantic_coll.find({
            "user_id": user_id,
            "understanding_level": {"$lt": threshold}
        })
        return [doc["concept"] for doc in weak]
    
    # ==================== Procedural Memory ====================
    
    def update_learning_patterns(self, user_id: str, patterns: Dict):
        """Track user's learning behaviors and preferences"""
        self.procedural_coll.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    **patterns,
                    "last_updated": datetime.now()
                }
            },
            upsert=True
        )
    
    def get_learning_patterns(self, user_id: str) -> Dict:
        """Get user's learning patterns (preferences, habits, etc.)"""
        doc = self.procedural_coll.find_one({"user_id": user_id})
        if doc:
            doc.pop("_id", None)
            return doc
        
        # Default patterns
        return {
            "preferred_difficulty": "medium",
            "preferred_time_of_day": "evening",
            "average_session_duration_minutes": 30,
            "preferred_question_types": ["mcq"],
            "learning_pace": "moderate"
        }
    
    def infer_preferences(self, user_id: str):
        """Infer user preferences from their behavior"""
        episodes = self.get_recent_episodes(user_id, limit=50)
        
        if not episodes:
            return
        
        # Analyze patterns
        difficulties = []
        session_times = []
        durations = []
        
        for episode in episodes:
            if episode["event_type"] == "quiz_attempt":
                data = episode["data"]
                difficulties.append(data.get("difficulty", "medium"))
                
                timestamp = episode["timestamp"]
                session_times.append(timestamp.hour)
                
                if "duration_minutes" in data:
                    durations.append(data["duration_minutes"])
        
        # Calculate preferences
        patterns = {}
        
        if difficulties:
            patterns["preferred_difficulty"] = max(set(difficulties), key=difficulties.count)
        
        if session_times:
            avg_hour = sum(session_times) / len(session_times)
            if avg_hour < 12:
                patterns["preferred_time_of_day"] = "morning"
            elif avg_hour < 18:
                patterns["preferred_time_of_day"] = "afternoon"
            else:
                patterns["preferred_time_of_day"] = "evening"
        
        if durations:
            patterns["average_session_duration_minutes"] = sum(durations) / len(durations)
        
        # Update
        self.update_learning_patterns(user_id, patterns)
        logger.info("preferences_inferred", user_id=user_id, patterns=patterns)
    
    # ==================== Prospective Memory ====================
    
    def schedule_review(self, user_id: str, topic: str, scheduled_for: datetime,
                       priority: str = "medium"):
        """Schedule a future review (spaced repetition)"""
        self.prospective_coll.insert_one({
            "user_id": user_id,
            "type": "review",
            "topic": topic,
            "scheduled_for": scheduled_for,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now()
        })
        logger.info("review_scheduled", user_id=user_id, topic=topic, when=scheduled_for)
    
    def get_due_reviews(self, user_id: str) -> List[Dict]:
        """Get reviews that are due now"""
        return list(self.prospective_coll.find({
            "user_id": user_id,
            "type": "review",
            "scheduled_for": {"$lte": datetime.now()},
            "completed": False
        }).sort("priority", -1))
    
    def mark_review_completed(self, review_id: str):
        """Mark a review as completed"""
        self.prospective_coll.update_one(
            {"_id": review_id},
            {
                "$set": {
                    "completed": True,
                    "completed_at": datetime.now()
                }
            }
        )
    
    def schedule_spaced_repetition(self, user_id: str, topic: str, 
                                   performance_level: float):
        """
        Schedule future reviews using spaced repetition algorithm
        
        performance_level: 0.0 (failed) to 1.0 (perfect)
        """
        # Simple SM-2 inspired algorithm
        if performance_level >= 0.9:
            intervals = [7, 14, 30]  # days
        elif performance_level >= 0.7:
            intervals = [3, 7, 14]
        else:
            intervals = [1, 3, 7]
        
        for days in intervals:
            scheduled_for = datetime.now() + timedelta(days=days)
            self.schedule_review(user_id, topic, scheduled_for, 
                               priority="high" if performance_level < 0.6 else "medium")
    
    # ==================== Memory Consolidation ====================
    
    def _should_consolidate(self, user_id: str) -> bool:
        """Check if it's time to consolidate memories"""
        last_consolidation = self.procedural_coll.find_one({"user_id": user_id})
        
        if not last_consolidation:
            return True
        
        last_time = last_consolidation.get("last_consolidation", datetime.min)
        return (datetime.now() - last_time) > timedelta(hours=24)
    
    def _consolidate_memories(self, user_id: str):
        """
        Consolidate episodic memories into semantic/procedural memory
        Similar to how human brain consolidates during sleep
        """
        logger.info("consolidating_memories", user_id=user_id)
        
        # Get recent episodes
        episodes = self.get_recent_episodes(user_id, limit=100)
        
        # Analyze for concept understanding
        topic_performance = {}
        for episode in episodes:
            if episode["event_type"] == "quiz_attempt":
                data = episode["data"]
                for answer in data.get("answers", []):
                    topic = answer.get("topic", "general")
                    
                    if topic not in topic_performance:
                        topic_performance[topic] = {"correct": 0, "total": 0}
                    
                    topic_performance[topic]["total"] += 1
                    if answer.get("is_correct", False):
                        topic_performance[topic]["correct"] += 1
        
        # Update semantic memory
        for topic, perf in topic_performance.items():
            understanding = perf["correct"] / perf["total"] if perf["total"] > 0 else 0.5
            self.store_concept(user_id, topic, understanding, [], 
                             f"Based on {perf['total']} attempts")
        
        # Infer procedural patterns
        self.infer_preferences(user_id)
        
        # Update consolidation timestamp
        self.procedural_coll.update_one(
            {"user_id": user_id},
            {"$set": {"last_consolidation": datetime.now()}},
            upsert=True
        )
        
        logger.info("consolidation_complete", user_id=user_id, 
                   topics_analyzed=len(topic_performance))
    
    # ==================== Cross-device Continuity ====================
    
    def get_user_state(self, user_id: str) -> Dict[str, Any]:
        """Get complete user state for cross-device sync"""
        return {
            "session_context": self.get_session_context(user_id),
            "recent_activity": self.get_recent_episodes(user_id, limit=5),
            "learning_patterns": self.get_learning_patterns(user_id),
            "due_reviews": self.get_due_reviews(user_id),
            "weak_concepts": self.get_weak_concepts(user_id)
        }
    
    def clear_user_data(self, user_id: str):
        """Clear all memory for a user (GDPR compliance)"""
        self.short_term_coll.delete_many({"user_id": user_id})
        self.episodic_coll.delete_many({"user_id": user_id})
        self.semantic_coll.delete_many({"user_id": user_id})
        self.procedural_coll.delete_many({"user_id": user_id})
        self.prospective_coll.delete_many({"user_id": user_id})
        
        logger.info("user_data_cleared", user_id=user_id)
