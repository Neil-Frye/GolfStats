# Vercel Size Optimization Guide

## Problem: Exceeding 250MB Serverless Function Size Limit

The GolfStats application was hitting Vercel's strict 250MB limit due to:

1. Heavy dependencies (Selenium, Pyppeteer, webdriver-manager)
2. Unnecessary files being included in the deployment
3. Inefficient module organization

## Solution Overview

We implemented a comprehensive fix with these key components:

### 1. Module Mocking Strategy

We now intercept module loading in `api/index.py` to replace heavy scraper implementations with lightweight mocks:

```python
# Replace heavy scraper modules with lightweight mocks
sys.modules['backend.scrapers.arccos_scraper'] = importlib.import_module('api.mock_scrapers')
sys.modules['backend.scrapers.trackman_scraper'] = importlib.import_module('api.mock_scrapers') 
sys.modules['backend.scrapers.skytrak_scraper'] = importlib.import_module('api.mock_scrapers')
```

This maintains API compatibility while drastically reducing bundle size.

### 2. Optimized Dependencies

We updated `api/requirements.txt` to remove:
- Browser automation tools (Selenium, Pyppeteer)
- Testing frameworks
- Other non-essential packages

Dependencies like pandas were minimized or removed where possible.

### 3. Aggressive File Exclusion

Updated `.vercelignore` to exclude:
- Test files and directories
- Original scraper implementations
- Data, logs, and screenshots
- ETL and scheduler code not needed in serverless

### 4. Enhanced Vercel Configuration

Updated `vercel.json` with:
- Memory allocation (1024MB)
- Function timeout settings (10 seconds)
- Environment variables
- Optimized routing

### 5. Improved Build Script

Optimized `vercel-build.sh` with:
- Detailed logging
- Size checking
- Optimized static asset handling

## Implementation Benefits

This architecture:
1. Maintains API compatibility
2. Provides proper functionality in Vercel's environment
3. Keeps the same codebase for both serverless and traditional deployments
4. Creates a clear separation between API and data processing

## Usage Notes

With this implementation:
- API endpoints work normally on Vercel
- Scraper endpoints return mock data
- Data processing should occur in a separate process/service
- Database and authentication functionality work as expected

## Deployment Instructions

1. Push these changes to your repository
2. Deploy to Vercel: `vercel --prod`
3. Verify all endpoints function correctly

## Maintenance Guidelines

1. Monitor Vercel deploy logs for size warnings
2. Test locally before deploying: `vercel deploy --prebuilt`
3. Be cautious when adding new dependencies
4. Keep browser automation code properly mocked

## Long-Term Architecture Recommendations

For a more comprehensive solution:
1. Split into microservices (API + data processing)
2. Use containers for scraping (Google Cloud Run, AWS ECS)
3. Implement API-first design instead of browser automation
4. Consider platforms without serverless size limits for components with large dependencies

---

*Note: These changes create a specialized deployment for Vercel. The full application with scraping capabilities should be deployed on a platform without these size constraints.*