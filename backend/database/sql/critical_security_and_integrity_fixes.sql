-- Critical Security and Database Integrity Fixes for GolfStats
-- Execute these updates immediately to address security vulnerabilities and data integrity issues

-- ==================================================
-- PHASE 1: CRITICAL SECURITY FIXES
-- ==================================================

-- 1. Create secure API credentials table to replace plaintext passwords
CREATE TABLE IF NOT EXISTS public.api_credentials (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  service_name character varying NOT NULL CHECK (service_name IN ('trackman', 'arccos', 'skytrak')),
  encrypted_credentials text NOT NULL, -- Encrypted JSON containing username/password
  encryption_key_id character varying NOT NULL, -- Reference to Supabase Vault key
  last_sync_at timestamp with time zone,
  is_active boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT unique_user_service UNIQUE(user_id, service_name)
);

-- Enable RLS on api_credentials
ALTER TABLE public.api_credentials ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own credentials" ON public.api_credentials
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own credentials" ON public.api_credentials
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own credentials" ON public.api_credentials
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own credentials" ON public.api_credentials
  FOR DELETE USING (auth.uid() = user_id);

-- 2. Remove plaintext password columns from user_preferences
ALTER TABLE public.user_preferences 
  DROP COLUMN IF EXISTS trackman_password,
  DROP COLUMN IF EXISTS arccos_password,
  DROP COLUMN IF EXISTS skytrak_password;

-- Add migration status columns to track credential migration
ALTER TABLE public.user_preferences
  ADD COLUMN IF NOT EXISTS credentials_migrated boolean DEFAULT false,
  ADD COLUMN IF NOT EXISTS migration_date timestamp with time zone;

-- ==================================================
-- PHASE 2: DATABASE INTEGRITY FIXES
-- ==================================================

-- 3. Fix golf_shots foreign key constraints
-- Add user_id column if missing (for standalone shots)
ALTER TABLE public.golf_shots 
  ADD COLUMN IF NOT EXISTS user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE;

-- Update existing records to set user_id from related tables
UPDATE public.golf_shots gs
SET user_id = COALESCE(
  (SELECT gr.user_id FROM golf_rounds gr 
   JOIN golf_holes gh ON gh.round_id = gr.id 
   WHERE gh.id = gs.hole_id),
  (SELECT rs.user_id FROM range_sessions rs WHERE rs.id = gs.session_id)
)
WHERE gs.user_id IS NULL;

-- Add constraint to ensure user_id is always set
ALTER TABLE public.golf_shots
  ADD CONSTRAINT check_user_id_not_null CHECK (user_id IS NOT NULL);

-- 4. Add unique constraints to prevent duplicate imports
-- Create composite unique index for golf_shots to prevent duplicates
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_shot_import 
ON public.golf_shots(
  user_id,
  shot_date,
  club,
  total_distance_yards,
  ball_speed_mph,
  source_system
) WHERE shot_date IS NOT NULL;

-- Add import tracking columns
ALTER TABLE public.golf_shots
  ADD COLUMN IF NOT EXISTS external_id character varying, -- ID from source system
  ADD COLUMN IF NOT EXISTS import_batch_id bigint,
  ADD COLUMN IF NOT EXISTS imported_at timestamp with time zone DEFAULT now();

-- Create unique index on external_id per source system
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_external_shot 
ON public.golf_shots(user_id, source_system, external_id) 
WHERE external_id IS NOT NULL;

-- ==================================================
-- PHASE 3: IMPORT TRACKING AND DATA QUALITY
-- ==================================================

-- 5. Data Import Tracking Table
CREATE TABLE IF NOT EXISTS public.import_logs (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  source_system character varying NOT NULL CHECK (source_system IN ('trackman', 'skytrak', 'arccos', 'csv', 'manual')),
  import_type character varying NOT NULL CHECK (import_type IN ('full', 'incremental', 'manual')),
  status character varying NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  records_processed integer DEFAULT 0,
  records_imported integer DEFAULT 0,
  records_skipped integer DEFAULT 0,
  records_failed integer DEFAULT 0,
  error_message text,
  import_metadata jsonb, -- Store API response metadata, file info, etc.
  started_at timestamp with time zone DEFAULT now(),
  completed_at timestamp with time zone,
  created_at timestamp with time zone DEFAULT now()
);

