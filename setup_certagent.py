#!/usr/bin/env python3
"""
Setup script for CertAgent

Initializes:
- Certification packs in MongoDB
- Documentation embeddings
- Database indexes
"""
import os
import sys
import asyncio
from pymongo import MongoClient
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from certifications.pack_loader import CertificationPackLoader
from memory.embedding_store import EmbeddingStore, UserMemoryStore
from fetchers.doc_fetcher import initialize_all_documentation


def main():
    """Run setup"""
    print("🚀 CertAgent Setup")
    print("=" * 50)
    
    # Get MongoDB connection
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("❌ MONGO_URI environment variable not set")
        print("   Please set MONGO_URI in .env file")
        sys.exit(1)
    
    print(f"📡 Connecting to MongoDB...")
    client = MongoClient(mongo_uri)
    
    try:
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        sys.exit(1)
    
    # Initialize certification packs
    print("\n📦 Initializing certification packs...")
    pack_loader = CertificationPackLoader(client)
    pack_loader.initialize_default_packs()
    
    packs = pack_loader.list_available_packs()
    print(f"✅ {len(packs)} certification packs initialized:")
    for pack in packs:
        print(f"   - {pack['display_name']}")
    
    # Initialize embedding store
    print("\n🧠 Setting up embedding storage...")
    embedding_store = EmbeddingStore(client)
    stats = embedding_store.get_statistics()
    print(f"✅ Embedding storage ready")
    print(f"   Total documents: {stats['total_documents']}")
    
    # Initialize user memory store
    print("\n💾 Setting up user memory system...")
    user_memory = UserMemoryStore(client)
    print("✅ User memory system ready")
    
    # Fetch and store documentation
    print("\n📚 Fetching certification documentation...")
    print("   This may take a few minutes...")
    
    asyncio.run(initialize_all_documentation(client))
    
    # Show final statistics
    stats = embedding_store.get_statistics()
    print(f"\n📊 Setup Summary:")
    print(f"   Certifications: {len(packs)}")
    print(f"   Documentation chunks: {stats['total_documents']}")
    print(f"   By certification:")
    for cert_id, count in stats.get('by_certification', {}).items():
        print(f"     - {cert_id}: {count} documents")
    
    print("\n✅ Setup complete!")
    print("\n🎯 Next steps:")
    print("   1. Set GEMINI_API_KEY in .env file")
    print("   2. Run: streamlit run app.py")
    print("   3. Sign in and start preparing for certifications!")
    
    client.close()


if __name__ == "__main__":
    main()
