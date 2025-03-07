# Google OAuth Setup Guide for GolfStats

This guide explains how to set up Google OAuth for both test and production environments.

## Prerequisites

- A Google Cloud Platform (GCP) account
- Access to the Supabase dashboard for your test and production projects
- Administrative access to your Vercel project

## Step 1: Create OAuth Credentials in Google Cloud Platform

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" and select "OAuth client ID"
5. Select "Web application" as the application type
6. Set a name for your OAuth client (e.g., "GolfStats")
7. Add authorized JavaScript origins:
   - `http://localhost:8000` (for local development)
   - `https://golf-stats-chi.vercel.app` (for test environment)
   - `https://golfstats-prod.vercel.app` (for production environment)
8. Add authorized redirect URIs:
   - `http://localhost:8000/auth/google/callback` (for local development)
   - `https://golf-stats-chi.vercel.app/auth/google/callback` (for test environment)
   - `https://golfstats-prod.vercel.app/auth/google/callback` (for production environment)
9. Click "Create"
10. Note the Client ID and Client Secret for both environments

## Step 2: Configure Supabase Auth Settings

### For Test Environment

1. Log in to your [Supabase Dashboard](https://app.supabase.io/)
2. Select your test project (`qfuvwfghevxhnkfrwmwk`)
3. Go to "Authentication" > "URL Configuration"
4. Add the following Site URLs:
   - `http://localhost:8000`
   - `https://golf-stats-chi.vercel.app`
5. Add the following Redirect URLs:
   - `http://localhost:8000/auth/callback`
   - `http://localhost:8000/auth/google/callback`
   - `https://golf-stats-chi.vercel.app/auth/callback`
   - `https://golf-stats-chi.vercel.app/auth/google/callback`
6. Save the changes

### For Production Environment

1. Log in to your [Supabase Dashboard](https://app.supabase.io/)
2. Select your production project (`rrrniscrqsrbtfahgguo`)
3. Go to "Authentication" > "URL Configuration"
4. Add the following Site URLs:
   - `https://golfstats-prod.vercel.app`
5. Add the following Redirect URLs:
   - `https://golfstats-prod.vercel.app/auth/callback`
   - `https://golfstats-prod.vercel.app/auth/google/callback`
6. Save the changes

## Step 3: Configure Environment Variables

### For Local Development

Add the following to your `.env.test` file:

```
GOOGLE_CLIENT_ID=your-test-google-client-id
GOOGLE_CLIENT_SECRET=your-test-google-client-secret
```

### For Vercel Test Environment

Add the following environment variables in Vercel for preview deployments:

```
GOOGLE_CLIENT_ID=your-test-google-client-id
GOOGLE_CLIENT_SECRET=your-test-google-client-secret
```

### For Vercel Production Environment

Add the following environment variables in Vercel for production:

```
GOOGLE_CLIENT_ID=your-production-google-client-id
GOOGLE_CLIENT_SECRET=your-production-google-client-secret
```

## Step 4: Initialize User Profiles

After a user authenticates via Google OAuth for the first time, you'll need to create their user preferences record in the `user_preferences` table. This is handled automatically by the application, but you can also manually initialize user profiles:

```bash
# For test environment
python backend/database/init_user_profiles.py

# For production environment
APP_ENVIRONMENT=production python backend/database/init_user_profiles.py
```

## Step 5: Testing OAuth Flow

1. Start the application in test mode:
   ```bash
   python run.py
   ```

2. Navigate to `http://localhost:8000/auth/google/login`
3. You should be redirected to Google's login page
4. After successful authentication, you should be redirected back to your application

## Step 6: Common Errors and Troubleshooting

### Redirect URI Mismatch

If you see an error like "redirect_uri_mismatch", make sure:
- The redirect URI in Google Cloud Console exactly matches the one in your application
- The URI includes the proper protocol (`http://` or `https://`)
- There are no trailing slashes or spaces

### Invalid Client Secret

If authentication fails with "invalid_client", check:
- Your client secret is correct and up to date
- Environment variables are properly set
- No extra whitespace in your credentials

### Cookies or Session Issues

If the user stays logged out after authentication:
- Check that your application's secret key is properly set
- Ensure cookies are being set correctly
- Verify session storage is working properly

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Supabase Auth Documentation](https://supabase.io/docs/guides/auth)
- [Flask-OAuthlib Documentation](https://flask-oauthlib.readthedocs.io/)