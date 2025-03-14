# GolfStats Environment Configuration

This directory contains the environment configuration system for the GolfStats application.

## Overview

The environment configuration is centralized in the `env.py` module, which provides a single source of truth for all environment variables and configuration settings.

## Files

- `env.py` - The main environment module that handles loading configuration from .env files and provides a consistent interface for accessing configuration values.
- `config.py` - A backward compatibility module that exports the configuration from `env.py`. This is maintained to ensure compatibility with existing code.

## Usage

### Basic Usage

```python
from config.env import env

# Access configuration values
supabase_url = env.get_supabase_url()
is_production = env.is_production()

# Direct dictionary-style access
app_debug = env["app"]["debug"]
```

### Environment Variables

The environment module loads configuration from the following sources, in order of precedence:

1. Environment variables set directly in the process
2. `.env.production` file (if `APP_ENVIRONMENT=production`)
3. `.env.test` file (if `APP_ENVIRONMENT=test` or not specified)
4. Default values defined in the `Environment` class

### Key Environment Variables

- `APP_ENVIRONMENT` - Controls which environment is loaded (`test` or `production`)
- `DB_TYPE` - The database type (`sqlite`, `postgresql`, `supabase`, or `mongodb`)
- `SUPABASE_URL` - The Supabase project URL
- `SUPABASE_API_KEY` / `SUPABASE_KEY` - The Supabase API key
- `SUPABASE_PASSWORD` - The Supabase database password (for direct database connections)

See `env.py` for a complete list of supported environment variables and their default values.

## Helper Methods

The `Environment` class provides several helper methods for common tasks:

- `get_config()` - Returns the full configuration dictionary
- `get_database_uri()` - Returns the database URI based on the configured database type
- `get_db_connect_args()` - Returns the database connection arguments
- `get_db_pool_settings()` - Returns the database connection pool settings
- `get_masked_config()` - Returns a copy of the configuration with sensitive values masked
- `is_production()` - Returns whether the application is running in production mode
- `is_test()` - Returns whether the application is running in test mode
- `get_database_type()` - Returns the configured database type
- `get_supabase_url()` - Returns the Supabase project URL
- `get_supabase_key()` - Returns the Supabase API key

## Environment Files

The environment module looks for the following files:

- `.env.test` - Environment variables for the test environment
- `.env.production` - Environment variables for the production environment

These files should be placed in the project root directory.

## Security

Be sure to add `.env.*` files to your `.gitignore` to prevent accidentally committing sensitive credentials to version control.