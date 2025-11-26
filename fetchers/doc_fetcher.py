"""
Generic Documentation Fetcher

Fetches documentation from various sources and stores embeddings
"""
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
import re


class DocumentationFetcher:
    """Generic fetcher for certification documentation"""
    
    def __init__(self, mongo_client: MongoClient, db_name: str = "campus-plateform"):
        self.db = mongo_client[db_name]
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_and_store(
        self,
        certification_id: str,
        source_config: Dict[str, Any]
    ) -> int:
        """Fetch documentation and store embeddings"""
        
        source_type = source_config.get("type")
        
        if source_type == "mongodb_docs":
            return await self._fetch_mongodb_docs(certification_id, source_config)
        elif source_type == "aws_docs":
            return await self._fetch_aws_docs(certification_id, source_config)
        elif source_type == "azure_docs":
            return await self._fetch_azure_docs(certification_id, source_config)
        elif source_type == "terraform_docs":
            return await self._fetch_terraform_docs(certification_id, source_config)
        else:
            return await self._fetch_generic_docs(certification_id, source_config)
    
    async def _fetch_mongodb_docs(
        self,
        certification_id: str,
        source_config: Dict[str, Any]
    ) -> int:
        """Fetch MongoDB documentation"""
        from memory.embedding_store import EmbeddingStore
        
        embedding_store = EmbeddingStore(self.db.client)
        
        # Sample MongoDB documentation (in production, fetch from actual API)
        sample_docs = [
            {
                "content": "MongoDB CRUD operations include insertOne, insertMany, findOne, find, updateOne, updateMany, replaceOne, deleteOne, and deleteMany. These operations allow you to create, read, update, and delete documents in MongoDB collections.",
                "topic": "CRUD Operations"
            },
            {
                "content": "MongoDB indexes improve query performance. Common index types include single field indexes, compound indexes, multikey indexes, text indexes, and geospatial indexes. Use createIndex() method to create indexes.",
                "topic": "Indexes and Performance"
            },
            {
                "content": "The MongoDB Java driver provides MongoClient for connecting to MongoDB. Use MongoDatabase to access databases and MongoCollection<Document> to perform operations on collections.",
                "topic": "Drivers"
            }
        ]
        
        count = embedding_store.batch_store_documents(
            documents=sample_docs,
            certification_id=certification_id
        )
        
        return count
    
    async def _fetch_aws_docs(
        self,
        certification_id: str,
        source_config: Dict[str, Any]
    ) -> int:
        """Fetch AWS documentation"""
        from memory.embedding_store import EmbeddingStore
        
        embedding_store = EmbeddingStore(self.db.client)
        
        # Sample AWS documentation
        sample_docs = [
            {
                "content": "Amazon EC2 provides scalable computing capacity. Instance types include General Purpose (t3, m5), Compute Optimized (c5), Memory Optimized (r5), and Storage Optimized (i3). Use Auto Scaling for automatic capacity management.",
                "topic": "EC2"
            },
            {
                "content": "Amazon S3 is object storage service. Storage classes include Standard, Intelligent-Tiering, Standard-IA, One Zone-IA, Glacier, and Glacier Deep Archive. Use lifecycle policies to transition objects between storage classes.",
                "topic": "S3"
            },
            {
                "content": "Amazon VPC enables you to launch AWS resources in a logically isolated virtual network. Components include subnets, route tables, internet gateways, NAT gateways, and security groups.",
                "topic": "VPC"
            },
            {
                "content": "AWS Lambda lets you run code without provisioning servers. Supports Node.js, Python, Java, Go, .NET. Charged based on execution time and memory. Use for event-driven architectures and microservices.",
                "topic": "Lambda"
            },
            {
                "content": "AWS IAM manages access to AWS services. Components include users, groups, roles, and policies. Use principle of least privilege. Enable MFA for enhanced security.",
                "topic": "IAM"
            }
        ]
        
        count = embedding_store.batch_store_documents(
            documents=sample_docs,
            certification_id=certification_id
        )
        
        return count
    
    async def _fetch_terraform_docs(
        self,
        certification_id: str,
        source_config: Dict[str, Any]
    ) -> int:
        """Fetch Terraform documentation"""
        from memory.embedding_store import EmbeddingStore
        
        embedding_store = EmbeddingStore(self.db.client)
        
        # Sample Terraform documentation
        sample_docs = [
            {
                "content": "Terraform is Infrastructure as Code tool. Write configuration in HCL (HashiCorp Configuration Language). Main commands: init, plan, apply, destroy. Workflow: Write > Plan > Apply.",
                "topic": "Terraform Basics"
            },
            {
                "content": "Terraform providers enable interaction with APIs. Popular providers: AWS, Azure, GCP, Kubernetes. Configure in required_providers block. Each resource belongs to a provider.",
                "topic": "Providers"
            },
            {
                "content": "Terraform state tracks infrastructure. Stored in terraform.tfstate file. Use remote backends (S3, Terraform Cloud) for team collaboration. Enable state locking to prevent concurrent modifications.",
                "topic": "State Management"
            },
            {
                "content": "Terraform modules are reusable configurations. Create modules for common patterns. Use input variables and output values. Source modules from Terraform Registry or Git repositories.",
                "topic": "Modules"
            },
            {
                "content": "Terraform CLI commands: init (initialize), validate (check syntax), plan (preview changes), apply (create/update), destroy (delete), fmt (format code), refresh (sync state).",
                "topic": "Terraform CLI"
            }
        ]
        
        count = embedding_store.batch_store_documents(
            documents=sample_docs,
            certification_id=certification_id
        )
        
        return count
    
    async def _fetch_azure_docs(
        self,
        certification_id: str,
        source_config: Dict[str, Any]
    ) -> int:
        """Fetch Azure documentation"""
        from memory.embedding_store import EmbeddingStore
        
        embedding_store = EmbeddingStore(self.db.client)
        
        sample_docs = [
            {
                "content": "Azure cloud computing offers IaaS, PaaS, and SaaS services. Main benefits: high availability, scalability, elasticity, agility, geo-distribution, and disaster recovery.",
                "topic": "Cloud Concepts"
            },
            {
                "content": "Azure core services include Compute (VMs, App Service, Functions), Networking (VNet, Load Balancer), Storage (Blob, File, Queue, Table), and Databases (SQL, Cosmos DB).",
                "topic": "Azure Services"
            },
            {
                "content": "Azure pricing: Pay-as-you-go, Reserved Instances (1 or 3 years), Spot Instances. Use Azure Cost Management for monitoring. Apply tags for cost allocation.",
                "topic": "Pricing"
            }
        ]
        
        count = embedding_store.batch_store_documents(
            documents=sample_docs,
            certification_id=certification_id
        )
        
        return count
    
    async def _fetch_generic_docs(
        self,
        certification_id: str,
        source_config: Dict[str, Any]
    ) -> int:
        """Fetch generic documentation from URL"""
        # Placeholder for generic fetcher
        return 0


async def initialize_all_documentation(mongo_client: MongoClient):
    """Initialize documentation for all certifications"""
    
    db = mongo_client["campus-plateform"]
    certs = db["certifications"].find({})
    
    async with DocumentationFetcher(mongo_client) as fetcher:
        for cert in certs:
            cert_id = cert["_id"]
            sources = cert.get("documentation_sources", [])
            
            print(f"Fetching documentation for {cert['name']}...")
            
            for source in sources:
                try:
                    count = await fetcher.fetch_and_store(cert_id, source)
                    print(f"  ✅ Stored {count} documents from {source['type']}")
                except Exception as e:
                    print(f"  ❌ Error fetching {source['type']}: {e}")
    
    print("✅ Documentation initialization complete")
