"""
Credential Migration Script for GolfStats
Migrates plaintext passwords to encrypted storage using Supabase Vault
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CredentialMigrator:
    """Handles migration of plaintext credentials to encrypted storage"""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize the migrator with Supabase credentials"""
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.encryption_key = self._get_or_create_encryption_key()
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create an encryption key for credential storage"""
        # In production, this should use Supabase Vault or AWS KMS
        # For now, we'll use a local key (should be stored securely)
        key_file = '.encryption_key'
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            logger.info("Generated new encryption key")
            return key
    
    def encrypt_credentials(self, username: str, password: str) -> str:
        """Encrypt username and password into a single encrypted string"""
        fernet = Fernet(self.encryption_key)
        
        credentials = {
            'username': username,
            'password': password,
            'encrypted_at': datetime.utcnow().isoformat()
        }
        
        json_str = json.dumps(credentials)
        encrypted = fernet.encrypt(json_str.encode())
        return encrypted.decode()
    
    def decrypt_credentials(self, encrypted_data: str) -> Dict[str, str]:
        """Decrypt credentials from encrypted string"""
        fernet = Fernet(self.encryption_key)
        
        try:
            decrypted = fernet.decrypt(encrypted_data.encode())
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"Failed to decrypt credentials: {e}")
            return {}
    
    def get_users_with_credentials(self) -> List[Dict]:
        """Get all users who have plaintext credentials stored"""
        try:
            response = self.supabase.table('user_preferences').select(
                'user_id, trackman_username, arccos_username, skytrak_username'
            ).execute()
            
            users_to_migrate = []
            for user_pref in response.data:
                services = []
                if user_pref.get('trackman_username'):
                    services.append('trackman')
                if user_pref.get('arccos_username'):
                    services.append('arccos')
                if user_pref.get('skytrak_username'):
                    services.append('skytrak')
                
                if services:
                    users_to_migrate.append({
                        'user_id': user_pref['user_id'],
                        'services': services
                    })
            
            return users_to_migrate
            
        except Exception as e:
            logger.error(f"Failed to get users with credentials: {e}")
            return []
    
    def migrate_user_credentials(self, user_id: str, dry_run: bool = True) -> bool:
        """Migrate credentials for a specific user"""
        try:
            # Get user's current preferences
            response = self.supabase.table('user_preferences').select('*').eq(
                'user_id', user_id
            ).single().execute()
            
            if not response.data:
                logger.warning(f"No preferences found for user {user_id}")
                return False
            
            user_prefs = response.data
            migrated_services = []
            
            # Check each service
            services = [
                ('trackman', 'trackman_username', 'trackman_password'),
                ('arccos', 'arccos_username', 'arccos_password'),
                ('skytrak', 'skytrak_username', 'skytrak_password')
            ]
            
            for service_name, username_field, password_field in services:
                username = user_prefs.get(username_field)
                # Note: In the current schema, passwords are stored separately
                # This is a placeholder - you'll need to retrieve passwords from wherever they're stored
                password = user_prefs.get(password_field, '')  # This would be the plaintext password
                
                if username and password:
                    encrypted = self.encrypt_credentials(username, password)
                    
                    if not dry_run:
                        # Insert into new api_credentials table
                        self.supabase.table('api_credentials').upsert({
                            'user_id': user_id,
                            'service_name': service_name,
                            'encrypted_credentials': encrypted,
                            'encryption_key_id': 'local_key_v1',  # In production, use vault key ID
                            'is_active': True
                        }).execute()
                        
                        logger.info(f"Migrated {service_name} credentials for user {user_id}")
                    else:
                        logger.info(f"[DRY RUN] Would migrate {service_name} credentials for user {user_id}")
                    
                    migrated_services.append(service_name)
            
            if migrated_services and not dry_run:
                # Mark user as migrated
                self.supabase.table('user_preferences').update({
                    'credentials_migrated': True,
                    'migration_date': datetime.utcnow().isoformat()
                }).eq('user_id', user_id).execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate credentials for user {user_id}: {e}")
            return False
    
    def migrate_all_users(self, dry_run: bool = True):
        """Migrate all users with stored credentials"""
        users = self.get_users_with_credentials()
        
        if not users:
            logger.info("No users found with credentials to migrate")
            return
        
        logger.info(f"Found {len(users)} users with credentials to migrate")
        
        success_count = 0
        for user_info in users:
            user_id = user_info['user_id']
            services = user_info['services']
            
            logger.info(f"Processing user {user_id} with services: {services}")
            
            if self.migrate_user_credentials(user_id, dry_run):
                success_count += 1
        
        logger.info(f"Migration completed: {success_count}/{len(users)} users processed successfully")
        
        if dry_run:
            logger.info("This was a DRY RUN. Run with dry_run=False to perform actual migration")


def main():
    """Main migration function"""
    # Get Supabase credentials from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_API_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("Missing SUPABASE_URL or SUPABASE_API_KEY environment variables")
        return
    
    # Create migrator
    migrator = CredentialMigrator(supabase_url, supabase_key)
    
    # First, do a dry run to see what would be migrated
    logger.info("Starting credential migration (DRY RUN)")
    migrator.migrate_all_users(dry_run=True)
    
    # Ask for confirmation
    response = input("\nProceed with actual migration? (yes/no): ")
    if response.lower() == 'yes':
        logger.info("Starting actual credential migration")
        migrator.migrate_all_users(dry_run=False)
    else:
        logger.info("Migration cancelled")


if __name__ == "__main__":
    main()