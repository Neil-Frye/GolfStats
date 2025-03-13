-- GolfStats SQL Update 
-- This SQL script adds shot_type and source_system columns to golf_shots
-- and removes the need for a separate range_shots table

-- Step 1: Add new columns to golf_shots
ALTER TABLE IF EXISTS public.golf_shots 
  ADD COLUMN IF NOT EXISTS shot_type VARCHAR(10) CHECK (shot_type IN ('course', 'sim', 'range')),
  ADD COLUMN IF NOT EXISTS source_system VARCHAR(50),
  ADD COLUMN IF NOT EXISTS session_id BIGINT REFERENCES public.range_sessions(id) ON DELETE SET NULL;

-- Step 2: Update hole_id constraint to be nullable
ALTER TABLE IF EXISTS public.golf_shots 
  ALTER COLUMN hole_id DROP NOT NULL;

-- Step 3: Add constraint that either hole_id or session_id must be set
ALTER TABLE IF EXISTS public.golf_shots 
  ADD CONSTRAINT golf_shots_context_check 
  CHECK ((hole_id IS NOT NULL) OR (session_id IS NOT NULL));

-- Step 4: Migrate data from range_shots to golf_shots
CREATE OR REPLACE FUNCTION migrate_range_shots_to_golf_shots() RETURNS void AS $$
BEGIN
  -- Insert range_shots data into golf_shots
  INSERT INTO public.golf_shots (
    shot_number, club, ball_speed_mph, club_speed_mph, 
    smash_factor, launch_angle_degrees, spin_rate_rpm, 
    spin_axis_degrees, carry_distance_yards, total_distance_yards, 
    side_deviation_yards, session_id, shot_type, source_system,
    created_at, updated_at
  )
  SELECT 
    rs.shot_number, rs.club, rs.ball_speed_mph, rs.club_speed_mph,
    rs.smash_factor, rs.launch_angle_degrees, rs.spin_rate_rpm,
    rs.spin_axis_degrees, rs.carry_distance_yards, rs.total_distance_yards,
    rs.side_deviation_yards, rs.session_id, 'range' as shot_type, 
    COALESCE(sess.source_system, 'manual') as source_system,
    rs.created_at, rs.updated_at
  FROM public.range_shots rs
  JOIN public.range_sessions sess ON rs.session_id = sess.id;
  
  -- Log the migration
  RAISE NOTICE 'Migrated % range shots to golf_shots table', (SELECT COUNT(*) FROM public.range_shots);
END;
$$ LANGUAGE plpgsql;

-- Execute the migration function (uncomment to run)
-- SELECT migrate_range_shots_to_golf_shots();

-- Step 5: Update existing golf_shots to set shot_type = 'course'
UPDATE public.golf_shots 
SET shot_type = 'course', 
    source_system = COALESCE(
      (SELECT source_system FROM public.golf_rounds gr 
       JOIN public.golf_holes gh ON gr.id = gh.round_id 
       WHERE gh.id = golf_shots.hole_id), 
      'manual'
    )
WHERE shot_type IS NULL AND hole_id IS NOT NULL;

-- Step 6: Update RLS policies for golf_shots to handle session_id
DROP POLICY IF EXISTS "Users can view their own shots through holes and rounds" ON public.golf_shots;
CREATE POLICY "Users can view their own shots through holes and rounds" 
  ON public.golf_shots FOR SELECT 
  USING (
    (
      hole_id IS NOT NULL AND EXISTS (
        SELECT 1 FROM public.golf_holes
        JOIN public.golf_rounds ON public.golf_rounds.id = public.golf_holes.round_id
        WHERE public.golf_holes.id = hole_id 
        AND public.golf_rounds.user_id = auth.uid()
      )
    ) OR (
      session_id IS NOT NULL AND EXISTS (
        SELECT 1 FROM public.range_sessions
        WHERE public.range_sessions.id = session_id 
        AND public.range_sessions.user_id = auth.uid()
      )
    )
  );

DROP POLICY IF EXISTS "Users can insert shots to their own holes" ON public.golf_shots;
CREATE POLICY "Users can insert shots to their own holes" 
  ON public.golf_shots FOR INSERT 
  WITH CHECK (
    (
      hole_id IS NOT NULL AND EXISTS (
        SELECT 1 FROM public.golf_holes
        JOIN public.golf_rounds ON public.golf_rounds.id = public.golf_holes.round_id
        WHERE public.golf_holes.id = hole_id 
        AND public.golf_rounds.user_id = auth.uid()
      )
    ) OR (
      session_id IS NOT NULL AND EXISTS (
        SELECT 1 FROM public.range_sessions
        WHERE public.range_sessions.id = session_id 
        AND public.range_sessions.user_id = auth.uid()
      )
    )
  );

