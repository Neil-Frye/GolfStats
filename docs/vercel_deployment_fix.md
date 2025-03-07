# Vercel Deployment Fix for Cryptography Module

## Issue Description

The application is failing in the Vercel production environment with this error:

```
ModuleNotFoundError: No module named 'cryptography'
```

This occurs because the authentication system requires the `cryptography` Python package, which was missing from our requirements and deployment configuration.

## Fixed Files

1. Added `cryptography==41.0.3` to:
   - `/backend/requirements.txt`
   - `/api/requirements.txt`

2. Updated Vercel deployment configuration:
   - Added configuration in `vercel.json` to include cryptography explicitly
   - Created `vercel-build.sh` for the build process
   - Added `package.json` with build scripts
   - Created `api/build.sh` script to install system dependencies

## Deployment Steps

To fix this issue in your Vercel production environment:

1. Pull these changes to your local repository.

2. Push the changes to your GitHub repository that's connected to Vercel.

3. Vercel should automatically trigger a new deployment with the updated configuration.

4. Verify the build logs to ensure that the cryptography package is being installed correctly.

## Manual Configuration in Vercel (if needed)

If the automatic deployment doesn't resolve the issue, follow these steps in the Vercel dashboard:

1. Go to your Vercel project settings.

2. Navigate to the "Build & Development Settings" section.

3. Make sure that the "Install Command" is set to `pip install -r api/requirements.txt`.

4. Ensure that environment variables are properly configured, especially:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REDIRECT_URI` (set to https://golfstats-prod.vercel.app/api/auth/google/callback)
   - `SUPABASE_URL`
   - `SUPABASE_API_KEY`
   - `APP_ENVIRONMENT` (set to production)

5. Trigger a manual redeployment from the "Deployments" tab.

## Monitoring & Verification

After redeployment:

1. Check the Vercel logs for any remaining errors.
2. Test the Google OAuth login flow.
3. Verify that the auth APIs (/api/auth/google/login, /api/auth/me) are working correctly.

If you encounter persistent issues, you may need to add additional system dependencies through Vercel's Advanced Build Settings.