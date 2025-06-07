-- GolfStats Database Migration Guide
-- This file provides step-by-step instructions for applying the database updates

-- ==================================================
-- MIGRATION OVERVIEW
-- ==================================================
-- This migration includes:
-- 1. Critical security fixes (removing plaintext passwords)
-- 2. Data integrity improvements (foreign keys, unique constraints)
-- 3. Performance optimizations (indexes, materialized views)
-- 4. Analytics enhancements (new tables for tracking and analysis)

-- ==================================================
-- PRE-MIGRATION CHECKLIST
-- ==================================================
-- [ ] Backup the database
-- [ ] Notify users of potential downtime
-- [ ] Review all SQL files for environment-specific changes
-- [ ] Ensure Supabase Vault is configured for encryption

-- ==================================================
-- MIGRATION STEPS
-- ==================================================

-- STEP 1: Apply critical security and integrity fixes
-- This MUST be done first as it fixes security vulnerabilities
-- Run: critical_security_and_integrity_fixes.sql

-- STEP 2: Apply comprehensive analytics enhancements
-- This adds new features and tables
-- Run: comprehensive_analytics_enhancements.sql

-- STEP 3: Migrate existing user credentials (if any exist)
-- This script helps migrate existing plaintext passwords to encrypted storage

-- Check if any users have credentials that need migration
DO $$
DECLARE
  users_with_credentials INTEGER;
BEGIN
  SELECT COUNT(DISTINCT user_id) INTO users_with_credentials
  FROM public.user_preferences
  WHERE (trackman_username IS NOT NULL AND trackman_username != '')
     OR (arccos_username IS NOT NULL AND arccos_username != '')
     OR (skytrak_username IS NOT NULL AND skytrak_username != '');
  
  IF users_with_credentials > 0 THEN
    RAISE NOTICE 'Found % users with credentials that need migration', users_with_credentials;
    RAISE NOTICE 'Manual migration required - credentials must be encrypted before storage';
  ELSE
    RAISE NOTICE 'No existing credentials found - migration not needed';
  END IF;
END $$;

-- STEP 4: Verify all constraints are in place
DO $$
BEGIN
  -- Check critical constraints
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint 
    WHERE conname = 'check_user_id_not_null' 
    AND conrelid = 'public.golf_shots'::regclass
  ) THEN
    RAISE WARNING 'Missing user_id constraint on golf_shots table';
  END IF;
  
  -- Check unique indexes
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes 
    WHERE indexname = 'idx_unique_shot_import'
  ) THEN
    RAISE WARNING 'Missing unique import index on golf_shots table';
  END IF;
  
  RAISE NOTICE 'Constraint verification complete';
END $$;

-- STEP 5: Refresh materialized views
-- This should be done after data is migrated
DO $$
BEGIN
  -- Check if materialized view exists before refreshing
  IF EXISTS (
    SELECT 1 FROM pg_matviews 
    WHERE matviewname = 'user_club_statistics'
  ) THEN
    REFRESH MATERIALIZED VIEW CONCURRENTLY public.user_club_statistics;
    RAISE NOTICE 'Materialized view refreshed successfully';
  END IF;
END $$;

-- STEP 6: Update existing shot patterns
-- Calculate initial shot patterns for users with sufficient data
INSERT INTO public.shot_patterns (user_id, club, shot_shape, typical_miss, avg_dispersion_yards, consistency_score, sample_size)
SELECT DISTINCT
  gs.user_id,
  gs.club,
  CASE 
    WHEN AVG(gs.side_deviation_yards) < -5 THEN 'pull'
    WHEN AVG(gs.side_deviation_yards) > 5 THEN 'push'
    ELSE 'straight'
  END as shot_shape,
  CASE 
    WHEN AVG(gs.side_deviation_yards) < 0 THEN 'left'
    WHEN AVG(gs.side_deviation_yards) > 0 THEN 'right'
    ELSE 'center'
  END as typical_miss,
  AVG(ABS(gs.side_deviation_yards)) as avg_dispersion_yards,
  CASE 
    WHEN STDDEV(gs.side_deviation_yards) < 10 THEN 90
    WHEN STDDEV(gs.side_deviation_yards) < 15 THEN 70
    WHEN STDDEV(gs.side_deviation_yards) < 20 THEN 50
    ELSE 30
  END as consistency_score,
  COUNT(*) as sample_size
