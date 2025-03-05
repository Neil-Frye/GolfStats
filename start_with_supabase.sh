#!/bin/bash
# Start GolfStats app with Supabase connection

# ========================================================
# IMPORTANT: Replace these values with your actual credentials
# ========================================================
SUPABASE_URL="https://qfuvwfghevxhnkfrwmwk.supabase.co"
SUPABASE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFmdXZ3ZmdoZXZ4aG5rZnJ3bXdrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA5NzU2MDYsImV4cCI6MjA1NjU1MTYwNn0.yzPWndB4fcSxOHy1kQ6NoSknWshhEj5Wk-USuK_6S9Y"
SUPABASE_PASSWORD="pqzA23aCUlUr" # REQUIRED: Your Supabase database password

# ========================================================
# For Supabase direct connections, you must use your database password, not the API key
# If you don't know your database password, you can reset it in the Supabase dashboard:
# Database → Settings → Database Password → Reset database password
# ========================================================

# Set basic environment variables
export SUPABASE_URL="$SUPABASE_URL"
export SUPABASE_API_KEY="$SUPABASE_KEY"
export SUPABASE_PASSWORD="$SUPABASE_PASSWORD"
export DB_TYPE="supabase"

# IMPORTANT: Set these variables directly using the database password
# This ensures they are available as environment variables when the app runs
export SUPABASE_DB_URL="postgresql://postgres:${SUPABASE_PASSWORD}@db.qfuvwfghevxhnkfrwmwk.supabase.co:5432/postgres"

# Transaction pooler (alternative connection method - uncomment if needed)
export SUPABASE_POOLER_URL="postgresql://postgres.qfuvwfghevxhnkfrwmwk:${SUPABASE_PASSWORD}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
# export SUPABASE_USE_POOLER="true"  # Uncomment to use the connection pooler

# Add connection debugging
export SQLALCHEMY_ECHO="true"  # Set to "false" to turn off SQL debugging

# Print debug info
echo "--------------------------------"
echo "Supabase Connection Debug Info:"
echo "--------------------------------"
echo "Supabase URL: $SUPABASE_URL"
echo "Supabase API Key available: $(if [ ! -z "$SUPABASE_API_KEY" ]; then echo "Yes"; else echo "No"; fi)"
echo "Supabase Password available: $(if [ ! -z "$SUPABASE_PASSWORD" ]; then echo "Yes"; else echo "No"; fi)"
echo "Database Type: $DB_TYPE"
echo "Connection URL: postgresql://postgres:***@db.qfuvwfghevxhnkfrwmwk.supabase.co:5432/postgres"
echo "--------------------------------"

# Run the app
echo "Starting GolfStats with Supabase connection"
python run.py "$@"