#!/bin/bash
# Start GolfStats app with Supabase connection

# Replace these with your actual values
SUPABASE_URL="https://qfuvwfghevxhnkfrwmwk.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFmdXZ3ZmdoZXZ4aG5rZnJ3bXdrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA5NzU2MDYsImV4cCI6MjA1NjU1MTYwNn0.yzPWndB4fcSxOHy1kQ6NoSknWshhEj5Wk-USuK_6S9Y"
SUPABASE_PASSWORD="pqzA23aCUlUr" # Replace with your actual Supabase database password

# Set environment variables
export SUPABASE_URL="$SUPABASE_URL"
export SUPABASE_API_KEY="$SUPABASE_KEY"
export DB_TYPE="supabase"

# Direct connection (default)
export SUPABASE_DB_URL="postgresql://postgres:${SUPABASE_PASSWORD}@db.qfuvwfghevxhnkfrwmwk.supabase.co:5432/postgres"

# Transaction pooler (optional)
# export SUPABASE_POOLER_URL="postgresql://postgres.qfuvwfghevxhnkfrwmwk:${SUPABASE_PASSWORD}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
# export SUPABASE_USE_POOLER="true"

# Add connection debugging
export SQLALCHEMY_ECHO="true"  # Set to "false" to turn off SQL debugging

# Run the app
echo "Starting GolfStats with Supabase connection"
python run.py "$@"