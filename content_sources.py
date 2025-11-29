"""
Content Sources Configuration

This file defines the sources for runtime content retrieval
for different certifications. Used by the runtime content loader.
"""

CONTENT_SOURCES = {
    "ai-fundamentals": {
        "description": "Google AI and Machine Learning Fundamentals",
        "web_urls": [
            {
                "url": "https://developers.google.com/machine-learning/crash-course",
                "description": "Google ML Crash Course"
            },
            {
                "url": "https://ai.google.dev/docs",
                "description": "Google AI Developer Documentation"
            },
            {
                "url": "https://developers.google.com/machine-learning/guides",
                "description": "ML Guides and Best Practices"
            },
            {
                "url": "https://cloud.google.com/vertex-ai/docs",
                "description": "Vertex AI Documentation"
            }
        ],
        "search_queries": [
            {
                "query": "machine learning fundamentals tutorial site:medium.com OR site:towardsdatascience.com OR site:realpython.com",
                "description": "Recent ML tutorials and guides",
                "max_results": 5
            },
            {
                "query": "AI concepts explained 2024 OR 2025",
                "description": "Latest AI concept explanations",
                "max_results": 3
            }
        ],
        "apis": [
            # Add API configurations here when available
        ]
    },

    "aws-solutions-architect": {
        "description": "AWS Solutions Architect Certification",
        "web_urls": [
            {
                "url": "https://docs.aws.amazon.com/wellarchitected/latest/framework/",
                "description": "AWS Well-Architected Framework"
            },
            {
                "url": "https://aws.amazon.com/architecture/well-architected/",
                "description": "Well-Architected Best Practices"
            },
            {
                "url": "https://docs.aws.amazon.com/whitepapers/latest/aws-overview/",
                "description": "AWS Overview Whitepaper"
            },
            {
                "url": "https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-patterns/",
                "description": "Architectural Patterns"
            }
        ],
        "search_queries": [
            {
                "query": "AWS solutions architect best practices 2024 OR 2025 site:medium.com OR site:aws.amazon.com/blogs",
                "description": "Recent AWS architecture best practices",
                "max_results": 5
            },
            {
                "query": "AWS well architected framework case studies",
                "description": "Real-world AWS architecture examples",
                "max_results": 3
            }
        ],
        "apis": [
            # AWS APIs would require authentication
        ]
    },

    "mongodb-developer": {
        "description": "MongoDB Developer Certification",
        "web_urls": [
            {
                "url": "https://docs.mongodb.com/manual/",
                "description": "MongoDB Manual"
            },
            {
                "url": "https://university.mongodb.com/",
                "description": "MongoDB University"
            },
            {
                "url": "https://docs.mongodb.com/drivers/",
                "description": "MongoDB Drivers Documentation"
            },
            {
                "url": "https://docs.mongodb.com/guides/",
                "description": "MongoDB Guides"
            }
        ],
        "search_queries": [
            {
                "query": "MongoDB best practices 2024 OR 2025 site:mongodb.com/blog OR site:medium.com",
                "description": "Recent MongoDB development best practices",
                "max_results": 5
            },
            {
                "query": "MongoDB schema design patterns",
                "description": "MongoDB data modeling examples",
                "max_results": 3
            }
        ],
        "apis": [
            # MongoDB Atlas APIs would require authentication
        ]
    },

    "azure-fundamentals": {
        "description": "Microsoft Azure Fundamentals",
        "web_urls": [
            {
                "url": "https://docs.microsoft.com/en-us/azure/",
                "description": "Azure Documentation"
            },
            {
                "url": "https://docs.microsoft.com/en-us/learn/paths/azure-fundamentals/",
                "description": "Azure Fundamentals Learning Path"
            }
        ],
        "apis": [
            # Azure APIs would require authentication
        ]
    },

    "gcp-professional-cloud-architect": {
        "description": "Google Cloud Professional Cloud Architect",
        "web_urls": [
            {
                "url": "https://cloud.google.com/architecture/",
                "description": "Google Cloud Architecture"
            },
            {
                "url": "https://cloud.google.com/docs/",
                "description": "Google Cloud Documentation"
            }
        ],
        "apis": [
            # GCP APIs would require authentication
        ]
    }
}

def get_content_sources(certification_id: str) -> dict:
    """Get content sources for a certification"""
    return CONTENT_SOURCES.get(certification_id, {"web_urls": [], "apis": []})

def get_available_certifications() -> list:
    """Get list of certifications with content sources"""
    return list(CONTENT_SOURCES.keys())