"""
User model for GolfStats application.

This module defines the User model for authentication and user management.
"""
from typing import Optional, Dict, Any
import os
import sys
import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship

# Add the project root directory to Python path if not already added
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.database.db_connection import Base

class User(Base):
    """User model for authentication and profile information."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # OAuth related fields
    auth_provider = Column(String(20), nullable=True)  # 'google', 'custom', etc.
    oauth_id = Column(String(255), nullable=True)
    oauth_access_token = Column(Text, nullable=True)
    oauth_refresh_token = Column(Text, nullable=True)
    oauth_token_expires = Column(DateTime, nullable=True)
    profile_picture = Column(String(255), nullable=True)
    
    # User preferences and golf-related data
    handicap = Column(String(10), nullable=True)
    preferred_units = Column(String(10), default="yards")  # 'yards' or 'meters'
    
    # Define relationships to other models
    golf_rounds = relationship("GolfRound", back_populates="user")
    clubs = relationship("Club", back_populates="user")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert user model to dictionary.
        
        Returns:
            Dictionary representation of the user
        """
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "auth_provider": self.auth_provider,
            "profile_picture": self.profile_picture,
            "handicap": self.handicap,
            "preferred_units": self.preferred_units
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
        return cls(
            email=oauth_data.get("email"),
            full_name=oauth_data.get("name"),
            auth_provider=oauth_data.get("provider"),
            oauth_id=oauth_data.get("id"),
            profile_picture=oauth_data.get("picture"),
            is_active=True
        )