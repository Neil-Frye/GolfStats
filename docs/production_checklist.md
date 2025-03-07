# Production Environment Checklist

Use this checklist to ensure your GolfStats production environment is properly configured and ready to use.

## 1. Supabase Production Setup

- [ ] Created a new Supabase project for production (`rrrniscrqsrbtfahgguo`)
- [ ] Obtained the production URL and API key
- [ ] Created `.env.production` file with production credentials
- [ ] Ran `python backend/database/setup_production.py` to create tables
- [ ] Verified all tables were created successfully
- [ ] Configured Supabase Auth redirect URLs (see Google OAuth setup guide)
- [ ] Set up Row Level Security (RLS) policies for all tables
- [ ] Created a test user account and verified authentication works

## 2. Google OAuth Configuration

- [ ] Created OAuth 2.0 credentials in Google Cloud Console
- [ ] Added proper redirect URIs for the production environment
- [ ] Added client ID and secret to `.env.production`
- [ ] Added client ID and secret to Vercel environment variables
- [ ] Tested the OAuth flow in production environment
- [ ] Verified user preferences are created after first login

## 3. Vercel Deployment

- [ ] Connected GitHub repository to Vercel
- [ ] Set all required environment variables:
  - [ ] `APP_ENVIRONMENT=production`
  - [ ] `SUPABASE_URL`
  - [ ] `SUPABASE_API_KEY`
  - [ ] `APP_SECRET_KEY`
  - [ ] `GOOGLE_CLIENT_ID`
  - [ ] `GOOGLE_CLIENT_SECRET`
- [ ] Deployed to production
- [ ] Verified the API is working
- [ ] Verified frontend is loading properly
- [ ] Confirmed the application is using the production database

## 4. Testing the Production Environment

- [ ] Successfully logged in with Google OAuth
- [ ] Created and retrieved golf rounds
- [ ] Verified data is isolated between users
- [ ] Confirmed no test data is in the production database
- [ ] Checked all major functionality works as expected:
  - [ ] Authentication
  - [ ] Creating/reading/updating/deleting golf rounds
  - [ ] Viewing statistics
  - [ ] User preferences
- [ ] Tested on multiple devices and browsers

## 5. Security Verification

- [ ] Confirmed environment variables are properly secured
- [ ] Verified RLS policies are properly enforcing data isolation
- [ ] Checked for exposed API endpoints that should be protected
- [ ] Ensured no sensitive data is being logged
- [ ] Verified HTTPS is enforced for all connections
- [ ] Confirmed JWT tokens are properly validated
- [ ] Tested session timeout and token refresh

## 6. Data Backup & Monitoring

- [ ] Set up database backups for the production Supabase instance
- [ ] Configured error logging and monitoring
- [ ] Established a process for regular data backups
- [ ] Created a disaster recovery plan
- [ ] Set up alerts for critical errors

## 7. Documentation & Administrative Access

- [ ] Updated documentation with production environment details
- [ ] Created administrative accounts for system administrators
- [ ] Documented the process for creating new user accounts
- [ ] Established procedures for database maintenance
- [ ] Created user guides for end users

## 8. Cleanup & Final Verification

- [ ] Removed any temporary test accounts
- [ ] Verified all credentials are secure
- [ ] Confirmed all test/debug code is disabled in production
- [ ] Conducted a final end-to-end test of all critical functionality
- [ ] Documented any known issues or limitations

---

## IMPORTANT Reminders

1. **Never use test credentials in production**
2. **Always maintain separate databases for test and production**
3. **Regularly rotate API keys and credentials**
4. **Monitor the production environment for errors and performance issues**
5. **Back up production data regularly**
6. **Keep all dependencies updated, especially those with security fixes**