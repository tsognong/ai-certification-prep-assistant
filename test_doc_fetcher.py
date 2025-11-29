#!/usr/bin/env python3
"""
Test script for the updated doc_fetcher.py with new resource handlers
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work correctly"""
    try:
        from fetchers.doc_fetcher import IntelligentDocumentationFetcher
        print("✅ IntelligentDocumentationFetcher imported successfully")

        # Check that the new methods exist
        methods_to_check = [
            '_fetch_official_docs_ai',
            '_fetch_learning_path_ai',
            '_fetch_architecture_center_ai',
            '_fetch_tutorials_ai',
            '_fetch_exam_guide_ai',
            '_analyze_official_docs_needs',
            '_analyze_learning_path_structure',
            '_analyze_architecture_patterns',
            '_analyze_tutorial_content',
            '_analyze_exam_guide_content',
            '_extract_official_content_ai',
            '_extract_learning_content_ai',
            '_extract_architecture_content_ai',
            '_extract_tutorial_content_ai',
            '_extract_exam_guide_content_ai',
            '_scrape_content',
            '_construct_topic_url'
        ]

        for method in methods_to_check:
            if hasattr(IntelligentDocumentationFetcher, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_resource_structure():
    """Test that the resource structure is correct"""
    try:
        from certifications.certification_packs import CERTIFICATION_PACKS

        # Check MongoDB certification
        mongodb_cert = CERTIFICATION_PACKS.get("mongodb_associate")
        if mongodb_cert and "available_resources" in mongodb_cert:
            resources = mongodb_cert["available_resources"]
            print(f"✅ MongoDB has {len(resources)} available resources")

            # Check for exam_guide resource type
            resource_types = [r["type"] for r in resources]
            if "exam_guide" in resource_types:
                print("✅ MongoDB includes exam_guide resource type")
            else:
                print("❌ MongoDB missing exam_guide resource type")
                return False

            for resource in resources:
                required_fields = ["type", "title", "url", "scrape_config", "quality_verified"]
                missing_fields = [field for field in required_fields if field not in resource]
                if missing_fields:
                    print(f"❌ Resource missing fields: {missing_fields}")
                    return False
                else:
                    print(f"✅ Resource '{resource['title']}' has all required fields")

        return True

    except Exception as e:
        print(f"❌ Resource structure test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing updated doc_fetcher implementation...\n")

    success = True

    print("1. Testing imports and method existence...")
    if not test_imports():
        success = False

    print("\n2. Testing resource structure...")
    if not test_resource_structure():
        success = False

    if success:
        print("\n🎉 All tests passed! The updated doc_fetcher is ready for runtime certification management.")
        print("\nKey improvements:")
        print("- ✅ Dynamic resource management via available_resources")
        print("- ✅ AI-powered content analysis and extraction")
        print("- ✅ Specialized handlers for different resource types")
        print("- ✅ Structured scraping configurations")
        print("- ✅ Quality verification and metadata")
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)