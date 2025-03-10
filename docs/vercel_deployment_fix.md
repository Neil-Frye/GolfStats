# Vercel Deployment Fix: Solving the 250MB Size Limit Issue

This document outlines the specific measures taken to fix Vercel deployment issues related to the 250MB size limit, with a particular focus on ensuring that only minimal dependencies are included in the serverless function.

## Core Issue

Vercel serverless functions have a 250MB size limit. Our original deployment was failing because:

1. The entire codebase was being included, with all heavy dependencies
2. Browser automation libraries (Selenium, Pyppeteer) were being pulled in 
3. Configuration was not strict enough to prevent unwanted inclusions

## Critical Files and Their Roles

### 1. `.vercelignore`

- Uses a strict allowlist approach: block everything first with `*`, then allow only specific files
- Only explicitly allows:
  - `api/index.py`
  - `api/requirements.txt`
  - `api/mock_scrapers.py`
  - `vercel.json`
  - `vercel-build.sh`
  - `frontend/**` (if needed)
- Explicitly blocks heavy directories like `backend/`, `tests/`, etc.

### 2. `vercel.json`

- The `functions` section uses both `includeFiles` and `excludeFiles`:
  ```json
  "functions": {
    "api/index.py": {
      "memory": 1024,
      "maxDuration": 10,
      "runtime": "python3.9",
      "includeFiles": [
        "api/index.py",
        "api/requirements.txt",
        "api/mock_scrapers.py"
      ],
      "excludeFiles": [
        "**"
      ]
    }
  }
  ```
- `installCommand` is set to `pip install -r api/requirements.txt` (NOT the main requirements.txt)
- `buildCommand` is set to `bash vercel-build.sh`
- Sets `VERCEL_STRICT_BUILD=true` to enable additional safeguards

### 3. `api/requirements.txt`

- Ultra-minimal requirements including only:
  - Flask
  - python-dotenv
  - supabase
- Explicitly excludes heavyweight dependencies like:
  - selenium, webdriver-manager, pyppeteer
  - psycopg2-binary, cryptography
  - Any other non-essential packages

### 4. `vercel-build.sh`

- Contains multiple safeguards to prevent deployment failures:
  - Checks for the presence of `backend/` directory and warns if found
  - Creates a minimal build context when `VERCEL_STRICT_BUILD=true`
  - Explicitly installs only from `api/requirements.txt`
  - Warns if the main `requirements.txt` is found (but does not use it)
  - Performs deep package checks for heavyweight dependencies
  - Estimates deployment size and warns if it might exceed limits

### 5. `api/index.py` and `api/mock_scrapers.py`

- Standalone implementation that doesn't import from the backend code
- All dependencies are minimal and explicitly declared
- Uses mock implementations instead of real scrapers
- No accidental imports of backend modules

## Deployment Process

1. **Push code to GitHub**: Make sure `.vercelignore` and `vercel.json` are committed
2. **Watch Vercel logs**: The build script will output detailed information
3. **Check for warnings**: Address any warnings about size or dependencies
4. **Verify API endpoints**: Make sure your API endpoints work as expected

## Troubleshooting

If you continue to see deployment failures:

1. **Enable Strict Build Mode**: Set `VERCEL_STRICT_BUILD=true` in Vercel's environment variables
2. **Check Vercel logs**: Look for mentions of problematic packages
3. **Verify excludes are working**: The build logs should show minimal files being included
4. **Check for transitive dependencies**: Some packages might pull in others indirectly

## Long-term Strategy

For the heavyweight parts of the application:
- Consider running scrapers and ETL processes via GitHub Actions
- Store results in your database
- Let the lightweight Vercel API just read from the database

This separation of concerns keeps your API endpoints fast and deployable while still maintaining full functionality.