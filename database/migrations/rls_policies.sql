-- GolfStats Row Level Security Policies
-- This file contains RLS policies for all tables that contain user-specific data
-- These policies enforce that users can only access their own data

-- Enable RLS on all tables first
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE golf_rounds ENABLE ROW LEVEL SECURITY;
ALTER TABLE golf_holes ENABLE ROW LEVEL SECURITY;
ALTER TABLE golf_shots ENABLE ROW LEVEL SECURITY;
ALTER TABLE round_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE clubs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to prevent errors on re-run)
DROP POLICY IF EXISTS "Users can view their own profile" ON users;
DROP POLICY IF EXISTS "Users can update their own profile" ON users;
DROP POLICY IF EXISTS "Service role has full access" ON users;

DROP POLICY IF EXISTS "Users can view their own golf rounds" ON golf_rounds;
DROP POLICY IF EXISTS "Users can create their own golf rounds" ON golf_rounds;
DROP POLICY IF EXISTS "Users can update their own golf rounds" ON golf_rounds;
DROP POLICY IF EXISTS "Users can delete their own golf rounds" ON golf_rounds;
DROP POLICY IF EXISTS "Service role has full access" ON golf_rounds;

DROP POLICY IF EXISTS "Users can view holes from their own rounds" ON golf_holes;
DROP POLICY IF EXISTS "Users can create holes for their own rounds" ON golf_holes;
DROP POLICY IF EXISTS "Users can update holes from their own rounds" ON golf_holes;
DROP POLICY IF EXISTS "Users can delete holes from their own rounds" ON golf_holes;
DROP POLICY IF EXISTS "Service role has full access" ON golf_holes;

DROP POLICY IF EXISTS "Users can view shots from their own rounds" ON golf_shots;
DROP POLICY IF EXISTS "Users can create shots for their own holes" ON golf_shots;
DROP POLICY IF EXISTS "Users can update shots from their own rounds" ON golf_shots;
DROP POLICY IF EXISTS "Users can delete shots from their own rounds" ON golf_shots;
DROP POLICY IF EXISTS "Service role has full access" ON golf_shots;

DROP POLICY IF EXISTS "Users can view stats from their own rounds" ON round_stats;
DROP POLICY IF EXISTS "Users can create stats for their own rounds" ON round_stats;
DROP POLICY IF EXISTS "Users can update stats from their own rounds" ON round_stats;
DROP POLICY IF EXISTS "Users can delete stats from their own rounds" ON round_stats;
DROP POLICY IF EXISTS "Service role has full access" ON round_stats;

DROP POLICY IF EXISTS "Users can view their own clubs" ON clubs;
DROP POLICY IF EXISTS "Users can create their own clubs" ON clubs;
DROP POLICY IF EXISTS "Users can update their own clubs" ON clubs;
DROP POLICY IF EXISTS "Users can delete their own clubs" ON clubs;
DROP POLICY IF EXISTS "Service role has full access" ON clubs;

DROP POLICY IF EXISTS "Users can view their own preferences" ON user_preferences;
DROP POLICY IF EXISTS "Users can create their own preferences" ON user_preferences;
DROP POLICY IF EXISTS "Users can update their own preferences" ON user_preferences;
DROP POLICY IF EXISTS "Users can delete their own preferences" ON user_preferences;
DROP POLICY IF EXISTS "Service role has full access" ON user_preferences;

-- 1. USERS TABLE
-- Users can read and update only their own profiles
CREATE POLICY "Users can view their own profile"
    ON users FOR SELECT
    USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update their own profile"
    ON users FOR UPDATE
    USING (auth.uid()::text = id::text);

-- 2. GOLF_ROUNDS TABLE
-- Users can CRUD only their own golf rounds
CREATE POLICY "Users can view their own golf rounds"
    ON golf_rounds FOR SELECT
    USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can create their own golf rounds"
    ON golf_rounds FOR INSERT
    WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own golf rounds"
    ON golf_rounds FOR UPDATE
    USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete their own golf rounds"
    ON golf_rounds FOR DELETE
    USING (auth.uid()::text = user_id::text);

