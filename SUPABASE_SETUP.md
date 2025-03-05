# Supabase Setup Guide for GolfStats

To properly set up your GolfStats application with Supabase, follow these steps:

## 1. Create Tables in Supabase

1. Go to the Supabase dashboard at [https://supabase.com](https://supabase.com) and sign in
2. Select your GolfStats project
3. Navigate to the "SQL Editor" section
4. Create a new query
5. Copy and paste the entire contents of the file `backend/database/sql/create_tables.sql` into the SQL editor
6. Run the query to create all required tables and set up Row Level Security (RLS) policies

## 2. Set Up User Preferences for Your User

1. In the Supabase dashboard, go to "Authentication" → "Users"
2. Find your user account (email: nealfrenchfry@gmail.com)
3. Copy your UUID (user ID)
4. Go to "Table Editor" → "user_preferences"
5. Click "Insert row" and fill in the following:
   - `user_id`: Paste your UUID from step 3
   - `preferred_units`: "yards"
   - Leave other fields as NULL or set them as desired
6. Click "Save"

## 3. Test the Application

1. Run the application with:
   ```
   python run.py
   ```
2. Open a web browser and navigate to http://localhost:8000
3. Sign in with your Google account
4. Verify that you can access your profile and settings

## Troubleshooting

If you encounter issues:

1. **Tables not found**: Make sure you ran the SQL script successfully in Supabase
2. **Authentication errors**: Verify that Google OAuth is properly configured in Supabase
3. **Permission errors**: Check that Row Level Security (RLS) policies are correctly set up
4. **User profile issues**: Ensure your user_preferences record is correctly linked to your auth user

## Additional Resources

- The complete SQL for creating tables is in `backend/database/sql/create_tables.sql`
- Database-related code is in the `backend/database` directory
- For more details on the database schema, see `backend/models`