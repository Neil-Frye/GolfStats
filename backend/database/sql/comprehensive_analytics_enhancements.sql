-- Comprehensive Analytics Enhancements for GolfStats
-- This file contains all additional tables and features for advanced golf analytics

-- ==================================================
-- ANALYTICS AND TRACKING TABLES
-- ==================================================

-- 1. Practice Goals & Progress Tracking
CREATE TABLE IF NOT EXISTS public.practice_goals (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  goal_type character varying NOT NULL CHECK (goal_type IN ('handicap', 'distance', 'accuracy', 'putting', 'consistency', 'custom')),
  metric_name character varying NOT NULL, -- e.g., 'driver_distance', 'gir_percentage', 'putts_per_round'
  target_value real NOT NULL,
  current_value real,
  baseline_value real, -- Starting point when goal was created
  target_date date,
  status character varying DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'abandoned')),
  priority character varying DEFAULT 'medium' CHECK (priority IN ('high', 'medium', 'low')),
  notes text,
  completed_date date,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.practice_goals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own goals" ON public.practice_goals
  FOR ALL USING (auth.uid() = user_id);

-- 2. Course Management Data
CREATE TABLE IF NOT EXISTS public.courses (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name character varying NOT NULL,
  location character varying,
  city character varying,
  state_province character varying,
  country character varying,
  total_holes integer DEFAULT 18,
  par integer,
  course_type character varying CHECK (course_type IN ('public', 'private', 'resort', 'municipal')),
  website_url character varying,
  phone_number character varying,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT unique_course_location UNIQUE(name, city, state_province)
);

-- Course ratings for different tees
CREATE TABLE IF NOT EXISTS public.course_tees (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  course_id bigint NOT NULL REFERENCES public.courses(id) ON DELETE CASCADE,
  tee_name character varying NOT NULL, -- 'Black', 'Blue', 'White', 'Red', etc.
  total_yardage integer,
  course_rating real,
  slope_rating integer,
  par integer,
  created_at timestamp with time zone DEFAULT now()
);

-- Detailed hole information
CREATE TABLE IF NOT EXISTS public.course_hole_details (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  course_id bigint NOT NULL REFERENCES public.courses(id) ON DELETE CASCADE,
  hole_number integer NOT NULL CHECK (hole_number >= 1 AND hole_number <= 18),
  par integer NOT NULL CHECK (par >= 3 AND par <= 6),
  handicap_index integer CHECK (handicap_index >= 1 AND handicap_index <= 18),
  hole_name character varying,
  notes text, -- Tips, hazards, strategy
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT unique_course_hole UNIQUE(course_id, hole_number)
);

-- Hole yardages per tee
CREATE TABLE IF NOT EXISTS public.course_hole_tees (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  course_id bigint NOT NULL REFERENCES public.courses(id) ON DELETE CASCADE,
  tee_id bigint NOT NULL REFERENCES public.course_tees(id) ON DELETE CASCADE,
  hole_number integer NOT NULL CHECK (hole_number >= 1 AND hole_number <= 18),
  yardage integer NOT NULL,
  CONSTRAINT unique_tee_hole UNIQUE(tee_id, hole_number)
);

-- 3. Weather Impact Analysis
CREATE TABLE IF NOT EXISTS public.weather_conditions (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  session_id bigint REFERENCES public.range_sessions(id) ON DELETE CASCADE,
  round_id bigint REFERENCES public.golf_rounds(id) ON DELETE CASCADE,
  temperature_f real,
  feels_like_f real,
  wind_speed_mph real,
  wind_gust_mph real,
  wind_direction character varying,
  humidity_percent real,
  pressure_inhg real,
  conditions character varying, -- 'sunny', 'cloudy', 'rain', 'windy', 'fog'
  precipitation_inches real,
  visibility_miles real,
  altitude_feet real,
  weather_source character varying, -- 'manual', 'api', 'device'
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT check_single_reference CHECK (
    (session_id IS NOT NULL AND round_id IS NULL) OR 
    (session_id IS NULL AND round_id IS NOT NULL)
  )
);

-- Index for efficient lookups
CREATE INDEX IF NOT EXISTS idx_weather_session ON public.weather_conditions(session_id);
CREATE INDEX IF NOT EXISTS idx_weather_round ON public.weather_conditions(round_id);

