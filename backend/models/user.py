"""
User model for GolfStats application.

This module defines the User model for authentication and user management,
and the UserPreference model for user preferences and tracker credentials.
"""
from typing import Optional, Dict, Any, List
import os
import sys
import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

# Add the project root directory to Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database.db_connection import Base
from config.config import config
from backend.database.supabase_data import get_user_preferences

class UserPreference(Base):
    """User preferences model for storing preferences and tracker credentials."""
    
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    preferred_units = Column(String(10), default="yards")  # 'yards' or 'meters'
    handicap = Column(String(10), nullable=True)
    
    # Tracker credentials
    trackman_username = Column(String(255), nullable=True)
    trackman_password = Column(String(255), nullable=True)
    arccos_email = Column(String(255), nullable=True)  
    arccos_password = Column(String(255), nullable=True)
    skytrak_username = Column(String(255), nullable=True)
    skytrak_password = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert preferences to dictionary.
        
        Returns:
            Dictionary representation of preferences
        """
        return {
            "id": self.id,
            "user_id": str(self.user_id) if self.user_id else None,
            "preferred_units": self.preferred_units,
            "handicap": self.handicap,
            "has_trackman": bool(self.trackman_username and self.trackman_password),
            "has_arccos": bool(self.arccos_email and self.arccos_password),
            "has_skytrak": bool(self.skytrak_username and self.skytrak_password)
        }

# NOTE: This User model has been commented out to use Supabase Auth directly
# We're keeping it as a reference for functions that still rely on it
# but no longer using it to manage users in a local database table.

# class User(Base):
#     """User model for authentication and profile information."""
#     
#     __tablename__ = "users"
#     
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String(255), unique=True, index=True, nullable=False)
#     username = Column(String(50), unique=True, index=True, nullable=True)
#     hashed_password = Column(String(255), nullable=True)
#     full_name = Column(String(100), nullable=True)
#     is_active = Column(Boolean, default=True)
#     is_superuser = Column(Boolean, default=False)
#     created_at = Column(DateTime, default=datetime.datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
#     
#     # OAuth related fields
#     auth_provider = Column(String(20), nullable=True)  # 'google', 'custom', etc.
#     oauth_id = Column(String(255), nullable=True)
#     oauth_access_token = Column(Text, nullable=True)
#     oauth_refresh_token = Column(Text, nullable=True)
#     oauth_token_expires = Column(DateTime, nullable=True)
#     profile_picture = Column(String(255), nullable=True)
#     
#     # Define relationships to other models
#     golf_rounds = relationship("GolfRound", back_populates="user")
#     clubs = relationship("Club", back_populates="user")

# Replacement User class that mimics the interface but uses Supabase Auth
class User:
    """User model that wraps Supabase Auth User."""
    
    def __init__(self, user_data: Dict[str, Any]):
        """
        Initialize from Supabase user data.
        
        Args:
            user_data: Dictionary containing user data from Supabase Auth
        """
        self.id = user_data.get('id')
        self.email = user_data.get('email')
        self.username = user_data.get('user_metadata', {}).get('username')
        self.full_name = user_data.get('user_metadata', {}).get('full_name')
        self.is_active = True
        self.is_superuser = user_data.get('app_metadata', {}).get('is_superuser', False)
        self.created_at = user_data.get('created_at')
        self.updated_at = user_data.get('updated_at')
        self.auth_provider = user_data.get('app_metadata', {}).get('provider', 'custom')
        self.oauth_id = user_data.get('user_metadata', {}).get('oauth_id')
        self.profile_picture = user_data.get('user_metadata', {}).get('picture')
        self._preferences_cache = None
    
    def get_preferences(self) -> Dict[str, Any]:
        """
        Get user preferences from Supabase user_preferences table.
        
        Returns:
            Dictionary of user preferences
        """
        # Use supabase_data function to get preferences
        if hasattr(self, '_preferences_cache') and self._preferences_cache:
            return self._preferences_cache
            
        # Convert ID appropriately for Supabase
        supabase_user_id = str(self.id)
        preferences = get_user_preferences(supabase_user_id)
        self._preferences_cache = preferences
        return preferences
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert user model to dictionary.
        
        Returns:
            Dictionary representation of the user
        """
        prefs = self.get_preferences() or {}
        
        # Get avatar URL from preferences or use profile picture from auth
        avatar_url = prefs.get("avatar_url") or self.profile_picture
        
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "name": self.full_name,  # Added for compatibility
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at,
            "auth_provider": self.auth_provider,
            "profile_picture": self.profile_picture,
            "avatar_url": avatar_url,
            "preferences": prefs,  # Include all preferences
            "handicap": prefs.get("handicap"),
            "preferred_units": prefs.get("preferred_units", "yards"),
            "has_trackman": self.trackman_credentials_valid(),
            "has_arccos": self.arccos_credentials_valid(),
            "has_skytrak": self.skytrak_credentials_valid()
        }
    
    def trackman_credentials_valid(self) -> bool:
        """
        Check if user has valid Trackman credentials.
        
        Returns:
            bool: True if has valid credentials
        """
        # First check user-specific credentials from preferences
        prefs = self.get_preferences()
        if prefs.get("trackman_username") and prefs.get("trackman_password"):
            return True
        
        # Then check global credentials from config
        global_username = config["scrapers"]["trackman"]["username"]
        global_password = config["scrapers"]["trackman"]["password"]
        
        return bool(global_username and global_password)
    
    def arccos_credentials_valid(self) -> bool:
        """
        Check if user has valid Arccos credentials.
        
        Returns:
            bool: True if has valid credentials
        """
        # First check user-specific credentials from preferences
        prefs = self.get_preferences()
        if prefs.get("arccos_email") and prefs.get("arccos_password"):
            return True
        
        # Then check global credentials from config
        global_email = config["scrapers"]["arccos"]["email"]
        global_password = config["scrapers"]["arccos"]["password"]
        
        return bool(global_email and global_password)
    
    def skytrak_credentials_valid(self) -> bool:
        """
        Check if user has valid SkyTrak credentials.
        
        Returns:
            bool: True if has valid credentials
        """
        # First check user-specific credentials from preferences
        prefs = self.get_preferences()
        if prefs.get("skytrak_username") and prefs.get("skytrak_password"):
            return True
        
        # Then check global credentials from config
        global_username = config["scrapers"]["skytrak"]["username"]
        global_password = config["scrapers"]["skytrak"]["password"]
        
        return bool(global_username and global_password)
    
    def get_trackman_credentials(self) -> Dict[str, str]:
        """
        Get Trackman credentials for this user.
        
        Returns:
            Dictionary with username and password
        """
        prefs = self.get_preferences()
        if prefs.get("trackman_username") and prefs.get("trackman_password"):
            return {
                "username": prefs["trackman_username"],
                "password": prefs["trackman_password"]
            }
        else:
            return {
                "username": config["scrapers"]["trackman"]["username"],
                "password": config["scrapers"]["trackman"]["password"]
            }
    
    def get_arccos_credentials(self) -> Dict[str, str]:
        """
        Get Arccos credentials for this user.
        
        Returns:
            Dictionary with email and password
        """
        prefs = self.get_preferences()
        if prefs.get("arccos_email") and prefs.get("arccos_password"):
            return {
                "email": prefs["arccos_email"],
                "password": prefs["arccos_password"]
            }
        else:
            return {
                "email": config["scrapers"]["arccos"]["email"],
                "password": config["scrapers"]["arccos"]["password"]
            }
    
    def get_skytrak_credentials(self) -> Dict[str, str]:
        """
        Get SkyTrak credentials for this user.
        
        Returns:
            Dictionary with username and password
        """
        prefs = self.get_preferences()
        if prefs.get("skytrak_username") and prefs.get("skytrak_password"):
            return {
                "username": prefs["skytrak_username"],
                "password": prefs["skytrak_password"]
            }
        else:
            return {
                "username": config["scrapers"]["skytrak"]["username"],
                "password": config["scrapers"]["skytrak"]["password"]
            }
    
    @classmethod
    def from_oauth(cls, oauth_data: Dict[str, Any]) -> "User":
        """
        Create a User instance from OAuth data.
        
        Args:
            oauth_data: Dictionary containing OAuth profile data
            
        Returns:
            User instance
        """
        return cls({
            'id': oauth_data.get('id'),
            'email': oauth_data.get('email'),
            'user_metadata': {
                'full_name': oauth_data.get('name'),
                'picture': oauth_data.get('picture'),
                'oauth_id': oauth_data.get('id')
            },
            'app_metadata': {
                'provider': oauth_data.get('provider'),
                'is_superuser': False
            }
        })