DROP POLICY IF EXISTS "Users can update shots in their own holes" ON public.golf_shots;
CREATE POLICY "Users can update shots in their own holes" 
  ON public.golf_shots FOR UPDATE 
  USING (
    (
      hole_id IS NOT NULL AND EXISTS (
        SELECT 1 FROM public.golf_holes
        JOIN public.golf_rounds ON public.golf_rounds.id = public.golf_holes.round_id
        WHERE public.golf_holes.id = hole_id 
        AND public.golf_rounds.user_id = auth.uid()
      )
    ) OR (
      session_id IS NOT NULL AND EXISTS (
        SELECT 1 FROM public.range_sessions
        WHERE public.range_sessions.id = session_id 
        AND public.range_sessions.user_id = auth.uid()
      )
    )
  );

DROP POLICY IF EXISTS "Users can delete shots in their own holes" ON public.golf_shots;
CREATE POLICY "Users can delete shots in their own holes" 
  ON public.golf_shots FOR DELETE 
  USING (
    (
      hole_id IS NOT NULL AND EXISTS (
        SELECT 1 FROM public.golf_holes
        JOIN public.golf_rounds ON public.golf_rounds.id = public.golf_holes.round_id
        WHERE public.golf_holes.id = hole_id 
        AND public.golf_rounds.user_id = auth.uid()
      )
    ) OR (
      session_id IS NOT NULL AND EXISTS (
        SELECT 1 FROM public.range_sessions
        WHERE public.range_sessions.id = session_id 
        AND public.range_sessions.user_id = auth.uid()
      )
    )
  );

-- Step 7: Update club_benchmark_data view
DROP VIEW IF EXISTS public.club_benchmark_data;
CREATE OR REPLACE VIEW public.club_benchmark_data AS
SELECT 
    user_id,
    club,
    shot_type,
    COUNT(*) as shot_count,
    AVG(carry_distance_yards) as avg_carry_distance,
    STDDEV(carry_distance_yards) as std_carry_distance,
    AVG(total_distance_yards) as avg_total_distance,
    STDDEV(total_distance_yards) as std_total_distance,
    AVG(ball_speed_mph) as avg_ball_speed,
    AVG(club_speed_mph) as avg_club_speed,
    AVG(smash_factor) as avg_smash_factor,
    AVG(launch_angle_degrees) as avg_launch_angle,
    AVG(spin_rate_rpm) as avg_spin_rate,
    AVG(ABS(spin_axis_degrees)) as avg_abs_spin_axis,
    AVG(ABS(side_deviation_yards)) as avg_abs_side_deviation,
    MAX(created_at) as last_shot_date
FROM (
    -- Course shots
    SELECT 
        gr.user_id,
        gs.club,
        gs.shot_type,
        gs.carry_distance_yards,
        gs.total_distance_yards,
        gs.ball_speed_mph,
        gs.club_speed_mph,
        gs.smash_factor,
        gs.launch_angle_degrees,
        gs.spin_rate_rpm,
        gs.spin_axis_degrees,
        gs.side_deviation_yards,
        gs.created_at
    FROM 
        public.golf_shots gs
    JOIN 
        public.golf_holes gh ON gs.hole_id = gh.id
    JOIN 
        public.golf_rounds gr ON gh.round_id = gr.id
    WHERE 
        gs.hole_id IS NOT NULL AND gs.club IS NOT NULL
    
    UNION ALL
    
    -- Range and simulator shots
    SELECT 
        rs.user_id,
        gs.club,
        gs.shot_type,
        gs.carry_distance_yards,
        gs.total_distance_yards,
        gs.ball_speed_mph,
        gs.club_speed_mph,
        gs.smash_factor,
        gs.launch_angle_degrees,
        gs.spin_rate_rpm,
        gs.spin_axis_degrees,
        gs.side_deviation_yards,
        gs.created_at
    FROM 
        public.golf_shots gs
    JOIN 
        public.range_sessions rs ON gs.session_id = rs.id
    WHERE 
        gs.session_id IS NOT NULL AND gs.club IS NOT NULL
) combined_shots
GROUP BY 
    user_id, club, shot_type;

-- Step 8: After confirming the migration was successful and all data is moved,
-- you can drop the range_shots table (uncomment when ready)
-- DROP TABLE IF EXISTS public.range_shots;