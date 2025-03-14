"""
Authentication module for GolfStats application.

This module provides authentication utilities using Supabase Auth.
"""
from backend.auth.supabase_auth import (
    login_with_email,
    logout,
    sign_up,
    get_current_user,
    is_authenticated,
    require_auth,
    get_authenticated_user,
    verify_jwt
)

from .crypto_utils import encrypt_value, decrypt_value

def init_app(app):
    """Initialize authentication for the Flask app."""
    # We don't need any initialization in supabase_auth, so this is a no-op
    pass