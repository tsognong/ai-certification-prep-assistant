"""
Certification Pack System

Pre-configured certification exam specifications that can be loaded dynamically.
Each pack contains exam structure, topics, and documentation sources.
"""
from typing import Dict, List, Optional
from pymongo import MongoClient
from datetime import datetime


# Pre-configured certification packs
CERTIFICATION_PACKS = {
    "mongodb_associate": {
        "_id": "mongodb_associate",
        "name": "MongoDB Developer Associate",
        "display_name": "MongoDB Developer Associate",
        "vendor": "MongoDB",
        "level": "Associate",
        "blueprint": {
            "total_questions": 53,
            "duration_minutes": 90,
            "passing_score": 70,
            "section_weights": {
                "CRUD Operations": 0.51,
                "Indexes and Performance": 0.17,
                "MongoDB Drivers": 0.18,
                "MongoDB Overview and Introduction": 0.08,
                "Data Modeling": 0.04,
                "Tools and Tooling": 0.02
            },
            "question_types": {
                "mcq": 0.70,  # Multiple Choice
                "msq": 0.30   # Multiple Select
            }
        },
        "topics": [
            "CRUD Operations",
            "Indexes and Performance",
            "MongoDB Drivers",
            "MongoDB Overview",
            "Data Modeling",
            "Tools and Tooling",
            "Aggregation Pipeline",
            "Transactions",
            "Replication",
            "Sharding"
        ],
        "available_resources": [
            {
                "type": "official_docs",
                "title": "MongoDB Manual",
                "url": "https://docs.mongodb.com/manual/",
                "description": "Official MongoDB documentation and manual",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["docs.mongodb.com"],
                    "max_pages": 50,
                    "content_selectors": ["article", ".content", "main"],
                    "exclude_patterns": ["/api/", "/reference/api/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            },
            {
                "type": "learning_path",
                "title": "MongoDB Developer Associate Study Guide",
                "url": "https://learn.mongodb.com/learning-paths/mongodb-developer-associate-exam-study-guide",
                "description": "Official MongoDB learning path for certification",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["learn.mongodb.com"],
                    "max_pages": 20,
                    "content_selectors": [".lesson-content", ".module-content"],
                    "exclude_patterns": ["/quiz/", "/assessment/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            },
            {
                "type": "exam_guide",
                "title": "MongoDB Developer Associate Exam Guide",
                "url": "https://learn.mongodb.com/pages/mongodb-developer-associate-exam-guide",
                "description": "Official MongoDB Developer Associate certification exam guide",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["learn.mongodb.com"],
                    "max_pages": 10,
                    "content_selectors": [".exam-guide-content", ".guide-content", "article"],
                    "exclude_patterns": ["/training/", "/certification/register/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            }
        ],
        "created_at": datetime.now(),
        "active": True
    },
    
    "aws_saa": {
        "_id": "aws_saa",
        "name": "AWS Solutions Architect Associate",
        "display_name": "AWS Solutions Architect Associate (SAA-C03)",
        "vendor": "Amazon Web Services",
        "level": "Associate",
        "blueprint": {
            "total_questions": 65,
            "duration_minutes": 130,
            "passing_score": 72,
            "section_weights": {
                "Design Resilient Architectures": 0.30,
                "Design High-Performing Architectures": 0.28,
                "Design Secure Applications and Architectures": 0.24,
                "Design Cost-Optimized Architectures": 0.18
            },
            "question_types": {
                "mcq": 0.85,
                "msq": 0.15
            }
        },
        "topics": [
            "EC2 (Elastic Compute Cloud)",
            "S3 (Simple Storage Service)",
            "VPC (Virtual Private Cloud)",
            "IAM (Identity and Access Management)",
            "RDS (Relational Database Service)",
            "Lambda (Serverless Computing)",
            "CloudFormation",
            "CloudWatch",
            "Auto Scaling",
            "Load Balancing (ELB/ALB/NLB)",
            "Route 53 (DNS)",
            "DynamoDB",
            "SNS & SQS",
            "CloudFront (CDN)",
            "Elastic Beanstalk",
            "ECS & EKS (Container Services)",
            "Security Groups & NACLs",
            "Cost Optimization Strategies"
        ],
        "available_resources": [
            {
                "type": "official_docs",
                "title": "AWS Documentation",
                "url": "https://docs.aws.amazon.com/",
                "description": "Official AWS documentation and service guides",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["docs.aws.amazon.com"],
                    "max_pages": 100,
                    "content_selectors": ["article", ".content", "main"],
                    "exclude_patterns": ["/console/", "/cli/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            },
            {
                "type": "architecture_center",
                "title": "AWS Architecture Center",
                "url": "https://aws.amazon.com/architecture/",
                "description": "AWS architecture patterns and best practices",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["aws.amazon.com"],
                    "max_pages": 30,
                    "content_selectors": [".architecture-content", ".pattern-content"],
                    "exclude_patterns": ["/pricing/", "/contact/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            },
            {
                "type": "exam_guide",
                "title": "AWS Solutions Architect Associate Exam Guide",
                "url": "https://aws.amazon.com/certification/certified-solutions-architect-associate/",
                "description": "Official AWS SAA-C03 certification exam guide and requirements",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["aws.amazon.com"],
                    "max_pages": 5,
                    "content_selectors": [".exam-guide-content", ".certification-content", "article"],
                    "exclude_patterns": ["/training/", "/register/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            }
        ],
        "created_at": datetime.now(),
        "active": True
    },
    
    "terraform_associate": {
        "_id": "terraform_associate",
        "name": "HashiCorp Terraform Associate",
        "display_name": "HashiCorp Certified: Terraform Associate (003)",
        "vendor": "HashiCorp",
        "level": "Associate",
        "blueprint": {
            "total_questions": 57,
            "duration_minutes": 60,
            "passing_score": 70,
            "section_weights": {
                "Understand Infrastructure as Code (IaC) concepts": 0.15,
                "Understand the purpose of Terraform": 0.15,
                "Understand Terraform basics": 0.20,
                "Use Terraform outside the core workflow": 0.15,
                "Interact with Terraform modules": 0.15,
                "Use the core Terraform workflow": 0.10,
                "Implement and maintain state": 0.10
            },
            "question_types": {
                "mcq": 0.75,
                "msq": 0.25
            }
        },
        "topics": [
            "Infrastructure as Code (IaC)",
            "Terraform Core Workflow",
            "Terraform Configuration Language (HCL)",
            "Variables and Outputs",
            "Resource Blocks",
            "Data Sources",
            "Providers",
            "State Management",
            "Remote State",
            "State Locking",
            "Terraform Modules",
            "Module Sources",
            "Terraform Cloud & Enterprise",
            "Workspaces",
            "Terraform Commands (init, plan, apply, destroy)",
            "Import Resources",
            "Terraform Functions",
            "Dependencies and Graph"
        ],
        "available_resources": [
            {
                "type": "official_docs",
                "title": "HashiCorp Terraform Documentation",
                "url": "https://developer.hashicorp.com/terraform/docs",
                "description": "Official Terraform documentation and guides",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["developer.hashicorp.com"],
                    "max_pages": 50,
                    "content_selectors": ["article", ".content", "main"],
                    "exclude_patterns": ["/api/", "/registry/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            },
            {
                "type": "tutorials",
                "title": "Terraform Tutorials",
                "url": "https://developer.hashicorp.com/terraform/tutorials",
                "description": "Official Terraform tutorials and examples",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["developer.hashicorp.com"],
                    "max_pages": 25,
                    "content_selectors": [".tutorial-content", ".example-content"],
                    "exclude_patterns": ["/certification/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            },
            {
                "type": "exam_guide",
                "title": "HashiCorp Terraform Associate Exam Guide",
                "url": "https://developer.hashicorp.com/terraform/tutorials/certification",
                "description": "Official HashiCorp Terraform Associate certification exam guide",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["developer.hashicorp.com"],
                    "max_pages": 8,
                    "content_selectors": [".exam-guide-content", ".certification-content", "article"],
                    "exclude_patterns": ["/training/schedule/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            }
        ],
        "created_at": datetime.now(),
        "active": True
    },
    
    "azure_az900": {
        "_id": "azure_az900",
        "name": "Azure Fundamentals",
        "display_name": "Microsoft Azure Fundamentals (AZ-900)",
        "vendor": "Microsoft",
        "level": "Fundamentals",
        "blueprint": {
            "total_questions": 60,
            "duration_minutes": 85,
            "passing_score": 70,
            "section_weights": {
                "Describe cloud concepts": 0.25,
                "Describe Azure architecture and services": 0.35,
                "Describe Azure management and governance": 0.30,
                "Describe Azure identity, access, and security": 0.10
            },
            "question_types": {
                "mcq": 0.70,
                "msq": 0.30
            }
        },
        "topics": [
            "Cloud Computing Concepts",
            "Azure Architecture",
            "Azure Virtual Machines",
            "Azure Storage",
            "Azure Networking",
            "Azure Active Directory",
            "Azure Subscriptions",
            "Resource Groups",
            "Azure Resource Manager",
            "Azure Cost Management",
            "Azure Governance",
            "Azure Monitor",
            "Azure Security Center",
            "Azure Policy"
        ],
        "available_resources": [
            {
                "type": "official_docs",
                "title": "Microsoft Learn - Azure",
                "url": "https://learn.microsoft.com/en-us/azure/",
                "description": "Official Microsoft Azure documentation and learning paths",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["learn.microsoft.com"],
                    "max_pages": 75,
                    "content_selectors": ["article", ".content", "main"],
                    "exclude_patterns": ["/training/", "/certification/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            },
            {
                "type": "learning_path",
                "title": "Azure Fundamentals Learning Path",
                "url": "https://learn.microsoft.com/en-us/certifications/azure-fundamentals/",
                "description": "Official Azure Fundamentals certification learning path",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["learn.microsoft.com"],
                    "max_pages": 15,
                    "content_selectors": [".learning-path-content", ".module-content"],
                    "exclude_patterns": ["/exam/", "/practice/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            },
            {
                "type": "exam_guide",
                "title": "Azure Fundamentals (AZ-900) Exam Guide",
                "url": "https://learn.microsoft.com/en-us/certifications/exams/az-900/",
                "description": "Official Microsoft Azure Fundamentals AZ-900 exam guide",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["learn.microsoft.com"],
                    "max_pages": 6,
                    "content_selectors": [".exam-guide-content", ".certification-content", "article"],
                    "exclude_patterns": ["/training/", "/schedule/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            }
        ],
        "created_at": datetime.now(),
        "active": True
    },
    
    "gcp_associate": {
        "_id": "gcp_associate",
        "name": "Google Cloud Associate Engineer",
        "display_name": "Google Cloud Associate Cloud Engineer",
        "vendor": "Google Cloud",
        "level": "Associate",
        "blueprint": {
            "total_questions": 50,
            "duration_minutes": 120,
            "passing_score": 70,
            "section_weights": {
                "Setting up a cloud solution environment": 0.20,
                "Planning and configuring a cloud solution": 0.20,
                "Deploying and implementing a cloud solution": 0.25,
                "Ensuring successful operation of a cloud solution": 0.20,
                "Configuring access and security": 0.15
            },
            "question_types": {
                "mcq": 0.80,
                "msq": 0.20
            }
        },
        "topics": [
            "Google Compute Engine",
            "Google Kubernetes Engine (GKE)",
            "Cloud Storage",
            "Cloud SQL",
            "BigQuery",
            "Cloud Functions",
            "IAM (Identity and Access Management)",
            "VPC Networking",
            "Load Balancing",
            "Cloud Monitoring",
            "Cloud Logging",
            "Deployment Manager",
            "Cloud Build",
            "Cloud Run"
        ],
        "available_resources": [
            {
                "type": "official_docs",
                "title": "Google Cloud Documentation",
                "url": "https://cloud.google.com/docs",
                "description": "Official Google Cloud Platform documentation",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["cloud.google.com"],
                    "max_pages": 80,
                    "content_selectors": ["article", ".content", "main"],
                    "exclude_patterns": ["/pricing/", "/support/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            },
            {
                "type": "learning_path",
                "title": "Cloud Engineer Learning Path",
                "url": "https://cloud.google.com/learn/certification/cloud-engineer",
                "description": "Official Google Cloud Associate Cloud Engineer learning path",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["cloud.google.com"],
                    "max_pages": 20,
                    "content_selectors": [".learning-content", ".path-content"],
                    "exclude_patterns": ["/exam/", "/training/pricing/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            },
            {
                "type": "exam_guide",
                "title": "Associate Cloud Engineer Exam Guide",
                "url": "https://cloud.google.com/learn/certification/guides/cloud-engineer",
                "description": "Official Google Cloud Associate Cloud Engineer exam guide",
                "access_type": "free",
                "scrape_config": {
                    "allowed_domains": ["cloud.google.com"],
                    "max_pages": 7,
                    "content_selectors": [".exam-guide-content", ".guide-content", "article"],
                    "exclude_patterns": ["/training/", "/register/"]
                },
                "quality_verified": True,
                "last_checked": "2025-11-29"
            }
        ],
        "created_at": datetime.now(),
        "active": True
    }
}


class CertificationPackLoader:
    """Loads and manages certification packs"""
    
    def __init__(self, mongo_client: MongoClient, db_name: str = "campus-plateform"):
        self.db = mongo_client[db_name]
        self.certifications_coll = self.db["certifications"]
        
        # Ensure indexes (_id is automatically unique, don't need to specify)
        self.certifications_coll.create_index("active")
    
    def initialize_packs(self):
        """Initialize all certification packs in MongoDB"""
        for pack_id, pack_data in CERTIFICATION_PACKS.items():
            self.certifications_coll.update_one(
                {"_id": pack_id},
                {"$set": pack_data},
                upsert=True
            )
        print(f"✅ Initialized {len(CERTIFICATION_PACKS)} certification packs")
    
    def get_pack(self, cert_id: str) -> Optional[Dict]:
        """Get a specific certification pack"""
        return self.certifications_coll.find_one({"_id": cert_id, "active": True})
    
    def get_all_packs(self) -> List[Dict]:
        """Get all active certification packs"""
        return list(self.certifications_coll.find({"active": True}))
    
    def get_pack_topics(self, cert_id: str) -> List[str]:
        """Get topics for a certification"""
        pack = self.get_pack(cert_id)
        return pack["topics"] if pack else []
    
    def get_pack_blueprint(self, cert_id: str) -> Dict:
        """Get exam blueprint for a certification"""
        pack = self.get_pack(cert_id)
        return pack["blueprint"] if pack else {}
    
    def get_available_resources(self, cert_id: str) -> List[Dict]:
        """Get available resources for a certification"""
        pack = self.get_pack(cert_id)
        return pack["available_resources"] if pack else []
    
    def add_custom_pack(self, pack_data: Dict) -> str:
        """Add a custom certification pack"""
        pack_data["created_at"] = datetime.now()
        pack_data["active"] = True
        
        result = self.certifications_coll.insert_one(pack_data)
        return str(result.inserted_id)
    
    def deactivate_pack(self, cert_id: str):
        """Deactivate a certification pack"""
        self.certifications_coll.update_one(
            {"_id": cert_id},
            {"$set": {"active": False}}
        )


def get_available_certifications_simple() -> Dict[str, str]:
    """Get simple dict of cert_id -> display_name for UI"""
    return {
        cert_id: pack_data["display_name"]
        for cert_id, pack_data in CERTIFICATION_PACKS.items()
    }
