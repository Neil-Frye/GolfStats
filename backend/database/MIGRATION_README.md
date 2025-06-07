# GolfStats Database Migration Guide

## Overview

This migration addresses critical security vulnerabilities and adds comprehensive analytics features to the GolfStats application.

## Critical Issues Addressed

### 1. Security Vulnerabilities
- **Issue**: User credentials stored in plaintext in `user_preferences` table
- **Fix**: Created encrypted `api_credentials` table with proper encryption
- **Impact**: All user API passwords are now encrypted before storage

### 2. Data Integrity
- **Issue**: Missing foreign key constraints allowing orphaned records
- **Fix**: Added proper user_id foreign keys and constraints to `golf_shots` table
- **Impact**: Ensures all shots are properly associated with users

### 3. Duplicate Import Prevention
- **Issue**: No mechanism to prevent duplicate data imports
- **Fix**: Added unique constraints and external_id tracking
- **Impact**: Prevents the same data from being imported multiple times

## New Features Added

### Analytics & Tracking
- Practice goals and progress tracking
- Course management with detailed hole information
- Weather impact analysis
- Equipment change history
- Performance benchmarks vs. handicap levels
- Practice drills and session tracking
- Handicap history tracking
- Shot dispersion patterns

### Performance Optimizations
- Materialized views for complex queries
- Proper indexes on frequently queried columns
- Analytical views for strokes gained and trends

## Migration Files

1. **critical_security_and_integrity_fixes.sql**
   - Must be run FIRST
   - Addresses security vulnerabilities
   - Adds data integrity constraints
   - Creates import tracking tables

2. **comprehensive_analytics_enhancements.sql**
   - Run after security fixes
   - Adds new analytics tables
   - Creates views and functions
   - Includes sample benchmark data

3. **migration_guide.sql**
   - Step-by-step migration instructions
   - Verification queries
   - Rollback scripts (if needed)

4. **migrate_credentials.py**
   - Python script to migrate existing credentials
   - Handles encryption of existing plaintext passwords
   - Includes dry-run mode for safety

## Migration Steps

### 1. Backup Database
```bash
# Using Supabase dashboard or CLI
supabase db dump -f backup_before_migration.sql
```

### 2. Apply Security Fixes
```sql
-- In Supabase SQL Editor
-- Run the entire contents of critical_security_and_integrity_fixes.sql
```

### 3. Apply Analytics Enhancements
```sql
-- In Supabase SQL Editor
-- Run the entire contents of comprehensive_analytics_enhancements.sql
```

### 4. Migrate Existing Credentials (if any)
```bash
# From backend/database directory
python migrate_credentials.py
```

### 5. Update Application Code

#### Update Authentication Code
Replace plaintext password storage with encrypted credentials:

```python
# OLD CODE (remove this)
user_prefs = {
    'trackman_username': username,
    'trackman_password': password  # INSECURE
}

# NEW CODE (use this)
from backend.database.migrate_credentials import CredentialMigrator

migrator = CredentialMigrator(supabase_url, supabase_key)
encrypted = migrator.encrypt_credentials(username, password)

api_creds = {
    'user_id': user_id,
    'service_name': 'trackman',
    'encrypted_credentials': encrypted,
    'encryption_key_id': 'vault_key_v1'
}
```

#### Update Import Logic
Use new import tracking:

```python
# Create import log
import_log = supabase.table('import_logs').insert({
    'user_id': user_id,
    'source_system': 'trackman',
    'import_type': 'incremental',
    'status': 'processing'
}).execute()

# Track each shot with external_id
shot_data['external_id'] = trackman_shot_id
shot_data['import_batch_id'] = import_log.data['id']
```

### 6. Verify Migration

Run the verification queries from migration_guide.sql:

```sql
-- Check security fixes
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'user_preferences' 
  AND column_name LIKE '%password%';
-- Should return no rows

-- Check new tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN ('api_credentials', 'import_logs', 'practice_goals');
-- Should return all tables
```

## Post-Migration Tasks

### 1. Set Up Scheduled Jobs

```python
# Add to scheduler.py
@scheduler.scheduled_job('cron', hour=2)
def refresh_materialized_views():
    """Refresh materialized views daily"""
    supabase.rpc('refresh_user_statistics').execute()

@scheduler.scheduled_job('cron', day_of_week='mon', hour=3)
def update_shot_patterns():
    """Update shot patterns weekly"""
    # Implementation here
```

### 2. Configure Encryption Keys

For production, use Supabase Vault:

```sql
-- Create vault secret
INSERT INTO vault.secrets (name, secret)
VALUES ('api_credential_key', 'your-strong-encryption-key');
```

### 3. Update API Documentation

Document new endpoints for:
- Practice goals CRUD operations
- Weather condition tracking
- Equipment change logging
- Performance benchmark comparisons

## Rollback Plan

If issues arise, rollback scripts are provided in migration_guide.sql. However:

⚠️ **WARNING**: Do not rollback security fixes unless absolutely necessary. Instead, fix forward.

## Monitoring

After migration, monitor:
1. Application logs for encryption/decryption errors
2. Import success rates
3. Query performance on new tables
4. Materialized view refresh times

## Support

For issues or questions:
1. Check migration logs in import_logs table
2. Review error messages in application logs
3. Verify all migration steps were completed