-- Enable RLS on import_logs
ALTER TABLE public.import_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own import logs" ON public.import_logs
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own import logs" ON public.import_logs
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 6. Import Staging Table for validation
CREATE TABLE IF NOT EXISTS public.import_staging (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  import_log_id bigint REFERENCES public.import_logs(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  source_system character varying NOT NULL,
  external_id character varying,
  raw_data jsonb NOT NULL,
  validation_status character varying CHECK (validation_status IN ('pending', 'valid', 'invalid')),
  validation_errors jsonb,
  processed boolean DEFAULT false,
  created_at timestamp with time zone DEFAULT now()
);

-- Index for efficient staging processing
CREATE INDEX IF NOT EXISTS idx_staging_processing 
ON public.import_staging(import_log_id, processed, validation_status);

-- ==================================================
-- PHASE 4: PERFORMANCE OPTIMIZATION
-- ==================================================

-- 7. Add missing indexes for common queries
CREATE INDEX IF NOT EXISTS idx_shots_user_date 
ON public.golf_shots(user_id, shot_date DESC) 
WHERE shot_date IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_shots_user_club 
ON public.golf_shots(user_id, club);

CREATE INDEX IF NOT EXISTS idx_shots_user_type 
ON public.golf_shots(user_id, shot_type);

CREATE INDEX IF NOT EXISTS idx_rounds_user_date 
ON public.golf_rounds(user_id, date DESC);

CREATE INDEX IF NOT EXISTS idx_sessions_user_date 
ON public.range_sessions(user_id, session_date DESC);

CREATE INDEX IF NOT EXISTS idx_import_logs_user_status 
ON public.import_logs(user_id, status, created_at DESC);

-- 8. Create materialized view for user statistics
CREATE MATERIALIZED VIEW IF NOT EXISTS public.user_club_statistics AS
SELECT 
  gs.user_id,
  gs.club,
  gs.shot_type,
  COUNT(*) as total_shots,
  AVG(gs.total_distance_yards) as avg_distance,
  STDDEV(gs.total_distance_yards) as distance_consistency,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY gs.total_distance_yards) as median_distance,
  AVG(gs.carry_distance_yards) as avg_carry,
  AVG(gs.side_deviation_yards) as avg_offline,
  AVG(ABS(gs.side_deviation_yards)) as avg_offline_absolute,
  AVG(gs.spin_rate_rpm) as avg_spin,
  AVG(gs.launch_angle_degrees) as avg_launch,
  AVG(gs.ball_speed_mph) as avg_ball_speed,
  MAX(gs.total_distance_yards) as max_distance,
  MIN(gs.total_distance_yards) FILTER (WHERE gs.total_distance_yards > 0) as min_distance,
  MAX(gs.shot_date) as last_shot_date,
  MIN(gs.shot_date) as first_shot_date
FROM public.golf_shots gs
WHERE gs.club IS NOT NULL 
  AND gs.total_distance_yards > 0
  AND gs.total_distance_yards < 500 -- Remove outliers
GROUP BY gs.user_id, gs.club, gs.shot_type;

-- Create index on materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_user_club_stats 
ON public.user_club_statistics(user_id, club, shot_type);

-- ==================================================
-- PHASE 5: ENHANCED TRACKING TABLES
-- ==================================================

-- 9. Shot Patterns & Tendencies
CREATE TABLE IF NOT EXISTS public.shot_patterns (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  club character varying NOT NULL,
  shot_shape character varying CHECK (shot_shape IN ('draw', 'fade', 'straight', 'pull', 'push', 'hook', 'slice')),
  typical_miss character varying CHECK (typical_miss IN ('left', 'right', 'short', 'long')),
  avg_dispersion_yards real,
  consistency_score real CHECK (consistency_score >= 0 AND consistency_score <= 100),
  sample_size integer,
  calculation_date timestamp with time zone DEFAULT now(),
  last_updated timestamp with time zone DEFAULT now(),
  CONSTRAINT unique_user_club_pattern UNIQUE(user_id, club)
);

-- Enable RLS
ALTER TABLE public.shot_patterns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own patterns" ON public.shot_patterns
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own patterns" ON public.shot_patterns
  FOR ALL USING (auth.uid() = user_id);

-- 10. Data Quality Metrics
CREATE TABLE IF NOT EXISTS public.data_quality_scores (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  source_system character varying NOT NULL,
  metric_date date NOT NULL,
  completeness_score real CHECK (completeness_score >= 0 AND completeness_score <= 100),
  accuracy_score real CHECK (accuracy_score >= 0 AND accuracy_score <= 100),
  consistency_score real CHECK (consistency_score >= 0 AND consistency_score <= 100),
  total_records integer,
  valid_records integer,
  missing_fields jsonb, -- Track which fields are commonly missing
  outlier_count integer,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT unique_quality_metric UNIQUE(user_id, source_system, metric_date)
);

-- ==================================================
-- PHASE 6: ADDITIONAL ENHANCEMENTS
-- ==================================================

