-- Function to get a user ID by their email address
-- This function needs to be executed in Supabase SQL editor
-- with appropriate permissions

CREATE OR REPLACE FUNCTION get_user_id_by_email(email_address text)
RETURNS uuid
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT id 
  FROM auth.users 
  WHERE email = email_address
$$;