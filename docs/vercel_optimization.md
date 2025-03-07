# Vercel Deployment Optimization

This document explains the optimizations made to deploy the GolfStats application on Vercel serverless platform while staying within the 250MB function size limit.

## Problem

Vercel has a 250MB unzipped function size limit. The initial deployment was exceeding this limit due to:

1. Large dependencies (Selenium, Pyppeteer, etc.)
2. Inclusion of unnecessary files (test files, logs, screenshots, etc.)
3. Inefficient packaging of Python libraries

## Solution Overview

The optimization strategy involved:

1. Streamlining dependencies for the serverless environment
2. Creating mock implementations of browser automation code
3. Configuring proper file exclusions
4. Adding serverless detection and adaptation in the application

## Implementation Details

### 1. Dependency Optimization

The `api/requirements.txt` file was optimized to include only essential packages needed for API functionality:

```
# Core dependencies only (minimal runtime requirements)
Flask==2.3.2
requests==2.31.0
sqlalchemy==2.0.20
google-auth==2.23.0
google-auth-oauthlib==1.0.0
python-dotenv==1.0.0
email-validator==2.0.0
Werkzeug==2.3.7
psycopg2-binary==2.9.9
sqlalchemy-utils==0.41.1
supabase==1.0.3
cryptography==41.0.3
APScheduler==3.10.1
```

Notably removed:
- `pandas` (large dependency)
- `selenium`, `webdriver-manager`, `pyppeteer` (browser automation)
- `pymongo` (not needed for serverless API)
- Testing tools like `pytest`

### 2. Mock Implementations

Created `api/mock_scrapers.py` to provide lightweight API-compatible versions of browser-based scrapers without the heavy dependencies:

- Added base `MockScraperBase` class
- Implemented mock classes for each scraper (Arccos, Trackman, SkyTrak)
- Modified the serverless entry point to use these mocks via module substitution

### 3. File Exclusions

Created a `.vercelignore` file to exclude unnecessary files:

```
# Python cache files
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/

# Virtual environments
venv/
env/
ENV/

# Data and log files
data/
logs/

# Development files
tests/
.git/
.github/
.vscode/
.idea/

# Screenshots and large binary files
**/screenshots/
**/*.png
**/*.jpg
**/*.jpeg

# Documentation
docs/

# Selenium drivers
**/drivers/
**/webdriver/
**/selenium/
chromedriver*

# Development config
.env.test
```

### 4. Vercel Configuration

Updated `vercel.json` to:

- Specify Python 3.9 runtime
- Set a reasonable Lambda size limit (50MB)
- Explicitly include essential files
- Exclude test and data files
- Set environment variables

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "runtime": "python3.9",
        "maxLambdaSize": "50mb",
        "includeFiles": [
          "api/**",
          "backend/**/*.py",
          "backend/auth/**",
          "backend/database/**",
          "backend/models/**",
          "config/**"
        ],
        "excludeFiles": [
          "**/__pycache__/**",
          "**/*.pyc",
          "**/*.pyo",
          "**/*.pyd",
          "**/.pytest_cache/**",
          "**/tests/**",
          "**/selenium/**",
          "**/webdriver/**",
          "**/data/**",
          "**/logs/**",
          "**/docs/**"
        ]
      }
    },
    {
      "src": "frontend/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ],
  "env": {
    "PYTHONPATH": ".",
    "APP_ENVIRONMENT": "production"
  }
}
```

### 5. Serverless Mode Detection

Modified `backend/app.py` to detect the serverless environment and adjust behavior:

```python
# Detect if we're running in Vercel serverless environment
is_serverless = os.environ.get('VERCEL') == '1' or 'SERVERLESS_CONTEXT' in os.environ

if is_serverless:
    logger.info("Detected serverless environment - applying optimizations")
    # In serverless, disable some features to reduce size and dependencies
    app.config['SERVERLESS'] = True
```

## Deployment Steps

1. Push these changes to the repository
2. Deploy to Vercel with: `vercel --prod`
3. Verify deployment via health check endpoint: `/health`

## Limitations

In the serverless environment:

1. Browser automation features (scrapers) return mock data
2. Data analysis capabilities are limited (no pandas)
3. Debug mode is disabled to improve performance

For full functionality including web scraping, a traditional (non-serverless) deployment is recommended.

## Future Improvements

1. Consider splitting the app into separate services:
   - API service (lightweight, suitable for serverless)
   - Data processing service (heavier, better for traditional hosting)
   - Scraper service (with browser automation, on separate infrastructure)

2. Implement a feature flag system to gracefully handle missing functionality in serverless mode

3. Set up a scheduled job outside of Vercel for ETL processes that require browser automation

4. Consider using Docker-based deployments for components requiring specific dependencies