-- 11. Add check constraints for data validation
ALTER TABLE public.golf_shots
  ADD CONSTRAINT check_reasonable_distance 
    CHECK (total_distance_yards >= 0 AND total_distance_yards <= 500),
  ADD CONSTRAINT check_reasonable_ball_speed 
    CHECK (ball_speed_mph >= 0 AND ball_speed_mph <= 250),
  ADD CONSTRAINT check_reasonable_spin 
    CHECK (spin_rate_rpm >= 0 AND spin_rate_rpm <= 15000),
  ADD CONSTRAINT check_reasonable_launch 
    CHECK (launch_angle_degrees >= -10 AND launch_angle_degrees <= 60);

-- 12. Add columns for enhanced tracking
ALTER TABLE public.golf_shots 
  ADD COLUMN IF NOT EXISTS shot_result character varying CHECK (shot_result IN ('great', 'good', 'average', 'poor', 'penalty')),
  ADD COLUMN IF NOT EXISTS lie_type character varying CHECK (lie_type IN ('tee', 'fairway', 'rough', 'sand', 'other')),
  ADD COLUMN IF NOT EXISTS shot_intent character varying,
  ADD COLUMN IF NOT EXISTS temperature_f real CHECK (temperature_f >= -50 AND temperature_f <= 150),
  ADD COLUMN IF NOT EXISTS elevation_change_feet real,
  ADD COLUMN IF NOT EXISTS data_quality_score real CHECK (data_quality_score >= 0 AND data_quality_score <= 100);

-- 13. Create view for recent activity
CREATE OR REPLACE VIEW public.recent_user_activity AS
SELECT 
  u.id as user_id,
  u.email,
  COUNT(DISTINCT gr.id) FILTER (WHERE gr.date >= CURRENT_DATE - INTERVAL '30 days') as rounds_last_30_days,
  COUNT(DISTINCT rs.id) FILTER (WHERE rs.session_date >= CURRENT_DATE - INTERVAL '30 days') as sessions_last_30_days,
  COUNT(gs.id) FILTER (WHERE gs.shot_date >= CURRENT_DATE - INTERVAL '30 days') as shots_last_30_days,
  MAX(GREATEST(gr.date, rs.session_date, gs.shot_date::date)) as last_activity_date,
  COUNT(DISTINCT il.id) FILTER (WHERE il.created_at >= CURRENT_DATE - INTERVAL '7 days') as imports_last_7_days
FROM auth.users u
LEFT JOIN public.golf_rounds gr ON gr.user_id = u.id
LEFT JOIN public.range_sessions rs ON rs.user_id = u.id
LEFT JOIN public.golf_shots gs ON gs.user_id = u.id
LEFT JOIN public.import_logs il ON il.user_id = u.id
GROUP BY u.id, u.email;

-- ==================================================
-- PHASE 7: MIGRATION HELPERS
-- ==================================================

-- 14. Function to refresh materialized views
CREATE OR REPLACE FUNCTION public.refresh_user_statistics()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY public.user_club_statistics;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 15. Function to validate shot data
CREATE OR REPLACE FUNCTION public.validate_shot_data(shot_data jsonb)
RETURNS jsonb AS $$
DECLARE
  errors jsonb := '[]'::jsonb;
BEGIN
  -- Check required fields
  IF shot_data->>'club' IS NULL THEN
    errors := errors || '["Missing required field: club"]'::jsonb;
  END IF;
  
  -- Check distance reasonableness
  IF (shot_data->>'total_distance_yards')::real > 500 OR 
     (shot_data->>'total_distance_yards')::real < 0 THEN
    errors := errors || '["Unreasonable distance value"]'::jsonb;
  END IF;
  
  -- Check ball speed reasonableness
  IF (shot_data->>'ball_speed_mph')::real > 250 OR 
     (shot_data->>'ball_speed_mph')::real < 0 THEN
    errors := errors || '["Unreasonable ball speed value"]'::jsonb;
  END IF;
  
  RETURN jsonb_build_object(
    'is_valid', jsonb_array_length(errors) = 0,
    'errors', errors
  );
END;
$$ LANGUAGE plpgsql;

-- ==================================================
-- COMPLETION MESSAGE
-- ==================================================

-- Log completion
DO $$
BEGIN
  RAISE NOTICE 'Critical security and integrity fixes completed successfully';
  RAISE NOTICE 'Next steps:';
  RAISE NOTICE '1. Implement encryption for api_credentials using Supabase Vault';
  RAISE NOTICE '2. Migrate existing user credentials to encrypted storage';
  RAISE NOTICE '3. Update application code to use new api_credentials table';
  RAISE NOTICE '4. Test import deduplication with unique constraints';
  RAISE NOTICE '5. Schedule regular refresh of materialized views';
END $$;