-- 4. Equipment Changes & Impact
CREATE TABLE IF NOT EXISTS public.equipment_changes (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  club_id bigint REFERENCES public.clubs(id) ON DELETE SET NULL,
  change_date date NOT NULL,
  change_type character varying NOT NULL CHECK (change_type IN ('new_club', 'adjustment', 'regrip', 'reshaft', 'loft_lie', 'weight', 'retired')),
  club_type character varying, -- For new clubs not yet in clubs table
  brand character varying,
  model character varying,
  previous_specs jsonb, -- {loft, lie, length, shaft, grip, etc.}
  new_specs jsonb,
  cost_usd real,
  fitter_name character varying,
  fitting_location character varying,
  performance_notes text,
  created_at timestamp with time zone DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.equipment_changes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own equipment changes" ON public.equipment_changes
  FOR ALL USING (auth.uid() = user_id);

-- 5. Performance Benchmarks
CREATE TABLE IF NOT EXISTS public.performance_benchmarks (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  handicap_range character varying NOT NULL CHECK (handicap_range IN ('scratch', '0-5', '6-10', '11-15', '16-20', '21-25', '26+')),
  category character varying NOT NULL CHECK (category IN ('driving', 'approach', 'short_game', 'putting', 'scoring')),
  metric_name character varying NOT NULL,
  metric_value real NOT NULL,
  unit character varying, -- 'yards', 'percent', 'strokes', etc.
  percentile integer CHECK (percentile IN (10, 25, 50, 75, 90)),
  sample_size integer,
  source character varying NOT NULL, -- 'pga_tour', 'amateur_study', 'app_users', 'trackman', 'arccos'
  source_year integer,
  notes text,
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT unique_benchmark UNIQUE(handicap_range, metric_name, percentile, source)
);

-- 6. Practice Drills & Sessions
CREATE TABLE IF NOT EXISTS public.practice_drills (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name character varying NOT NULL,
  category character varying NOT NULL CHECK (category IN ('driving', 'iron_play', 'wedges', 'putting', 'short_game', 'mental', 'fitness')),
  difficulty_level character varying CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
  description text NOT NULL,
  setup_instructions text,
  success_criteria text,
  typical_duration_minutes integer,
  equipment_needed text[],
  created_by character varying DEFAULT 'system',
  is_public boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now()
);

-- User's practice drill history
CREATE TABLE IF NOT EXISTS public.practice_drill_sessions (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  drill_id bigint NOT NULL REFERENCES public.practice_drills(id),
  session_id bigint REFERENCES public.range_sessions(id) ON DELETE SET NULL,
  performed_date timestamp with time zone DEFAULT now(),
  duration_minutes integer,
  success_rate real CHECK (success_rate >= 0 AND success_rate <= 100),
  notes text,
  improvement_areas text[],
  created_at timestamp with time zone DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.practice_drill_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own drill sessions" ON public.practice_drill_sessions
  FOR ALL USING (auth.uid() = user_id);

-- 7. Handicap Tracking
CREATE TABLE IF NOT EXISTS public.handicap_history (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  handicap_index real NOT NULL,
  calculation_date date NOT NULL,
  rounds_used integer,
  trend character varying CHECK (trend IN ('improving', 'stable', 'declining')),
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT unique_user_handicap_date UNIQUE(user_id, calculation_date)
);

-- Enable RLS
ALTER TABLE public.handicap_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own handicap history" ON public.handicap_history
  FOR SELECT USING (auth.uid() = user_id);

-- 8. Shot Dispersion Patterns
CREATE TABLE IF NOT EXISTS public.shot_dispersion_data (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  club character varying NOT NULL,
  target_distance_yards real NOT NULL,
  landing_x real NOT NULL, -- Lateral deviation in yards (negative = left)
  landing_y real NOT NULL, -- Distance deviation in yards (negative = short)
  shot_id bigint REFERENCES public.golf_shots(id) ON DELETE CASCADE,
  created_at timestamp with time zone DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.shot_dispersion_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own dispersion data" ON public.shot_dispersion_data
  FOR ALL USING (auth.uid() = user_id);

-- ==================================================
-- ENHANCED EXISTING TABLE MODIFICATIONS
-- ==================================================

-- 9. Additional columns for clubs table
ALTER TABLE public.clubs 
  ADD COLUMN IF NOT EXISTS shaft_brand character varying,
  ADD COLUMN IF NOT EXISTS shaft_model character varying,
  ADD COLUMN IF NOT EXISTS shaft_weight_grams real,
  ADD COLUMN IF NOT EXISTS shaft_flex character varying CHECK (shaft_flex IN ('L', 'A', 'R', 'S', 'X', 'XX')),
  ADD COLUMN IF NOT EXISTS grip_brand character varying,
  ADD COLUMN IF NOT EXISTS grip_model character varying,
  ADD COLUMN IF NOT EXISTS grip_size character varying CHECK (grip_size IN ('undersize', 'standard', 'midsize', 'jumbo')),
  ADD COLUMN IF NOT EXISTS purchase_date date,
  ADD COLUMN IF NOT EXISTS purchase_price real,
  ADD COLUMN IF NOT EXISTS custom_fitting boolean DEFAULT false,
  ADD COLUMN IF NOT EXISTS swing_weight character varying,
  ADD COLUMN IF NOT EXISTS total_weight_grams real,
  ADD COLUMN IF NOT EXISTS is_active boolean DEFAULT true;

-- 10. Additional columns for golf_rounds table
ALTER TABLE public.golf_rounds 
  ADD COLUMN IF NOT EXISTS tee_played character varying,
  ADD COLUMN IF NOT EXISTS course_id bigint REFERENCES public.courses(id) ON DELETE SET NULL,
  ADD COLUMN IF NOT EXISTS playing_partners integer DEFAULT 0,
  ADD COLUMN IF NOT EXISTS round_type character varying CHECK (round_type IN ('practice', 'casual', 'tournament', 'league', 'lesson')),
  ADD COLUMN IF NOT EXISTS walking_or_cart character varying CHECK (walking_or_cart IN ('walking', 'cart', 'pushcart')),
  ADD COLUMN IF NOT EXISTS weather_conditions character varying,
  ADD COLUMN IF NOT EXISTS mental_score integer CHECK (mental_score >= 1 AND mental_score <= 10),
  ADD COLUMN IF NOT EXISTS physical_score integer CHECK (physical_score >= 1 AND physical_score <= 10);

-- 11. Additional columns for range_sessions table
ALTER TABLE public.range_sessions 
  ADD COLUMN IF NOT EXISTS session_type character varying CHECK (session_type IN ('practice', 'warmup', 'lesson', 'fitting', 'testing')),
  ADD COLUMN IF NOT EXISTS session_focus character varying[], -- Array of focus areas
  ADD COLUMN IF NOT EXISTS balls_hit integer,
  ADD COLUMN IF NOT EXISTS warmup_routine text,
  ADD COLUMN IF NOT EXISTS instructor_name character varying,
  ADD COLUMN IF NOT EXISTS mental_state character varying CHECK (mental_state IN ('focused', 'relaxed', 'stressed', 'tired', 'energized')),
  ADD COLUMN IF NOT EXISTS technical_focus text[]; -- Array of technical points worked on

-- ==================================================
-- ANALYTICAL VIEWS AND FUNCTIONS
-- ==================================================

-- 12. Strokes Gained Calculation View
CREATE OR REPLACE VIEW public.strokes_gained_analysis AS
WITH benchmark_data AS (
  SELECT 
    handicap_range,
    metric_name,
    metric_value as benchmark_value
  FROM public.performance_benchmarks
  WHERE percentile = 50 -- Use median as benchmark
)
SELECT 
  gs.user_id,
  gs.shot_date,
  gs.club,
  gs.shot_type,
  gs.total_distance_yards,
  bd.benchmark_value,
  CASE 
    WHEN gs.shot_type = 'approach' THEN 
      (bd.benchmark_value - gs.from_pin_yards) / NULLIF(bd.benchmark_value, 0)
    ELSE 0
  END as strokes_gained
FROM public.golf_shots gs
LEFT JOIN auth.users u ON u.id = gs.user_id
LEFT JOIN benchmark_data bd ON bd.metric_name = gs.club
WHERE gs.shot_date >= CURRENT_DATE - INTERVAL '90 days';

-- 13. Club Gapping Analysis View
CREATE OR REPLACE VIEW public.club_gapping_analysis AS
WITH club_distances AS (
  SELECT 
    user_id,
    club,
    AVG(total_distance_yards) as avg_distance,
    STDDEV(total_distance_yards) as consistency,
    COUNT(*) as shot_count
  FROM public.golf_shots
  WHERE shot_type = 'range' 
    AND total_distance_yards > 0
    AND shot_date >= CURRENT_DATE - INTERVAL '180 days'
  GROUP BY user_id, club
  HAVING COUNT(*) >= 10
)
SELECT 
  c1.user_id,
  c1.club as club_1,
  c1.avg_distance as distance_1,
  c2.club as club_2,
  c2.avg_distance as distance_2,
  c2.avg_distance - c1.avg_distance as gap_yards,
  CASE 
    WHEN c2.avg_distance - c1.avg_distance < 8 THEN 'Too Small'
    WHEN c2.avg_distance - c1.avg_distance > 20 THEN 'Too Large'
    ELSE 'Good'
  END as gap_assessment
FROM club_distances c1
JOIN club_distances c2 
  ON c1.user_id = c2.user_id 
  AND c1.avg_distance < c2.avg_distance
WHERE c2.avg_distance - c1.avg_distance > 0
ORDER BY c1.user_id, c1.avg_distance;

-- 14. Round Trend Analysis
CREATE OR REPLACE VIEW public.round_trend_analysis AS
WITH round_scores AS (
  SELECT 
    gr.user_id,
    gr.date,
    gr.total_score,
    gr.total_score - gr.total_par as score_to_par,
    AVG(gr.total_score - gr.total_par) OVER (
      PARTITION BY gr.user_id 
      ORDER BY gr.date 
      ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) as rolling_avg_score,
    rs.fairways_hit::real / NULLIF(rs.fairways_total, 0) * 100 as fairway_pct,
    rs.greens_in_regulation::real / 18 * 100 as gir_pct,
    rs.total_putts,
    rs.putts_per_hole
  FROM public.golf_rounds gr
  LEFT JOIN public.round_stats rs ON gr.id = rs.round_id
)
SELECT 
  *,
  CASE 
    WHEN rolling_avg_score < LAG(rolling_avg_score, 5) OVER (PARTITION BY user_id ORDER BY date) THEN 'Improving'
    WHEN rolling_avg_score > LAG(rolling_avg_score, 5) OVER (PARTITION BY user_id ORDER BY date) THEN 'Declining'
    ELSE 'Stable'
  END as trend
FROM round_scores
ORDER BY user_id, date DESC;

-- ==================================================
-- HELPER FUNCTIONS
-- ==================================================

-- 15. Calculate shot dispersion pattern
CREATE OR REPLACE FUNCTION public.calculate_shot_pattern(
  p_user_id uuid,
  p_club character varying,
  p_days_back integer DEFAULT 90
)
RETURNS jsonb AS $$
DECLARE
  pattern_data jsonb;
BEGIN
  WITH shot_data AS (
    SELECT 
      side_deviation_yards,
      total_distance_yards - AVG(total_distance_yards) OVER () as distance_deviation
    FROM public.golf_shots
    WHERE user_id = p_user_id
      AND club = p_club
      AND shot_date >= CURRENT_DATE - INTERVAL '1 day' * p_days_back
      AND side_deviation_yards IS NOT NULL
  ),
  pattern_calc AS (
    SELECT 
      CASE 
        WHEN AVG(side_deviation_yards) < -5 THEN 'pull'
        WHEN AVG(side_deviation_yards) > 5 THEN 'push'
        WHEN STDDEV(side_deviation_yards) > 15 THEN 'inconsistent'
        ELSE 'straight'
      END as shot_shape,
      CASE 
        WHEN AVG(side_deviation_yards) < 0 THEN 'left'
        WHEN AVG(side_deviation_yards) > 0 THEN 'right'
        ELSE 'center'
      END as typical_miss,
      AVG(ABS(side_deviation_yards)) as avg_dispersion,
      COUNT(*) as sample_size
    FROM shot_data
  )
  SELECT jsonb_build_object(
    'shot_shape', shot_shape,
    'typical_miss', typical_miss,
    'avg_dispersion_yards', ROUND(avg_dispersion::numeric, 1),
    'sample_size', sample_size
  ) INTO pattern_data
  FROM pattern_calc;
  
  RETURN pattern_data;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 16. Get user performance vs benchmarks
CREATE OR REPLACE FUNCTION public.get_performance_vs_benchmark(
  p_user_id uuid,
  p_handicap_range character varying
)
RETURNS TABLE(
  category character varying,
  metric_name character varying,
  user_value real,
  benchmark_value real,
  percentile_rank integer
) AS $$
BEGIN
  RETURN QUERY
  WITH user_stats AS (
    -- Calculate user's current stats
    SELECT 
      'driving' as category,
      'avg_drive_distance' as metric,
      AVG(total_distance_yards) as value
    FROM public.golf_shots
    WHERE user_id = p_user_id
      AND club = 'Driver'
      AND shot_date >= CURRENT_DATE - INTERVAL '90 days'
    
    UNION ALL
    
    SELECT 
      'approach' as category,
      'avg_approach_proximity' as metric,
      AVG(from_pin_yards) as value
    FROM public.golf_shots
    WHERE user_id = p_user_id
      AND shot_type = 'approach'
      AND from_pin_yards IS NOT NULL
      AND shot_date >= CURRENT_DATE - INTERVAL '90 days'
    
    -- Add more metrics as needed
  )
  SELECT 
    us.category,
    us.metric,
    us.value,
    pb.metric_value,
    CASE 
      WHEN us.value >= pb90.metric_value THEN 90
      WHEN us.value >= pb75.metric_value THEN 75
      WHEN us.value >= pb50.metric_value THEN 50
      WHEN us.value >= pb25.metric_value THEN 25
      ELSE 10
    END as percentile_rank
  FROM user_stats us
  LEFT JOIN performance_benchmarks pb 
    ON pb.handicap_range = p_handicap_range 
    AND pb.metric_name = us.metric 
    AND pb.percentile = 50
  LEFT JOIN performance_benchmarks pb90 
    ON pb90.handicap_range = p_handicap_range 
    AND pb90.metric_name = us.metric 
    AND pb90.percentile = 90
  LEFT JOIN performance_benchmarks pb75 
    ON pb75.handicap_range = p_handicap_range 
    AND pb75.metric_name = us.metric 
    AND pb75.percentile = 75
  LEFT JOIN performance_benchmarks pb50 
    ON pb50.handicap_range = p_handicap_range 
    AND pb50.metric_name = us.metric 
    AND pb50.percentile = 50
  LEFT JOIN performance_benchmarks pb25 
    ON pb25.handicap_range = p_handicap_range 
    AND pb25.metric_name = us.metric 
    AND pb25.percentile = 25;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ==================================================
-- SAMPLE DATA FOR BENCHMARKS
-- ==================================================

-- Insert sample benchmark data
INSERT INTO public.performance_benchmarks (handicap_range, category, metric_name, metric_value, unit, percentile, source, source_year)
VALUES 
  -- Driver distance benchmarks
  ('scratch', 'driving', 'avg_drive_distance', 280, 'yards', 50, 'amateur_study', 2024),
  ('0-5', 'driving', 'avg_drive_distance', 260, 'yards', 50, 'amateur_study', 2024),
  ('6-10', 'driving', 'avg_drive_distance', 240, 'yards', 50, 'amateur_study', 2024),
  ('11-15', 'driving', 'avg_drive_distance', 220, 'yards', 50, 'amateur_study', 2024),
  ('16-20', 'driving', 'avg_drive_distance', 200, 'yards', 50, 'amateur_study', 2024),
  
  -- Approach proximity benchmarks
  ('scratch', 'approach', 'avg_approach_proximity', 20, 'feet', 50, 'amateur_study', 2024),
  ('0-5', 'approach', 'avg_approach_proximity', 30, 'feet', 50, 'amateur_study', 2024),
  ('6-10', 'approach', 'avg_approach_proximity', 40, 'feet', 50, 'amateur_study', 2024),
  ('11-15', 'approach', 'avg_approach_proximity', 50, 'feet', 50, 'amateur_study', 2024),
  ('16-20', 'approach', 'avg_approach_proximity', 65, 'feet', 50, 'amateur_study', 2024)
ON CONFLICT (handicap_range, metric_name, percentile, source) DO NOTHING;

-- ==================================================
-- INDEXES FOR PERFORMANCE
-- ==================================================

CREATE INDEX IF NOT EXISTS idx_goals_user_status 
ON public.practice_goals(user_id, status);

CREATE INDEX IF NOT EXISTS idx_equipment_user_date 
ON public.equipment_changes(user_id, change_date DESC);

CREATE INDEX IF NOT EXISTS idx_handicap_user_date 
ON public.handicap_history(user_id, calculation_date DESC);

CREATE INDEX IF NOT EXISTS idx_dispersion_user_club 
ON public.shot_dispersion_data(user_id, club);

CREATE INDEX IF NOT EXISTS idx_drill_sessions_user 
ON public.practice_drill_sessions(user_id, performed_date DESC);

-- ==================================================
-- COMPLETION
-- ==================================================

DO $$
BEGIN
  RAISE NOTICE 'Comprehensive analytics enhancements completed successfully';
  RAISE NOTICE 'New features added:';
  RAISE NOTICE '- Practice goals and progress tracking';
  RAISE NOTICE '- Course management with detailed hole information';
  RAISE NOTICE '- Weather impact tracking';
  RAISE NOTICE '- Equipment change history';
  RAISE NOTICE '- Performance benchmarks and comparisons';
  RAISE NOTICE '- Practice drills and session tracking';
  RAISE NOTICE '- Handicap history';
  RAISE NOTICE '- Shot dispersion patterns';
  RAISE NOTICE '- Analytical views for strokes gained, club gapping, and trends';
END $$;