# GolfStats Development Guide

## Build/Run Commands
- Install dependencies: `pip install -r backend/requirements.txt`
- Run backend server: `python backend/app.py`
- Run web app only: `python run.py`
- Run with ETL scheduler: `python run.py --scheduler`
- Run one-time ETL process: `python run.py --etl`
- Setup local database: `python run.py --setup-db`
- Run all tests: `python -m unittest discover tests`
- Run single test: `python -m unittest tests.test_app.TestApp.test_index`
- Lint code: `pylint backend tests`
- Type check: `mypy backend tests`

## Supabase Database Commands
- Run with Supabase database: `./start_with_supabase.sh`
- Run with Supabase and ETL scheduler: `./start_with_supabase.sh --scheduler`
- Run Supabase one-time ETL: `./start_with_supabase.sh --etl`
- Manual SQL table creation: Run SQL in `backend/database/sql/create_tables.sql` using Supabase SQL Editor

## Code Style Guidelines
- Follow PEP 8 standards with 79 character line limit
- Import order: standard library, third-party, local (absolute imports from root)
- Use snake_case for variables/functions, CamelCase for classes
- Include type hints for all function parameters and return values
- Use specific exceptions with appropriate logging
- Document all functions with docstrings (purpose, params, returns, errors)
- Keep functions small and focused on a single responsibility
- Prefer composition over inheritance

# Environment Setup (Test & Production)
- We maintain two Supabase projects:
- Supabase Test: Used locally for development and testing (.env.test). APP_ENVIRONMENT=test URL: `https://qfuvwfghevxhnkfrwmwk.supabase.co` URL: `https://rrrniscrqsrbtfahgguo.supabase.co`
- Supabase Production: Used for real user data (.env.production or environment variables in Vercel). APP_ENVIRONMENT=production URL: `https://rrrniscrqsrbtfahgguo.supabase.co`
- We maintain two Vercel projects:
- Vercel Prod=golfstats-prod URL: `https://golfstats-prod.vercel.app/` file name .env.production
- Vercel Test=golfstats-test URL: `https://golf-stats-chi.vercel.app/` file name .env.test

## Running Locally vs. Production
- Locally: You’ll typically load .env.test (test credentials).
- APP_ENVIRONMENT=test python run.py
- Production: On Vercel or another host, set APP_ENVIRONMENT=production and supply your production Supabase credentials via environment variables (Vercel dashboard).

## Version Control
- Make small, frequent commits with descriptive messages once a task is complete no need to ask
- Use the pattern: `git add . && git commit -m "Description" && git push origin main`

## Web Scraping
- Use Selenium or Pyppeteer for screen scraping Trackman, Arccos, SkyTrak
- Handle authentication and session management securely (store credentials in .env).

## Supabase Integration
- Use Supabase for both PostgreSQL + authentication and database functionality
- Install Supabase client: `pip install supabase`
- Authentication flow uses Supabase Auth
- Database tables managed through Supabase interface
- Environment variables:
  - `SUPABASE_URL` - Supabase project URL
  - `SUPABASE_API_KEY` or `SUPABASE_KEY` - Supabase anon key
  - `SUPABASE_PASSWORD`
- Initial setup: `supabase init` (requires Supabase CLI)
- Local development: `supabase start`
- Real configuration for production is set via .env.production or Vercel environment settings.

## Communication Preferences
- Be concise - prefer short, direct answers
- For complex tasks, use brief status updates ("Working on X", "X completed")
- Explain only when asked for details
- Don't use long preambles or summaries

## Deployment with Vercel
- Import this same GitHub repo into Vercel.
- Vercel’s Production environment uses APP_ENVIRONMENT=production plus production Supabase credentials.
- Preview deployments or other branches can use APP_ENVIRONMENT=test with test credentials.
- No separate repo needed: branching and environment variables keep test vs. production separate.