"""
MongoDB Documentation Fetcher

Fetches MongoDB documentation pages from mongodb.com/docs/
and extracts relevant content for quiz generation.
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import time


# MongoDB documentation URL mappings for exam topics
# Based on MongoDB Developer Associate Exam Guide official sections
MONGO_DOC_URLS = {
    "MongoDB Overview and Document Model": [
        "https://www.mongodb.com/docs/manual/core/document/",
        "https://www.mongodb.com/docs/manual/reference/bson-types/",
        "https://www.mongodb.com/docs/manual/core/databases-and-collections/"
    ],
    "CRUD": [
        "https://www.mongodb.com/docs/manual/crud/",
        "https://www.mongodb.com/docs/manual/tutorial/insert-documents/",
        "https://www.mongodb.com/docs/manual/tutorial/query-documents/",
        "https://www.mongodb.com/docs/manual/tutorial/update-documents/",
        "https://www.mongodb.com/docs/manual/tutorial/remove-documents/",
        "https://www.mongodb.com/docs/manual/reference/method/db.collection.findAndModify/",
        "https://www.mongodb.com/docs/manual/aggregation/",
        "https://www.mongodb.com/docs/manual/core/aggregation-pipeline/"
    ],
    "Indexes": [
        "https://www.mongodb.com/docs/manual/indexes/",
        "https://www.mongodb.com/docs/manual/core/index-single/",
        "https://www.mongodb.com/docs/manual/core/index-compound/",
        "https://www.mongodb.com/docs/manual/core/index-multikey/",
        "https://www.mongodb.com/docs/manual/core/index-text/"
    ],
    "Data Modeling": [
        "https://www.mongodb.com/docs/manual/core/data-modeling-introduction/",
        "https://www.mongodb.com/docs/manual/core/data-model-design/",
        "https://www.mongodb.com/docs/manual/applications/data-models-relationships/"
    ],
    "Tools and Tooling": [
        "https://www.mongodb.com/docs/mongodb-shell/",
        "https://www.mongodb.com/docs/compass/",
        "https://www.mongodb.com/docs/atlas/",
        "https://www.mongodb.com/docs/database-tools/"
    ],
    "Drivers": [
        "https://www.mongodb.com/docs/drivers/java/sync/current/",
        "https://www.mongodb.com/docs/drivers/java/sync/current/quick-start/",
        "https://www.mongodb.com/docs/drivers/java/sync/current/usage-examples/",
        "https://www.mongodb.com/docs/drivers/java/sync/current/fundamentals/connection/",
        "https://www.mongodb.com/docs/drivers/java/sync/current/fundamentals/crud/"
    ]
}


def fetch_mongo_doc(url: str, timeout: int = 10) -> Optional[Dict[str, str]]:
    """
    Fetch MongoDB documentation page and extract content.
    
    Args:
        url: MongoDB documentation URL
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with 'url', 'title', 'content', 'code_blocks'
        Returns None if fetch fails
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Educational Quiz Generator)'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title_tag = soup.find('h1') or soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else "MongoDB Documentation"
        
        # Remove navigation, footer, and script tags
        for tag in soup.find_all(['nav', 'footer', 'script', 'style', 'aside']):
            tag.decompose()
        
        # Extract main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if not main_content:
            # Fallback to body
            main_content = soup.find('body')
        
        # Extract text content
        text_content = []
        if main_content:
            for p in main_content.find_all(['p', 'li', 'dt', 'dd']):
                text = p.get_text(strip=True)
                if text and len(text) > 10:  # Filter out very short snippets
                    text_content.append(text)
        
        # Extract code blocks
        code_blocks = []
        if main_content:
            for code in main_content.find_all(['code', 'pre']):
                code_text = code.get_text(strip=True)
                if code_text and len(code_text) > 5:
                    code_blocks.append(code_text)
        
        return {
            'url': url,
            'title': title,
            'content': '\n\n'.join(text_content),
            'code_blocks': code_blocks
        }
        
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return None


def fetch_docs_for_topics(topics: List[str], max_pages_per_topic: int = 3) -> Dict[str, List[Dict]]:
    """
    Fetch MongoDB documentation for selected topics.
    
    Args:
        topics: List of exam topics
        max_pages_per_topic: Maximum pages to fetch per topic
        
    Returns:
        Dictionary mapping topic to list of fetched documents
    """
    results = {}
    
    for topic in topics:
        if topic not in MONGO_DOC_URLS:
            continue
            
        topic_docs = []
        urls = MONGO_DOC_URLS[topic][:max_pages_per_topic]
        
        for url in urls:
            doc = fetch_mongo_doc(url)
            if doc:
                topic_docs.append(doc)
            # Be respectful - don't hammer the server
            time.sleep(0.5)
        
        if topic_docs:
            results[topic] = topic_docs
    
    return results


def get_available_mongo_topics() -> List[str]:
    """Get list of available MongoDB exam topics."""
    return sorted(MONGO_DOC_URLS.keys())


def format_docs_for_context(docs: Dict[str, List[Dict]]) -> str:
    """
    Format fetched documentation into context string for LLM.
    
    Args:
        docs: Dictionary of topics to document lists
        
    Returns:
        Formatted context string
    """
    context_parts = []
    
    for topic, topic_docs in docs.items():
        context_parts.append(f"\n{'='*80}")
        context_parts.append(f"TOPIC: {topic}")
        context_parts.append(f"{'='*80}\n")
        
        for doc in topic_docs:
            context_parts.append(f"\n--- {doc['title']} ---")
            context_parts.append(f"Source: {doc['url']}\n")
            context_parts.append(doc['content'][:3000])  # Limit content length
            
            if doc['code_blocks']:
                context_parts.append("\n--- Code Examples ---")
                for i, code in enumerate(doc['code_blocks'][:5], 1):  # Max 5 code blocks
                    context_parts.append(f"\nExample {i}:")
                    context_parts.append(code[:500])  # Limit code block length
            
            context_parts.append("\n")
    
    return '\n'.join(context_parts)
