# Vercel Deployment Size Optimization

This document explains the approach taken to optimize the GolfStats application for Vercel deployment, specifically addressing the 250MB serverless function size limit.

## Problem: Heavyweight Dependencies

The main challenges faced were:

1. **Browser automation libraries**: Selenium, Pyppeteer, and webdriver-manager are extremely large
2. **Python package bloat**: Many dependencies pulling in their own large subdependencies
3. **Full application code**: Trying to deploy the entire backend with scraping logic to Vercel

## Solution: Strict Separation of Concerns

We implemented a "strict separation" approach where:

1. The Vercel deployment contains ONLY the minimal API endpoints
2. All heavy dependencies (scrapers, ETL) run elsewhere (e.g., GitHub Actions, dedicated server)
3. Mock implementations provide API compatibility for serverless functions

## Key Implementation Details

### 1. Strict Allowlist in `.vercelignore`

We use an allowlist approach in `.vercelignore`, explicitly allowing ONLY:
- `api/index.py` - Standalone serverless implementation
- `api/requirements.txt` - Minimal dependencies
- `api/mock_scrapers.py` - Lightweight mock implementations
- `vercel.json` and `vercel-build.sh` - Build configuration
- `frontend/` - Static frontend files

Everything else is excluded by default.

### 2. Minimal API Requirements

The `api/requirements.txt` file contains only:
- Flask - For API routes
- python-dotenv - For environment variables
- Werkzeug - Required by Flask
- supabase - For data access

Notably excluded:
- psycopg2-binary (database driver - supabase handles this)
- All browser automation libraries
- All test/development libraries

### 3. Standalone API Implementation

The API endpoints in `api/index.py` are:
- Completely self-contained
- Do NOT import from the main backend/ code
- Use mock_scrapers.py for any scraper functionality
- Have explicit error handling

### 4. Mock Scraper Implementations

In `api/mock_scrapers.py`, we provide:
- API-compatible mock classes for all scrapers
- Lightweight implementations that return structured empty data
- No browser automation dependencies

### 5. Size Verification in Build

The `vercel-build.sh` script:
- Installs only minimal dependencies
- Verifies forbidden packages are not present
- Creates a size estimation bundle
- Warns if estimated deployment size exceeds limits

### 6. Environment Configuration

The `vercel.json` file:
- Explicitly includes only necessary files
- Sets appropriate memory and timeout limits
- Configures environment variables for serverless mode

## Continuous Integration / GitHub Actions

For data collection that would normally use heavy dependencies:
- Schedule GitHub Actions workflows to run scrapers
- Store results in the database
- Let Vercel API endpoints read from the database (no scraping)

## Local Development vs. Vercel

For local development:
- Use the full backend with all dependencies
- For testing the Vercel deployment, run just the API standalone

## Results

- Deployment size reduced from ~300MB+ to under 100MB
- No timeout issues during Vercel builds
- Clear separation between lightweight API and heavyweight backend processing