FROM public.golf_shots gs
WHERE gs.side_deviation_yards IS NOT NULL
  AND gs.shot_date >= CURRENT_DATE - INTERVAL '180 days'
GROUP BY gs.user_id, gs.club
HAVING COUNT(*) >= 20
ON CONFLICT (user_id, club) DO UPDATE
SET 
  shot_shape = EXCLUDED.shot_shape,
  typical_miss = EXCLUDED.typical_miss,
  avg_dispersion_yards = EXCLUDED.avg_dispersion_yards,
  consistency_score = EXCLUDED.consistency_score,
  sample_size = EXCLUDED.sample_size,
  last_updated = now();

-- ==================================================
-- POST-MIGRATION VERIFICATION
-- ==================================================

-- Verify critical security fixes
DO $$
DECLARE
  password_columns_exist BOOLEAN;
BEGIN
  SELECT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_schema = 'public' 
    AND table_name = 'user_preferences'
    AND column_name IN ('trackman_password', 'arccos_password', 'skytrak_password')
  ) INTO password_columns_exist;
  
  IF password_columns_exist THEN
    RAISE WARNING 'Password columns still exist in user_preferences table!';
  ELSE
    RAISE NOTICE 'Security fix verified: Password columns removed';
  END IF;
END $$;

-- Verify new tables exist
DO $$
DECLARE
  expected_tables TEXT[] := ARRAY[
    'api_credentials',
    'import_logs',
    'import_staging',
    'shot_patterns',
    'data_quality_scores',
    'practice_goals',
    'courses',
    'course_tees',
    'course_hole_details',
    'course_hole_tees',
    'weather_conditions',
    'equipment_changes',
    'performance_benchmarks',
    'practice_drills',
    'practice_drill_sessions',
    'handicap_history',
    'shot_dispersion_data'
  ];
  missing_tables TEXT[];
BEGIN
  SELECT ARRAY_AGG(table_name) INTO missing_tables
  FROM UNNEST(expected_tables) AS table_name
  WHERE NOT EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = table_name
  );
  
  IF missing_tables IS NOT NULL THEN
    RAISE WARNING 'Missing tables: %', missing_tables;
  ELSE
    RAISE NOTICE 'All expected tables created successfully';
  END IF;
END $$;

-- ==================================================
-- ROLLBACK SCRIPTS (if needed)
-- ==================================================

-- To rollback security changes (NOT RECOMMENDED):
-- ALTER TABLE public.user_preferences 
--   ADD COLUMN trackman_password varchar(255),
--   ADD COLUMN arccos_password varchar(255),
--   ADD COLUMN skytrak_password varchar(255);
-- DROP TABLE IF EXISTS public.api_credentials CASCADE;

-- To rollback new tables:
-- DROP TABLE IF EXISTS public.shot_dispersion_data CASCADE;
-- DROP TABLE IF EXISTS public.handicap_history CASCADE;
-- DROP TABLE IF EXISTS public.practice_drill_sessions CASCADE;
-- DROP TABLE IF EXISTS public.practice_drills CASCADE;
-- ... (continue for all new tables)

-- ==================================================
-- MAINTENANCE TASKS
-- ==================================================

-- Schedule these tasks to run regularly:

-- 1. Refresh materialized views (daily)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY public.user_club_statistics;

-- 2. Update shot patterns (weekly)
-- CALL update_all_shot_patterns();

-- 3. Clean up old import staging data (monthly)
-- DELETE FROM public.import_staging 
-- WHERE created_at < CURRENT_DATE - INTERVAL '30 days' 
-- AND processed = true;

-- 4. Archive old import logs (quarterly)
-- DELETE FROM public.import_logs 
-- WHERE created_at < CURRENT_DATE - INTERVAL '365 days';

-- ==================================================
-- COMPLETION
-- ==================================================

DO $$
BEGIN
  RAISE NOTICE '========================================';
  RAISE NOTICE 'Migration guide completed';
  RAISE NOTICE 'Next steps:';
  RAISE NOTICE '1. Update application code to use api_credentials table';
  RAISE NOTICE '2. Implement encryption/decryption for credentials';
  RAISE NOTICE '3. Set up regular maintenance tasks';
  RAISE NOTICE '4. Monitor performance and adjust indexes as needed';
  RAISE NOTICE '========================================';
END $$;