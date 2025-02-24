# Golf Data Scrapers

This directory contains web scrapers for extracting golf data from various sources:

## Scrapers

### Trackman Scraper
- Connects to the Trackman website to extract shot data from practice sessions
- Provides detailed launch monitor data (ball speed, club speed, spin rate, etc.)
- Accessible via `get_trackman_data(user_id, limit)`

### Arccos Golf Scraper
- Extracts round data from Arccos Golf dashboard
- Provides detailed shot-by-shot data from actual rounds of golf
- Includes statistics like fairways hit, GIR, putts per round
- Accessible via `get_arrcos_data(user_id, limit)`

### SkyTrak Scraper
- Extracts shot data from SkyTrak practice sessions
- Provides detailed launch monitor data similar to Trackman
- Accessible via `get_skytrak_data(user_id, limit)`

## Usage

The scrapers can be used in two ways:

### 1. Direct Usage

```python
from backend.scrapers.trackman_scraper import get_trackman_data
from backend.scrapers.arccos_scraper import get_arrcos_data
from backend.scrapers.skytrak_scraper import get_skytrak_data

# Get Trackman data for a specific user
trackman_rounds = get_trackman_data(user_id=1, limit=10)

# Get Arccos data for a specific user
arccos_rounds = get_arrcos_data(user_id=1, limit=10)

# Get SkyTrak data for a specific user
skytrak_rounds = get_skytrak_data(user_id=1, limit=10)
```

### 2. Through ETL Process

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

## Authentication

Each scraper supports two authentication methods:

1. **Global credentials** defined in `.env` file
2. **User-specific credentials** stored in user profile in database

The scrapers will first check for user-specific credentials, then fall back to global credentials if needed.

## Error Handling

All scrapers include comprehensive error handling and logging to:
- Handle timeouts, missing elements, and other scraping issues
- Log all errors to log files (`logs/trackman_scraper.log`, etc.)
- Prevent crashes when one scraper fails