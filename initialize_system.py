"""
CertAgent Initialization Script

Initializes the database with certification packs and sets up the system.
Run this once after setting up your environment variables.
"""
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import google.generativeai as genai

# Load environment variables
load_dotenv()

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        "MONGO_URI",
        "GEMINI_API_KEY"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\n📝 Please set these in your .env file")
        print("   See .env.example for reference")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_mongo_connection():
    """Test MongoDB connection"""
    try:
        mongo_uri = os.getenv("MONGO_URI")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()  # Force connection
        print("✅ MongoDB connection successful")
        return client
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return None

def test_gemini_api():
    """Test Gemini API key"""
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # Test with a simple embedding
        result = genai.embed_content(
            model="models/text-embedding-004",
            content="test",
            task_type="retrieval_document"
        )
        print("✅ Gemini API key is valid")
        return True
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def initialize_certification_packs(client):
    """Initialize certification packs in MongoDB"""
    try:
        from certifications.certification_packs import CertificationPackLoader
        
        loader = CertificationPackLoader(client)
        loader.initialize_packs()
        print("✅ Certification packs initialized")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize certification packs: {e}")
        return False

def create_indexes(client):
    """Create necessary database indexes"""
    try:
        db = client["campus-plateform"]
        
        # Users collection (skip if already exists)
        try:
            db["users"].create_index("email", unique=True, sparse=True)
        except:
            pass
        try:
            db["users"].create_index("google_id", unique=True, sparse=True)
        except:
            pass
        
        # Agent logs
        db["agent_logs"].create_index([("agent_name", 1), ("timestamp", -1)])
        db["agent_logs"].create_index("timestamp")
        
        # Agent metrics
        db["agent_metrics"].create_index([("agent_name", 1), ("metric_type", 1)])
        
        # Quizzes
        db["quizzes"].create_index([("user_id", 1), ("cert_id", 1)])
        db["quizzes"].create_index("generated_at")
        
        # Scores
        db["scores"].create_index([("user_id", 1), ("cert_id", 1)])
        db["scores"].create_index("submitted_at")
        
        # Memory collections
        db["memory_short_term"].create_index("user_id")
        db["memory_short_term"].create_index("created_at", expireAfterSeconds=86400)
        db["memory_episodic"].create_index([("user_id", 1), ("timestamp", -1)])
        db["memory_procedural"].create_index("user_id", unique=True)
        db["memory_prospective"].create_index([("user_id", 1), ("scheduled_for", 1)])
        
        print("✅ Database indexes created")
        return True
    except Exception as e:
        print(f"❌ Failed to create indexes: {e}")
        return False

def main():
    """Main initialization routine"""
    print("=" * 60)
    print("🚀 CertAgent Initialization")
    print("=" * 60)
    print()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    print()
    
    # Test MongoDB
    client = test_mongo_connection()
    if not client:
        sys.exit(1)
    
    print()
    
    # Test Gemini API
    if not test_gemini_api():
        sys.exit(1)
    
    print()
    print("-" * 60)
    print("Initializing database...")
    print("-" * 60)
    print()
    
    # Create indexes
    if not create_indexes(client):
        print("⚠️  Warning: Some indexes may not have been created")
    
    print()
    
    # Initialize certification packs
    if not initialize_certification_packs(client):
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✅ Initialization complete!")
    print("=" * 60)
    print()
    print("📚 Initialized Certifications:")
    print("   - MongoDB Developer Associate")
    print("   - AWS Solutions Architect Associate")
    print("   - HashiCorp Terraform Associate")
    print("   - Microsoft Azure Fundamentals")
    print("   - Google Cloud Associate Engineer")
    print()
    print("🎯 Next steps:")
    print("   1. Run: streamlit run app.py")
    print("   2. Open: http://localhost:8501")
    print("   3. Start preparing for your certification!")
    print()

if __name__ == "__main__":
    main()
