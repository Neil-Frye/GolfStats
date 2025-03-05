# Supabase Database Integration Guide

This guide explains how to set up and use the Supabase PostgreSQL database with GolfStats.

## Connection Options

GolfStats supports two ways to connect to your Supabase PostgreSQL database:

1. **Direct Connection** (default): Connects directly to your Supabase PostgreSQL instance
   - For read/write operations
   - Good for development and low-volume applications
   - URL format: `postgresql://postgres:[PASSWORD]@db.qfuvwfghevxhnkfrwmwk.supabase.co:5432/postgres`

2. **Connection Pooler** (optional): Uses the Supabase connection pooler
   - Better for production applications with many concurrent users
   - URL format: `postgresql://postgres.qfuvwfghevxhnkfrwmwk:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres`

## Setup Instructions

### 1. Configure Your Environment Variables

Edit the `start_with_supabase.sh` script with your Supabase credentials:

```
SUPABASE_URL="https://qfuvwfghevxhnkfrwmwk.supabase.co"
SUPABASE_KEY="YOUR_SUPABASE_ANON_KEY"
SUPABASE_PASSWORD="YOUR_PASSWORD"
```

### 2. Set Up the Required Tables

1. Log into your Supabase dashboard
2. Go to SQL Editor
3. Copy the SQL from `backend/database/sql/create_tables.sql`
4. Run the script to create all tables

### 3. Create User Profile for Your Account

After setting up tables, you need to create a user profile record for your Supabase user:

1. Find your user ID in the Supabase dashboard (Authentication > Users)
2. Run this SQL in the Supabase SQL Editor (replace with your actual user ID):

```sql
INSERT INTO public.user_preferences (user_id, preferred_units)
VALUES ('your-user-id-from-supabase', 'yards');
```

### 4. Run the Application

Start the application with Supabase database integration:

```
./start_with_supabase.sh
```

Or with specific flags:

```
./start_with_supabase.sh --scheduler
```

## Troubleshooting

### Connection Issues

If you encounter connection problems:

1. Verify your password in the `start_with_supabase.sh` script
2. Make sure you've added your current IP address to Supabase's allowlist
3. Check Supabase dashboard for service status
4. Try switching between direct connection and connection pooler

### Missing Tables

If the application reports missing tables:

1. Run the SQL script again from `backend/database/sql/create_tables.sql`
2. Verify that tables were created in the Supabase Table Editor
3. Check for SQL errors in the Supabase SQL Editor output

## Database Management

To manage your database:

- Access the Supabase dashboard to view and modify tables
- Use the Table Editor for easy data editing
- Use SQL Editor for more complex operations
- Check the Authentication section to manage users