-- 3. GOLF_HOLES TABLE
-- Users can CRUD only holes from their own rounds
-- This requires a JOIN to check ownership
CREATE POLICY "Users can view holes from their own rounds"
    ON golf_holes FOR SELECT
    USING (
        round_id IN (
            SELECT id FROM golf_rounds WHERE user_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can create holes for their own rounds"
    ON golf_holes FOR INSERT
    WITH CHECK (
        round_id IN (
            SELECT id FROM golf_rounds WHERE user_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can update holes from their own rounds"
    ON golf_holes FOR UPDATE
    USING (
        round_id IN (
            SELECT id FROM golf_rounds WHERE user_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can delete holes from their own rounds"
    ON golf_holes FOR DELETE
    USING (
        round_id IN (
            SELECT id FROM golf_rounds WHERE user_id::text = auth.uid()::text
        )
    );

-- 4. GOLF_SHOTS TABLE
-- Users can CRUD only shots from their own holes/rounds
-- This requires a JOIN through golf_holes to golf_rounds
CREATE POLICY "Users can view shots from their own rounds"
    ON golf_shots FOR SELECT
    USING (
        hole_id IN (
            SELECT h.id FROM golf_holes h
            JOIN golf_rounds r ON h.round_id = r.id
            WHERE r.user_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can create shots for their own holes"
    ON golf_shots FOR INSERT
    WITH CHECK (
        hole_id IN (
            SELECT h.id FROM golf_holes h
            JOIN golf_rounds r ON h.round_id = r.id
            WHERE r.user_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can update shots from their own rounds"
    ON golf_shots FOR UPDATE
    USING (
        hole_id IN (
            SELECT h.id FROM golf_holes h
            JOIN golf_rounds r ON h.round_id = r.id
            WHERE r.user_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can delete shots from their own rounds"
    ON golf_shots FOR DELETE
    USING (
        hole_id IN (
            SELECT h.id FROM golf_holes h
            JOIN golf_rounds r ON h.round_id = r.id
            WHERE r.user_id::text = auth.uid()::text
        )
    );

-- 5. ROUND_STATS TABLE
-- Users can CRUD only stats from their own rounds
CREATE POLICY "Users can view stats from their own rounds"
    ON round_stats FOR SELECT
    USING (
        round_id IN (
            SELECT id FROM golf_rounds WHERE user_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can create stats for their own rounds"
    ON round_stats FOR INSERT
    WITH CHECK (
        round_id IN (
            SELECT id FROM golf_rounds WHERE user_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can update stats from their own rounds"
    ON round_stats FOR UPDATE
    USING (
        round_id IN (
            SELECT id FROM golf_rounds WHERE user_id::text = auth.uid()::text
        )
    );

CREATE POLICY "Users can delete stats from their own rounds"
    ON round_stats FOR DELETE
    USING (
        round_id IN (
            SELECT id FROM golf_rounds WHERE user_id::text = auth.uid()::text
        )
    );

-- 6. CLUBS TABLE
-- Users can CRUD only their own clubs
CREATE POLICY "Users can view their own clubs"
    ON clubs FOR SELECT
    USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can create their own clubs"
    ON clubs FOR INSERT
    WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own clubs"
    ON clubs FOR UPDATE
    USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete their own clubs"
    ON clubs FOR DELETE
    USING (auth.uid()::text = user_id::text);

-- 7. USER_PREFERENCES TABLE
-- Users can CRUD only their own preferences
CREATE POLICY "Users can view their own preferences"
    ON user_preferences FOR SELECT
    USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can create their own preferences"
    ON user_preferences FOR INSERT
    WITH CHECK (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update their own preferences"
    ON user_preferences FOR UPDATE
    USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can delete their own preferences"
    ON user_preferences FOR DELETE
    USING (auth.uid()::text = user_id::text);

-- Create policy for service role access (admin/backend access)
-- This allows the service role to bypass RLS for administrative operations
-- The service role is used by the backend server
CREATE POLICY "Service role has full access"
    ON users FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Service role has full access"
    ON golf_rounds FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Service role has full access"
    ON golf_holes FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Service role has full access"
    ON golf_shots FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Service role has full access"
    ON round_stats FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Service role has full access"
    ON clubs FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY "Service role has full access"
    ON user_preferences FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');