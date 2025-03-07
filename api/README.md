# GolfStats Vercel Deployment

This directory contains the serverless API entry point for Vercel deployment.

## Deployment Optimizations

To keep the deployment size under Vercel's 250MB limit, the following optimizations have been implemented:

1. **Reduced Dependencies**: The `requirements.txt` file contains only essential packages needed for API functionality.

2. **Mock Scrapers**: Browser automation libraries (Selenium, Pyppeteer) are replaced with lightweight mock implementations for the serverless environment.

3. **File Exclusions**: The `.vercelignore` file excludes unnecessary files like tests, screenshots, and cache files.

4. **Selective Imports**: The deployment only includes required Python modules and avoids large binary dependencies.

## Deployment Configuration

The `vercel.json` file is configured to:

- Limit the size of the Lambda function
- Include only necessary files
- Exclude large binary files and unnecessary directories
- Set appropriate environment variables

## Important Notes

1. **Scraper Functionality**: In the Vercel environment, scraper functions return mock data. For full scraper functionality, use a non-serverless deployment.

2. **Environment Variables**: Make sure to set all required environment variables in the Vercel project settings, especially:
   - `SUPABASE_URL`
   - `SUPABASE_API_KEY`
   - `APP_ENVIRONMENT=production`

3. **Static Assets**: Frontend static files are served from the `frontend/` directory.

## Local Testing

To test the serverless setup locally:

```bash
pip install -r api/requirements.txt
vercel dev
```

## Deployment Commands

Deploy to Vercel:

```bash
vercel
```

Deploy to production:

```bash
vercel --prod
```

## Troubleshooting

If you encounter deployment issues:

1. Check the Vercel build logs for specific errors
2. Verify that all environment variables are correctly set
3. Ensure all dependencies in `requirements.txt` are compatible with Python 3.9
4. Make sure the mock scrapers are correctly implemented for API endpoints that use them