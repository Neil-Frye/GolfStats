# Golf Data Scrapers

This directory contains web scrapers for extracting golf data from various sources.

## Unified Scraper Architecture

GolfStats provides a unified scraper architecture that works in both:
- Regular environments with Selenium (full web scraping capabilities)
- Serverless environments without Selenium (graceful fallback to mock implementations)

### Key Components

1. **Real Scrapers**:
   - `arccos_scraper.py`: Extracts data from Arccos Golf using Selenium
   - `trackman_scraper.py`: Extracts data from Trackman using Selenium
   - `skytrak_scraper.py`: Extracts data from SkyTrak using Selenium

2. **Mock Implementations**:
   - `mock.py`: Provides mock implementations for serverless environments
   - Used automatically when Selenium is not available

3. **Unified Interface**:
   - Accessible via the scrapers module (`import backend.scrapers`)
   - Same function signatures work in all environments
   - Intelligent fallback to mocks when needed

## Usage

The preferred way to use scrapers is through the unified interface:

```python
from backend.scrapers import get_arccos_data, get_trackman_data, get_skytrak_data

# Get Trackman data for a specific user
trackman_sessions = get_trackman_data(user_id=1, limit=10)

# Get Arccos data for a specific user
arccos_rounds = get_arccos_data(user_id=1, limit=10)

# Get SkyTrak data for a specific user
skytrak_sessions = get_skytrak_data(user_id=1, limit=10)
```

The unified interface will:
1. Try to use the real scrapers with Selenium if available
2. Fall back to mock implementations if Selenium is not available
3. Handle exceptions gracefully and log appropriate messages

## Authentication

Each scraper supports two authentication methods:

1. **Global credentials** defined in the `.env` file
2. **User-specific credentials** stored in user profile in the database

The scrapers will first check for user-specific credentials, then fall back to global credentials if needed.

## ETL Process Integration

The ETL process automatically runs all scrapers for all active users:

```python
from backend.etl.daily_etl import run_daily_etl

# Run the ETL process to collect data from all sources
results = run_daily_etl()
print(f"Processed {results['users_processed']} users")
print(f"Trackman Sessions: {results['trackman_sessions']}")
print(f"Arccos Rounds: {results['arccos_rounds']}")
print(f"SkyTrak Sessions: {results['skytrak_sessions']}")
```

## Error Handling

All scrapers include comprehensive error handling and logging to:
- Handle timeouts, missing elements, and other scraping issues
- Log all errors to log files (`logs/trackman_scraper.log`, etc.)
- Prevent crashes when one scraper fails

## Extending with New Scrapers

To add a new scraper:
1. Create a new real scraper file in the `scrapers` directory
2. Add corresponding mock implementation in `mock.py`
3. Update the `__init__.py` file to include the new scraper in the unified interface