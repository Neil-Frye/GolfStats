"""
Cryptographic utilities for GolfStats application.

This module provides encryption functions for securing sensitive data.
"""
import os
import base64
import logging
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Configure logging
logger = logging.getLogger(__name__)

def get_encryption_key() -> bytes:
    """
    Get the encryption key from environment variable or generate one.
    
    Uses PBKDF2 to derive a key from the base key.
    
    Returns:
        Encryption key as bytes
    """
    # Get base key from environment
    base_key = os.environ.get('GOLFSTATS_ENCRYPTION_KEY')
    
    if not base_key:
        # Use a default key for development (NEVER DO THIS IN PRODUCTION)
        logger.warning("Using default encryption key - NOT SECURE FOR PRODUCTION")
        base_key = "golfstats_dev_only_key_replace_in_production"
    
    # Use a fixed salt (in production, consider a per-user salt stored securely)
    salt = b'GolfStats_fixed_salt'
    
    # Derive key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000
    )
    
    # Derive the key from the password
    return base64.urlsafe_b64encode(kdf.derive(base_key.encode()))

def encrypt_value(value: str) -> str:
    """
    Encrypt a string value.
    
    Args:
        value: The string to encrypt
        
    Returns:
        Encrypted string as base64
    """
    if not value:
        return ""
    
    try:
        key = get_encryption_key()
        f = Fernet(key)
        encrypted = f.encrypt(value.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    except Exception as e:
        logger.error(f"Encryption error: {str(e)}")
        # Return empty string on error (alternative: raise the exception)
        return ""

def decrypt_value(encrypted_value: str) -> str:
    """
    Decrypt an encrypted string.
    
    Args:
        encrypted_value: The encrypted string (base64 encoded)
        
    Returns:
        Decrypted string
    """
    if not encrypted_value:
        return ""
    
    try:
        key = get_encryption_key()
        f = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_value.encode())
        decrypted = f.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Decryption error: {str(e)}")
        # Return empty string on error (alternative: raise the exception)
        return ""