#!/usr/bin/env python3
"""
Quick environment and setup checker for the AI Quiz System.
Run this before starting the Streamlit app to verify your setup.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_env_vars():
    """Check required environment variables."""
    print("🔍 Checking environment variables...")
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    mongo_uri = os.environ.get("MONGO_URI")
    
    if not gemini_key:
        print("  ❌ GEMINI_API_KEY is not set")
        print("     Run: export GEMINI_API_KEY='your_key_here'")
        return False
    else:
        print(f"  ✅ GEMINI_API_KEY is set (length: {len(gemini_key)} chars)")
    
    if not mongo_uri:
        print("  ❌ MONGO_URI is not set")
        print("     Run: export MONGO_URI='your_mongodb_uri_here'")
        return False
    else:
        print(f"  ✅ MONGO_URI is set")
        # Basic validation
        if not mongo_uri.startswith("mongodb"):
            print("     ⚠️  Warning: URI should start with 'mongodb://' or 'mongodb+srv://'")
    
    return True

def check_dependencies():
    """Check if required packages are installed."""
    print("\n🔍 Checking Python dependencies...")
    
    required = ["streamlit", "pymongo"]
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"  ✅ {pkg} is installed")
        except ImportError:
            print(f"  ❌ {pkg} is NOT installed")
            missing.append(pkg)
    
    # Check google_adk (might not exist)
    try:
        __import__("google_adk")
        print(f"  ✅ google_adk is installed")
    except ImportError:
        print(f"  ⚠️  google_adk is NOT installed")
        print(f"     Note: This is a placeholder. You may need to install the correct Google AI package.")
        print(f"     Try: pip install google-generativeai")
    
    if missing:
        print(f"\n  ⚠️  Run: pip install -r requirements.txt")
        return False
    
    return True

def check_data_files():
    """Check if data directory and .txt files exist."""
    print("\n🔍 Checking data files...")
    
    data_dir = Path(__file__).parent / "data"
    
    if not data_dir.exists():
        print(f"  ❌ data/ directory does not exist")
        print(f"     Create it: mkdir data")
        return False
    else:
        print(f"  ✅ data/ directory exists")
    
    txt_files = list(data_dir.glob("*.txt"))
    
    if not txt_files:
        print(f"  ⚠️  No .txt files found in data/")
        print(f"     Add course text files (e.g., day1.txt, day2.txt)")
        return False
    else:
        print(f"  ✅ Found {len(txt_files)} .txt file(s):")
        for f in txt_files:
            size_kb = f.stat().st_size / 1024
            print(f"     - {f.name} ({size_kb:.1f} KB)")
    
    return True

def test_mongodb_connection():
    """Test MongoDB connection."""
    print("\n🔍 Testing MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        mongo_uri = os.environ.get("MONGO_URI")
        
        if not mongo_uri:
            print("  ⏭️  Skipping (MONGO_URI not set)")
            return False
        
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Trigger connection
        #client.admin.command('ping')
        
        db_name = "campus-plateform"
        print(f"  ✅ Successfully connected to MongoDB")
        print(f"     Database: {db_name}")
        
        db = client[db_name]
        collections = db.list_collection_names()
        if collections:
            print(f"     Existing collections: {', '.join(collections)}")
        else:
            print(f"     No collections yet (will be created on first use)")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"  ❌ MongoDB connection failed: {e}")
        print(f"     - Check your MONGO_URI")
        print(f"     - Verify network access in MongoDB Atlas")
        print(f"     - Whitelist your IP address")
        return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("AI Course Quiz System - Setup Verification")
    print("=" * 60)
    
    results = []
    
    results.append(("Environment Variables", check_env_vars()))
    results.append(("Python Dependencies", check_dependencies()))
    results.append(("Data Files", check_data_files()))
    results.append(("MongoDB Connection", test_mongodb_connection()))
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    all_pass = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_pass = False
    
    print("=" * 60)
    
    if all_pass:
        print("\n🎉 All checks passed! You're ready to run the app:")
        print("   streamlit run app.py")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("   See TESTING.md for detailed troubleshooting steps.")
    
    print()
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
