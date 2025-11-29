"""
Content Retrieval Demo for Quiz Generation

This script demonstrates how the embedding store retrieves relevant content
for generating quiz questions and exam questions.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

def demonstrate_content_retrieval():
    """Demonstrate content retrieval for quiz generation"""

    print("=" * 70)
    print("🎯 Content Retrieval for Quiz Generation Demo")
    print("=" * 70)
    print()

    try:
        # Initialize MongoDB connection
        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            print("❌ MONGO_URI not found in environment")
            return

        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db_name = "campus-plateform"

        # Import and initialize embedding store
        from memory.embedding_store import EmbeddingStore
        embedding_store = EmbeddingStore(client, db_name)

        print("📊 Current Embedding Store Status:")
        stats = embedding_store.get_statistics()
        print(f"   Total documents: {stats['total_documents']}")
        print(f"   Certifications: {list(stats.get('by_certification', {}).keys())}")
        print()

        # Example topics for AI certification
        ai_topics = [
            "machine learning basics",
            "neural networks",
            "deep learning",
            "natural language processing",
            "computer vision",
            "AI ethics"
        ]

        print("🔍 Testing Content Retrieval for Quiz Generation")
        print("-" * 50)

        for topic in ai_topics[:3]:  # Test first 3 topics
            print(f"\n📝 Topic: '{topic}'")
            print("-" * 30)

            # Perform semantic search (like ContentCuratorAgent does)
            results = embedding_store.semantic_search(
                query=topic,
                certification_id="ai-fundamentals",  # Use the correct certification_id
                top_k=2
            )

            if results:
                print(f"✅ Found {len(results)} relevant documents:")
                for i, result in enumerate(results, 1):
                    similarity = result['similarity'] * 100
                    content_preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                    print(f"   {i}. Similarity: {similarity:.1f}%")
                    print(f"      Topic: {result['topic']}")
                    print(f"      Content: {content_preview}")
                    print()
            else:
                print("❌ No relevant content found in embedding store")
                print("   This would trigger fallback to certification pack data")
                print()

        # Demonstrate how this content would be used for question generation
        print("🎯 How Retrieved Content Powers Quiz Generation")
        print("-" * 50)

        # Simulate the quiz generation process
        selected_topic = "machine learning basics"
        print(f"Example: Generating questions for topic '{selected_topic}'")
        print()

        # Get relevant content
        context_docs = embedding_store.semantic_search(
            query=selected_topic,
            certification_id="ai-fundamentals",
            top_k=1
        )

        if context_docs:
            context = context_docs[0]['content']
            print("📚 Retrieved Context (first 500 chars):")
            print(context[:500] + "..." if len(context) > 500 else context)
            print()

            print("🤖 This context would be fed to AssessmentEngineAgent to generate:")
            print("   - Multiple Choice Questions (MCQ)")
            print("   - Multiple Select Questions (MSQ)")
            print("   - Scenario-based questions")
            print("   - Code comprehension questions")
            print()

            # Show example question structure
            print("📋 Example Question Structure:")
            print("""
{
  "question": "What is the primary goal of supervised learning?",
  "type": "mcq",
  "options": [
    "A) Learn patterns from unlabeled data",
    "B) Learn from labeled examples to make predictions",
    "C) Explore data without specific goals",
    "D) Generate new data samples"
  ],
  "correct_answer": ["B"],
  "explanation": "Supervised learning uses labeled training data to learn mappings from inputs to outputs",
  "difficulty": "easy",
  "topic": "machine learning basics"
}
""")

        print("🔄 Content Retrieval Flow:")
        print("   1. User requests quiz on specific topics")
        print("   2. ContentCuratorAgent performs semantic search")
        print("   3. Relevant documents retrieved based on similarity")
        print("   4. Context passed to AssessmentEngineAgent")
        print("   5. Questions generated using certification blueprint")
        print("   6. LearningCoachAgent adjusts difficulty based on user history")
        print()

        print("💡 Key Benefits:")
        print("   - Semantic search finds most relevant content")
        print("   - Questions based on actual course materials")
        print("   - Adaptive difficulty adjustment")
        print("   - Certification-standard question formats")
        print()

    except Exception as e:
        print(f"❌ Error in demonstration: {e}")
        import traceback
        traceback.print_exc()

def show_embedding_store_details():
    """Show detailed information about the embedding store"""

    print("\n" + "=" * 70)
    print("🔍 Embedding Store Details")
    print("=" * 70)

    try:
        mongo_uri = os.getenv("MONGO_URI")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db_name = "campus-plateform"

        from memory.embedding_store import EmbeddingStore
        store = EmbeddingStore(client, db_name)

        # Get all documents
        docs = list(store.embeddings_collection.find({}))

        print(f"📄 Total Documents: {len(docs)}")
        print()

        for doc in docs:
            print(f"Document ID: {doc['_id'][:16]}...")
            print(f"Topic: {doc['topic']}")
            print(f"Certification: {doc['certification_id']}")
            print(f"Content Length: {len(doc['content'])} characters")
            print(f"Word Count: {len(doc['content'].split())} words")
            print(f"Created: {doc.get('created_at', 'Unknown')}")
            if 'metadata' in doc and doc['metadata']:
                print(f"Metadata: {doc['metadata']}")
            print("-" * 50)

    except Exception as e:
        print(f"❌ Error getting details: {e}")

def main():
    """Main demonstration"""

    # Check environment
    required_vars = ["MONGO_URI", "GEMINI_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease set these in your .env file")
        sys.exit(1)

    # Run demonstration
    demonstrate_content_retrieval()

    # Show detailed store info if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--details":
        show_embedding_store_details()

if __name__ == "__main__":
    main()