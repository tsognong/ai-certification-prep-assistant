"""
Embedding Storage and Semantic Search using MongoDB

Stores document embeddings for semantic similarity search
without requiring external vector databases.
Uses Google Gemini API for embeddings (lightweight, no CUDA dependencies).
"""
from typing import List, Dict, Any, Optional
from pymongo import MongoClient, ASCENDING
import numpy as np
from datetime import datetime
import hashlib
import google.generativeai as genai
import os


class EmbeddingStore:
    """Manages document embeddings in MongoDB using Gemini API"""
    
    def __init__(self, mongo_client: MongoClient, db_name: str = "campus-plateform"):
        self.db = mongo_client[db_name]
        self.embeddings_collection = self.db["embeddings"]
        
        # Configure Gemini for embeddings (no heavy dependencies!)
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Create indexes
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create necessary indexes"""
        self.embeddings_collection.create_index([("certification_id", ASCENDING)])
        self.embeddings_collection.create_index([("topic", ASCENDING)])
        self.embeddings_collection.create_index([("content_hash", ASCENDING)], unique=True)
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate unique hash for content"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Gemini API (no CUDA needed!)"""
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Fallback: return zero vector
            return [0.0] * 768
    
    def store_document(
        self,
        content: str,
        certification_id: str,
        topic: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """Store document with its embedding"""
        
        # Generate embedding using Gemini API (lightweight!)
        embedding = self._generate_embedding(content)
        content_hash = self._generate_content_hash(content)
        
        doc = {
            "_id": content_hash,
            "content": content,
            "embedding": embedding,
            "certification_id": certification_id,
            "topic": topic,
            "metadata": metadata or {},
            "created_at": datetime.now(),
            "vector_dim": len(embedding)
        }
        
        # Upsert to avoid duplicates
        self.embeddings_collection.update_one(
            {"_id": content_hash},
            {"$set": doc},
            upsert=True
        )
        
        return content_hash
    
    def batch_store_documents(
        self,
        documents: List[Dict[str, Any]],
        certification_id: str
    ) -> int:
        """Store multiple documents at once"""
        
        stored_count = 0
        for doc in documents:
            try:
                self.store_document(
                    content=doc["content"],
                    certification_id=certification_id,
                    topic=doc.get("topic", "general"),
                    metadata=doc.get("metadata", {})
                )
                stored_count += 1
            except Exception as e:
                print(f"Error storing document: {e}")
                continue
        
        return stored_count
    
    def semantic_search(
        self,
        query: str,
        certification_id: Optional[str] = None,
        topic: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using cosine similarity
        
        Args:
            query: Search query text
            certification_id: Filter by certification
            topic: Filter by topic
            top_k: Number of results to return
            
        Returns:
            List of documents with similarity scores
        """
        
        # Generate query embedding using Gemini
        query_embedding = np.array(self._generate_embedding(query))
        
        # Build filter
        filter_query = {}
        if certification_id:
            filter_query["certification_id"] = certification_id
        if topic:
            filter_query["topic"] = topic
        
        # Fetch all documents matching filter
        documents = list(self.embeddings_collection.find(filter_query))
        
        if not documents:
            return []
        
        # Calculate cosine similarity
        results = []
        for doc in documents:
            doc_embedding = np.array(doc["embedding"])
            
            # Cosine similarity
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            
            results.append({
                "content": doc["content"],
                "similarity": float(similarity),
                "topic": doc["topic"],
                "certification_id": doc["certification_id"],
                "metadata": doc.get("metadata", {})
            })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def get_topic_documents(
        self,
        certification_id: str,
        topic: str
    ) -> List[Dict[str, Any]]:
        """Get all documents for a specific topic"""
        
        documents = self.embeddings_collection.find({
            "certification_id": certification_id,
            "topic": topic
        })
        
        return [
            {
                "content": doc["content"],
                "topic": doc["topic"],
                "metadata": doc.get("metadata", {})
            }
            for doc in documents
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get embedding storage statistics"""
        
        total_docs = self.embeddings_collection.count_documents({})
        
        # Count by certification
        pipeline = [
            {"$group": {
                "_id": "$certification_id",
                "count": {"$sum": 1}
            }}
        ]
        by_cert = list(self.embeddings_collection.aggregate(pipeline))
        
        return {
            "total_documents": total_docs,
            "by_certification": {item["_id"]: item["count"] for item in by_cert}
        }


class UserMemoryStore:
    """Stores user-specific memory (episodic, preferences, patterns)"""
    
    def __init__(self, mongo_client: MongoClient, db_name: str = "campus-plateform"):
        self.db = mongo_client[db_name]
        self.memory_collection = self.db["user_memory"]
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create indexes for efficient queries"""
        self.memory_collection.create_index([("user_id", ASCENDING), ("memory_type", ASCENDING)])
        self.memory_collection.create_index([("user_id", ASCENDING), ("timestamp", ASCENDING)])
    
    def store_episodic_memory(
        self,
        user_id: str,
        certification_id: str,
        event_type: str,
        data: Dict[str, Any]
    ):
        """Store episodic memory (quiz attempts, study sessions)"""
        
        memory_doc = {
            "user_id": user_id,
            "memory_type": "episodic",
            "certification_id": certification_id,
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now()
        }
        
        self.memory_collection.insert_one(memory_doc)
    
    def get_user_history(
        self,
        user_id: str,
        certification_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user's episodic memory (history)"""
        
        query = {"user_id": user_id, "memory_type": "episodic"}
        if certification_id:
            query["certification_id"] = certification_id
        
        return list(
            self.memory_collection
            .find(query)
            .sort("timestamp", -1)
            .limit(limit)
        )
    
    def store_procedural_memory(
        self,
        user_id: str,
        pattern_type: str,
        pattern_data: Dict[str, Any]
    ):
        """Store procedural memory (learned patterns, preferences)"""
        
        self.memory_collection.update_one(
            {
                "user_id": user_id,
                "memory_type": "procedural",
                "pattern_type": pattern_type
            },
            {
                "$set": {
                    "pattern_data": pattern_data,
                    "updated_at": datetime.now()
                },
                "$setOnInsert": {
                    "created_at": datetime.now()
                }
            },
            upsert=True
        )
    
    def get_procedural_memory(
        self,
        user_id: str,
        pattern_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get procedural memory (user patterns)"""
        
        doc = self.memory_collection.find_one({
            "user_id": user_id,
            "memory_type": "procedural",
            "pattern_type": pattern_type
        })
        
        return doc.get("pattern_data") if doc else None
    
    def analyze_user_patterns(self, user_id: str, certification_id: str) -> Dict[str, Any]:
        """Analyze user learning patterns from episodic memory"""
        
        history = self.get_user_history(user_id, certification_id)
        
        if not history:
            return {
                "total_sessions": 0,
                "average_score": 0,
                "weak_topics": [],
                "strong_topics": [],
                "preferred_difficulty": "medium"
            }
        
        # Analyze quiz performance
        quiz_sessions = [h for h in history if h["event_type"] == "quiz_completed"]
        
        total_sessions = len(quiz_sessions)
        scores = [s["data"].get("score", 0) for s in quiz_sessions]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Topic performance
        topic_performance = {}
        for session in quiz_sessions:
            for topic, perf in session["data"].get("topic_breakdown", {}).items():
                if topic not in topic_performance:
                    topic_performance[topic] = []
                topic_performance[topic].append(perf)
        
        # Calculate average per topic
        topic_averages = {
            topic: sum(scores) / len(scores)
            for topic, scores in topic_performance.items()
        }
        
        # Identify weak and strong topics
        sorted_topics = sorted(topic_averages.items(), key=lambda x: x[1])
        weak_topics = [t[0] for t in sorted_topics[:3]]
        strong_topics = [t[0] for t in sorted_topics[-3:]]
        
        # Determine preferred difficulty
        difficulties = [s["data"].get("difficulty", "medium") for s in quiz_sessions]
        preferred_difficulty = max(set(difficulties), key=difficulties.count) if difficulties else "medium"
        
        return {
            "total_sessions": total_sessions,
            "average_score": round(average_score, 2),
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "preferred_difficulty": preferred_difficulty,
            "last_session": quiz_sessions[0]["timestamp"] if quiz_sessions else None
        }
