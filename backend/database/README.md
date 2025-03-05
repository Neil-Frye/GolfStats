# GolfStats Database Setup

This directory contains scripts and utilities for setting up and managing the GolfStats database in Supabase.

## Setting Up Supabase Tables

To set up the database tables in Supabase, follow these steps:

1. Log in to your Supabase dashboard at https://supabase.com
2. Navigate to your GolfStats project
3. Go to the SQL Editor
4. Create a new query
5. Copy the contents of `sql/create_tables.sql` into the query editor
6. Run the SQL commands to create all tables and configure Row Level Security

## Setting Up User Preferences

After creating the tables, you need to set up a user preferences record for your user:

1. Log in to your Supabase dashboard
2. Go to the Authentication -> Users page
3. Find your user and copy the UUID
4. Go to the Table Editor -> user_preferences table
5. Click "Insert row" and create a new record:
   - Set `user_id` to your UUID
   - Set `preferred_units` to "yards" 
   - Leave other fields null or set as desired
6. Click "Save"

## Automated Setup

If you have the Supabase CLI installed, you can use it to set up the database:

```
supabase db reset
```

Or you can try using our Python script, but it requires full access rights:

```
python run.py --setup-db
```

Note that the automated setup may not work with limited permissions.

## RLS Policies

All tables are protected with Row Level Security (RLS) policies to ensure that users can only access their own data. The policies are configured in the `create_tables.sql` script.

## Troubleshooting

If you encounter any issues:

1. Check that your Supabase URL and API key are correctly set in `.env`
2. Verify that you have the necessary permissions to create tables
3. If using the REST API, ensure you have enabled the necessary APIs
4. For authentication issues, verify that Row Level Security (RLS) is correctly configured