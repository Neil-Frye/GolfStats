-- Additional golf_shots columns update
-- This SQL adds missing columns to the golf_shots table that are in the DB_FIELDS set

-- Add missing columns
ALTER TABLE IF EXISTS public.golf_shots 
  ADD COLUMN IF NOT EXISTS height_feet REAL,
  ADD COLUMN IF NOT EXISTS launch_direction_degrees REAL,
  ADD COLUMN IF NOT EXISTS from_pin_yards REAL,
  ADD COLUMN IF NOT EXISTS carry_side_feet REAL,
  ADD COLUMN IF NOT EXISTS club_path_degrees REAL,
  ADD COLUMN IF NOT EXISTS face_angle_degrees REAL,
  ADD COLUMN IF NOT EXISTS attack_angle_degrees REAL,
  ADD COLUMN IF NOT EXISTS carry_efficiency REAL,
  ADD COLUMN IF NOT EXISTS height_to_carry_ratio REAL,
  ADD COLUMN IF NOT EXISTS spin_to_launch_ratio REAL,
  ADD COLUMN IF NOT EXISTS shot_date TIMESTAMP WITH TIME ZONE,
  ADD COLUMN IF NOT EXISTS notes TEXT;

-- Log the update
RAISE NOTICE 'Added missing columns to golf_shots table';