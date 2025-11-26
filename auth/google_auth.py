"""
Google OAuth Authentication for Streamlit

Provides Google sign-in functionality and user management.
"""
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
from typing import Optional, Dict
from pymongo import MongoClient
from datetime import datetime
import hashlib


class GoogleAuthManager:
    """Manages Google OAuth authentication"""
    
    def __init__(self, mongo_client: MongoClient, db_name: str = "campus-plateform"):
        self.db = mongo_client[db_name]
        self.users_collection = self.db["users"]
        
        # Ensure indexes (skip if already exist)
        try:
            self.users_collection.create_index("email", unique=True, sparse=True)
        except Exception:
            pass  # Index already exists
        
        try:
            self.users_collection.create_index("google_id", unique=True, sparse=True)
        except Exception:
            pass  # Index already exists
        
        # Google OAuth configuration
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8501")
        
    def init_session_state(self):
        """Initialize session state for authentication"""
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "user_info" not in st.session_state:
            st.session_state.user_info = None
        if "user_id" not in st.session_state:
            st.session_state.user_id = None
    
    def get_google_login_url(self) -> str:
        """Generate Google OAuth login URL"""
        # For production, use proper OAuth flow
        # For now, simplified version
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=[
                'openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'
            ]
        )
        
        flow.redirect_uri = self.redirect_uri
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return authorization_url
    
    def handle_callback(self, code: str) -> Dict:
        """Handle OAuth callback and return user info"""
        import requests
        
        try:
            # Create flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=[
                    'openid',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile'
                ]
            )
            
            flow.redirect_uri = self.redirect_uri
            
            # Exchange code for token
            flow.fetch_token(code=code)
            
            # Get credentials
            credentials = flow.credentials
            
            # Get user info from Google
            user_info_response = requests.get(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                headers={'Authorization': f'Bearer {credentials.token}'}
            )
            
            if user_info_response.status_code != 200:
                raise Exception(f"Failed to get user info: {user_info_response.text}")
            
            google_user_info = user_info_response.json()
            
            # Create or update user in MongoDB
            user_id = self.create_or_update_user(google_user_info)
            
            # Get full user profile
            user_profile = self.get_user_profile(user_id)
            
            if not user_profile:
                raise Exception("Failed to retrieve user profile from database")
            
            return user_profile
            
        except Exception as e:
            raise Exception(f"OAuth callback failed: {str(e)}")
    
    def create_or_update_user(self, google_user_info: Dict) -> str:
        """Create or update user in MongoDB"""
        user_email = google_user_info.get("email")
        user_id = hashlib.sha256(user_email.encode()).hexdigest()[:16]
        
        user_doc = {
            "_id": user_id,
            "email": user_email,
            "name": google_user_info.get("name"),
            "picture": google_user_info.get("picture"),
            "google_id": google_user_info.get("sub"),
            "last_login": datetime.now(),
            "created_at": datetime.now(),
            "preferences": {
                "favorite_certifications": [],
                "difficulty_preference": "medium",
                "daily_goal": 10
            },
            "statistics": {
                "total_quizzes": 0,
                "total_questions_answered": 0,
                "average_score": 0,
                "certifications_in_progress": []
            }
        }
        
        # Update last_login if user exists, create if not
        self.users_collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "last_login": datetime.now(),
                    "email": user_email,
                    "name": google_user_info.get("name"),
                    "picture": google_user_info.get("picture")
                },
                "$setOnInsert": {
                    "created_at": datetime.now(),
                    "preferences": user_doc["preferences"],
                    "statistics": user_doc["statistics"]
                }
            },
            upsert=True
        )
        
        return user_id
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile from MongoDB"""
        return self.users_collection.find_one({"_id": user_id})
    
    def update_user_preferences(self, user_id: str, preferences: Dict):
        """Update user preferences"""
        self.users_collection.update_one(
            {"_id": user_id},
            {"$set": {"preferences": preferences}}
        )
    
    def render_login_button(self):
        """Render Google login button"""
        st.markdown("""
        <style>
        .google-login-btn {
            display: inline-flex;
            align-items: center;
            background: white;
            color: #444;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            text-decoration: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: box-shadow 0.3s;
        }
        .google-login-btn:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .google-icon {
            width: 20px;
            height: 20px;
            margin-right: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Simplified login for development
        # In production, use proper OAuth flow
        st.markdown("### 🔐 Sign in to Continue")
        
        # Demo mode - allow email input for testing
        if not os.getenv("GOOGLE_CLIENT_ID"):
            st.warning("⚠️ Demo Mode: Google OAuth not configured. Enter email to continue.")
            demo_email = st.text_input("Email (Demo)", key="demo_email")
            if st.button("Sign In (Demo)", key="demo_signin"):
                if demo_email:
                    # Create demo user
                    user_info = {
                        "email": demo_email,
                        "name": demo_email.split("@")[0],
                        "picture": "https://www.gravatar.com/avatar/?d=mp",
                        "sub": hashlib.md5(demo_email.encode()).hexdigest()
                    }
                    user_id = self.create_or_update_user(user_info)
                    st.session_state.authenticated = True
                    st.session_state.user_info = user_info
                    st.session_state.user_id = user_id
                    st.rerun()
        else:
            # Real Google OAuth
            login_url = self.get_google_login_url()
            st.markdown(f"""
            <a href="{login_url}" class="google-login-btn">
                <img class="google-icon" src="https://www.google.com/favicon.ico" />
                Sign in with Google
            </a>
            """, unsafe_allow_html=True)
    
    def render_user_profile(self):
        """Render user profile in sidebar"""
        if st.session_state.authenticated and st.session_state.user_info:
            user_info = st.session_state.user_info
            
            st.sidebar.markdown("---")
            cols = st.sidebar.columns([1, 3])
            with cols[0]:
                st.image(user_info.get("picture", ""), width=50)
            with cols[1]:
                st.markdown(f"**{user_info.get('name', 'User')}**")
                st.caption(user_info.get('email', ''))
            
            if st.sidebar.button("🚪 Sign Out", key="signout"):
                st.session_state.authenticated = False
                st.session_state.user_info = None
                st.session_state.user_id = None
                st.rerun()
    
    def require_authentication(self) -> bool:
        """Check if user is authenticated, show login if not"""
        self.init_session_state()
        
        if not st.session_state.authenticated:
            st.title("🎓 CertAgent - Universal Certification Preparation")
            st.markdown("""
            Welcome to CertAgent! Prepare for multiple certifications with AI-powered agents:
            
            - 🤖 **Multi-Agent System**: Content Curator, Assessment Engine, Learning Coach
            - 📚 **10+ Certifications**: AWS, Azure, GCP, MongoDB, Terraform, and more
            - 🎯 **Adaptive Learning**: AI adjusts to your skill level
            - 📊 **Progress Tracking**: Monitor your preparation across certifications
            - 🔄 **Cross-Device Sync**: Study anywhere, progress everywhere
            """)
            
            self.render_login_button()
            return False
        
        return True
