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
- Supabase Production: Used for real user data (.env.production or environment variables in Render). APP_ENVIRONMENT=production URL: `https://rrrniscrqsrbtfahgguo.supabase.co`
- We maintain two Vercel projects:
- Render Prod=golfstats-prod URL: `https://golfstats-jzfs.onrender.com` file name .env.production
- Render Test=golfstats-test URL: `https://golf-stats-chi.vercel.app/` file name .env.test

## Running Locally vs. Production
- Locally: You’ll typically load .env.test (test credentials).
- APP_ENVIRONMENT=test python run.py
- Production: On Vercel or another host, set APP_ENVIRONMENT=production and supply your production Supabase credentials via environment variables (Render dashboard).

## Version Control
- Make small, frequent commits with descriptive messages once a task is complete no need to ask
- Use the pattern: `git add . && git commit -m "Description" && git push origin main`
- Please do not say or add the words 'claude code' in the git descriptions when doing any commits

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

## Deployment with Render
- We have already import this GitHub repo into render.
- Render's Production environment uses APP_ENVIRONMENT=production plus production Supabase credentials.
- Preview deployments or other branches can use APP_ENVIRONMENT=test with test credentials.
- No separate repo needed: branching and environment variables keep test vs. production separate.

## Environment Awareness
- **Respect dev/test/prod**: Always ensure changes consider the unique requirements of each environment. Do not introduce code or data that pollutes production or disrupts test/development workflows.

## Scope & Minimalism
- **Focus on requested changes**: Only modify or add code for issues/features you understand well. Avoid "drive-by" changes that are unrelated to the task at hand.
- **Avoid introducing new patterns/technologies** unless you've first attempted to refine or extend existing approaches. If a new approach is adopted, remove any legacy logic so the code doesn't contain duplicates.

## Keeping Code Manageable
- **Limit file size**: If a file approaches 300 lines, consider refactoring or splitting into smaller modules.
- **Single-use scripts**: If a script is truly one-off, keep it separate or ephemeral—don't embed large, rarely-used chunks of logic in core code.
- **Mock/stub data**: Only mock data when running automated tests. Don't introduce fakes into dev or production environments.

## Maintaining Clean Configuration
- **Never overwrite `.env`**: Don't automatically overwrite an existing `.env` file without explicit confirmation.
- **Protect existing config**: When adding or updating environment variables, confirm with the team (or the repository owner) to avoid inadvertently breaking dev or production environments.
- **Security**: Never upload `.env` files to GitHub to ensure security.

## Optimize Render deployment 
- Create lighter weight scrapers
- Reduce dependencies in api/requirements.txt
- Update render.yaml with optimized  configuration
- Document deployment process and optimizations