"""
Certification Pack Loader

Manages certification configurations and provides 
a unified interface for multi-certification support.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pymongo import MongoClient
import json


@dataclass
class CertificationPack:
    """Represents a certification pack configuration"""
    id: str
    name: str
    display_name: str
    blueprint: Dict[str, Any]
    topics: List[str]
    documentation_sources: List[Dict[str, str]]
    question_style: str
    code_language: Optional[str] = None
    
    @property
    def total_questions(self) -> int:
        return self.blueprint.get('total_questions', 50)
    
    @property
    def passing_score(self) -> int:
        return self.blueprint.get('passing_score', 70)
    
    @property
    def duration_minutes(self) -> int:
        return self.blueprint.get('duration_minutes', 90)
    
    @property
    def section_weights(self) -> Dict[str, float]:
        return self.blueprint.get('sections', {})


class CertificationPackLoader:
    """Loads and manages certification packs from MongoDB"""
    
    def __init__(self, mongo_client: MongoClient, db_name: str = "campus-plateform"):
        self.db = mongo_client[db_name]
        self.certs_collection = self.db["certifications"]
        
    def initialize_default_packs(self):
        """Initialize default certification packs if not exists"""
        
        default_packs = [
            # MongoDB Developer Associate
            {
                "_id": "mongodb_associate",
                "name": "MongoDB Developer Associate",
                "display_name": "MongoDB Developer Associate",
                "blueprint": {
                    "total_questions": 53,
                    "passing_score": 68,
                    "duration_minutes": 90,
                    "sections": {
                        "CRUD Operations": 0.51,
                        "Indexes and Performance": 0.17,
                        "Data Modeling": 0.04,
                        "Tools and Tooling": 0.02,
                        "Drivers": 0.18,
                        "MongoDB Overview and the Document Model": 0.08
                    },
                    "question_types": {
                        "mcq": 0.80,
                        "msq": 0.20
                    }
                },
                "topics": [
                    "CRUD Operations",
                    "Indexes and Performance",
                    "Data Modeling",
                    "Tools and Tooling",
                    "Drivers",
                    "MongoDB Overview and the Document Model"
                ],
                "documentation_sources": [
                    {
                        "type": "mongodb_docs",
                        "base_url": "https://www.mongodb.com/docs/",
                        "sections": ["manual", "drivers/java", "drivers/python"]
                    }
                ],
                "question_style": "code_based_java",
                "code_language": "java"
            },
            
            # AWS Solutions Architect Associate
            {
                "_id": "aws_saa",
                "name": "AWS Solutions Architect Associate",
                "display_name": "AWS Solutions Architect Associate (SAA-C03)",
                "blueprint": {
                    "total_questions": 65,
                    "passing_score": 72,
                    "duration_minutes": 130,
                    "sections": {
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
                    "EC2", "S3", "VPC", "RDS", "Lambda", "IAM",
                    "CloudFront", "Route 53", "ELB", "Auto Scaling",
                    "DynamoDB", "SQS", "SNS", "CloudWatch",
                    "CloudFormation", "Elastic Beanstalk"
                ],
                "documentation_sources": [
                    {
                        "type": "aws_docs",
                        "base_url": "https://docs.aws.amazon.com/",
                        "sections": ["ec2", "s3", "vpc", "rds", "lambda", "iam"]
                    }
                ],
                "question_style": "scenario_based",
                "code_language": None
            },
            
            # Terraform Associate
            {
                "_id": "terraform_associate",
                "name": "Terraform Associate",
                "display_name": "HashiCorp Certified: Terraform Associate",
                "blueprint": {
                    "total_questions": 57,
                    "passing_score": 70,
                    "duration_minutes": 60,
                    "sections": {
                        "Understand Infrastructure as Code (IaC) concepts": 0.15,
                        "Understand Terraform's purpose": 0.10,
                        "Understand Terraform basics": 0.20,
                        "Use the Terraform CLI": 0.15,
                        "Interact with Terraform modules": 0.15,
                        "Navigate Terraform workflow": 0.15,
                        "Implement and maintain state": 0.10
                    },
                    "question_types": {
                        "mcq": 0.90,
                        "msq": 0.10
                    }
                },
                "topics": [
                    "IaC Concepts", "Terraform Purpose", "Terraform Basics",
                    "Terraform CLI", "Modules", "Workflow", "State Management",
                    "Providers", "Resources", "Variables", "Outputs",
                    "Provisioners", "Workspaces", "Backend Configuration"
                ],
                "documentation_sources": [
                    {
                        "type": "terraform_docs",
                        "base_url": "https://developer.hashicorp.com/terraform/docs",
                        "sections": ["cli", "language", "cloud"]
                    }
                ],
                "question_style": "code_based_hcl",
                "code_language": "hcl"
            },
            
            # Azure Fundamentals
            {
                "_id": "azure_az900",
                "name": "Azure Fundamentals",
                "display_name": "Microsoft Azure Fundamentals (AZ-900)",
                "blueprint": {
                    "total_questions": 40,
                    "passing_score": 70,
                    "duration_minutes": 85,
                    "sections": {
                        "Describe cloud concepts": 0.25,
                        "Describe Azure architecture and services": 0.35,
                        "Describe Azure management and governance": 0.30,
                        "Describe Azure cost management": 0.10
                    },
                    "question_types": {
                        "mcq": 0.85,
                        "msq": 0.15
                    }
                },
                "topics": [
                    "Cloud Concepts", "Azure Services", "Core Solutions",
                    "Security", "Identity", "Governance", "Privacy",
                    "Compliance", "Pricing", "Support", "SLAs"
                ],
                "documentation_sources": [
                    {
                        "type": "azure_docs",
                        "base_url": "https://learn.microsoft.com/en-us/azure/",
                        "sections": ["fundamentals"]
                    }
                ],
                "question_style": "conceptual",
                "code_language": None
            },
            
            # Google Cloud Associate
            {
                "_id": "gcp_associate",
                "name": "Google Cloud Associate",
                "display_name": "Google Cloud Associate Cloud Engineer",
                "blueprint": {
                    "total_questions": 50,
                    "passing_score": 70,
                    "duration_minutes": 120,
                    "sections": {
                        "Setting up a cloud solution environment": 0.20,
                        "Planning and configuring a cloud solution": 0.20,
                        "Deploying and implementing a cloud solution": 0.25,
                        "Ensuring successful operation": 0.20,
                        "Configuring access and security": 0.15
                    },
                    "question_types": {
                        "mcq": 0.80,
                        "msq": 0.20
                    }
                },
                "topics": [
                    "Compute Engine", "Cloud Storage", "VPC", "IAM",
                    "App Engine", "Kubernetes Engine", "Cloud Functions",
                    "Cloud SQL", "BigQuery", "Cloud Monitoring"
                ],
                "documentation_sources": [
                    {
                        "type": "gcp_docs",
                        "base_url": "https://cloud.google.com/docs/",
                        "sections": ["compute", "storage", "networking"]
                    }
                ],
                "question_style": "scenario_based",
                "code_language": None
            }
        ]
        
        # Insert packs if they don't exist
        for pack in default_packs:
            self.certs_collection.update_one(
                {"_id": pack["_id"]},
                {"$set": pack},
                upsert=True
            )
        
        print(f"✅ Initialized {len(default_packs)} certification packs")
    
    def get_pack(self, cert_id: str) -> Optional[CertificationPack]:
        """Load a specific certification pack"""
        doc = self.certs_collection.find_one({"_id": cert_id})
        if not doc:
            return None
        
        return CertificationPack(
            id=doc["_id"],
            name=doc["name"],
            display_name=doc["display_name"],
            blueprint=doc["blueprint"],
            topics=doc["topics"],
            documentation_sources=doc["documentation_sources"],
            question_style=doc["question_style"],
            code_language=doc.get("code_language")
        )
    
    def list_available_packs(self) -> List[Dict[str, str]]:
        """List all available certification packs"""
        packs = self.certs_collection.find({}, {"_id": 1, "display_name": 1, "name": 1})
        return [
            {
                "id": pack["_id"],
                "display_name": pack["display_name"],
                "name": pack["name"]
            }
            for pack in packs
        ]
    
    def get_topics_for_pack(self, cert_id: str) -> List[str]:
        """Get topics for a specific certification"""
        pack = self.get_pack(cert_id)
        return pack.topics if pack else []
