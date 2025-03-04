# GolfStats

## Project Overview
GolfStats is a comprehensive golf statistics tracking application that integrates with popular golf tracking systems including Trackman, Arccos, and SkyTrak. The backend handles data collection, processing, and storage using Flask and Supabase, while the frontend provides a user interface for data visualization.

## Features

- Import golf round data from Arccos, Trackman, and SkyTrak
- Track rounds, shots, and clubs
- Calculate statistics and trends
- Secure authentication with Supabase
- Data isolation with Row Level Security (RLS)

## Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Configure the application in `config/config.py`.
4. Run the backend: `python backend/app.py`
5. Run with ETL scheduler: `python run.py --scheduler`
6. Run one-time ETL process: `python run.py --etl`
7. Open `frontend/index.html` in your browser.

## Deployment

### Vercel Deployment

This project is configured for deployment on Vercel with the following features:

- Serverless API functions
- Automatic builds on GitHub push
- Environment variable management through Vercel dashboard

To deploy on Vercel:

1. Push to GitHub
2. Connect repository to Vercel
3. Set the following environment variables in Vercel dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_API_KEY`
   - `APP_SECRET_KEY`
   - Other scraper-specific credentials
4. Deploy!

## GitHub Actions
This project uses GitHub Actions to automate the daily ETL process:

- **Daily ETL**: Automatically runs at 3 AM UTC every day to scrape and import new golf data
- **Manual Trigger**: Can be manually triggered via GitHub Actions UI when needed
- **Artifact Storage**: ETL logs are stored as artifacts for 7 days for monitoring and debugging

## Supabase Row Level Security (RLS)

This application uses Supabase Row Level Security to ensure that users can only access their own data. RLS policies are automatically applied when the application starts.

### Protected Tables

The following tables are protected with RLS policies:

- `users` - User profiles and credentials
- `golf_rounds` - Golf rounds data
- `golf_holes` - Holes within a round
- `golf_shots` - Shots within a hole
- `round_stats` - Statistics for a round
- `clubs` - User's golf clubs
- `user_preferences` - User preferences and settings

### Security Policies

RLS policies ensure that:
- Users can only view/edit their own data
- Data from other users is completely invisible
- Backend service role can access all data for administrative purposes

### How It Works

1. **Authentication**: When users log in, they receive a JWT token from Supabase Auth
2. **User Context**: Each database query includes the user's ID through the `auth.uid()` function
3. **Policy Enforcement**: Database tables check if the user ID on records matches the requesting user
4. **Relationship Protection**: Related tables use JOINs to verify ownership (e.g., only see shots for your own rounds)
5. **Administrative Access**: Service role tokens bypass RLS for backend operations

### Manual RLS Updates

Administrators can manually apply or update RLS policies via:
1. Admin API endpoint: `/api/admin/apply-rls` (requires admin privileges)
2. Running migrations directly: `python backend/database/migrations.py`

## Architecture
- **Backend**: Flask API with SQLAlchemy ORM and Supabase integration
- **Authentication**: Supabase Auth
- **Database**: Supabase PostgreSQL
- **Web scrapers**: Selenium-based for various golf platforms
- **ETL**: Automated data extraction, transformation, and loading
- **Config**: Contains configuration settings for the application
- **Docs**: Project documentation and overview
- **Tests**: Unit and integration tests for the application