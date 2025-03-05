#!/bin/bash
# Start GolfStats app with Supabase connection

# Replace these with your actual values
SUPABASE_URL="https://qfuvwfghevxhnkfrwmwk.supabase.co"
SUPABASE_KEY="YOUR_SUPABASE_ANON_KEY"
SUPABASE_PASSWORD="YOUR_PASSWORD"

# Set environment variables
export SUPABASE_URL="$SUPABASE_URL"
export SUPABASE_API_KEY="$SUPABASE_KEY"
export DB_TYPE="supabase"

# Direct connection (default)
export SUPABASE_DB_URL="postgresql://postgres:$SUPABASE_PASSWORD@db.qfuvwfghevxhnkfrwmwk.supabase.co:5432/postgres"

# Transaction pooler (optional)
# export SUPABASE_POOLER_URL="postgresql://postgres.qfuvwfghevxhnkfrwmwk:$SUPABASE_PASSWORD@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
# export SUPABASE_USE_POOLER="true"

# Add connection debugging
export SQLALCHEMY_ECHO="true"  # Set to "false" to turn off SQL debugging

# Run the app
echo "Starting GolfStats with Supabase connection"
python run.py "$@"