#!/bin/bash
# Start GolfStats app with Supabase connection

# Set environment to test mode by default
export APP_ENVIRONMENT="test"

# Check if a specific environment was requested
if [ "$1" = "--production" ]; then
    export APP_ENVIRONMENT="production"
    shift
fi

# Set database type
export DB_TYPE="supabase"

# Load environment variables from the appropriate .env file
if [ "$APP_ENVIRONMENT" = "production" ]; then
    ENV_FILE=".env.production"
else
    ENV_FILE=".env.test"
fi

# Check if the environment file exists
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment from $ENV_FILE"
    set -a
    source "$ENV_FILE"
    set +a
else
    echo "Warning: $ENV_FILE not found. Using environment variables only."
fi

# Print debug info
echo "--------------------------------"
echo "Supabase Connection Debug Info:"
echo "--------------------------------"
echo "Environment: $APP_ENVIRONMENT"
echo "Supabase URL: $SUPABASE_URL"
echo "Supabase API Key available: $(if [ ! -z "$SUPABASE_API_KEY" ]; then echo "Yes"; else echo "No"; fi)"
echo "Supabase Password available: $(if [ ! -z "$SUPABASE_PASSWORD" ]; then echo "Yes"; else echo "No"; fi)"
echo "Database Type: $DB_TYPE"
echo "--------------------------------"

# Run the app
echo "Starting GolfStats with Supabase connection"
python run.py "${@}"