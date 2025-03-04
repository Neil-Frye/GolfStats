# GolfStats Project Overview

## Vision
The GolfStats project aims to provide golfers with a comprehensive platform to track and analyze their performance data from various sources, including Trackman, Arccos, and Skytrak. The platform integrates data scraping, ETL processes, and visualization tools to offer insights into a golfer's game, all while ensuring data security and privacy.

## Objectives
1. **Data Collection**: Scrape data from Trackman, Arccos, and Skytrak systems.
2. **Data Processing**: Perform ETL (Extract, Transform, Load) operations to clean and standardize the data.
3. **Data Storage**: Store processed data in a secure database with row-level security.
4. **Data Visualization**: Provide a user-friendly interface for visualizing golf statistics and trends.
5. **Data Security**: Ensure user data is isolated and protected with proper authentication.

## Architecture

### Backend
- Flask web application
- Supabase integration for authentication and database
- SQLAlchemy ORM for database abstraction
- Web scrapers for data collection from golf platforms
- ETL processes for data normalization and aggregation
- Scheduled tasks for automated data collection

### Frontend
- Simple HTML/CSS/JavaScript interface
- Data visualization using charts and statistics
- Mobile-responsive design

### Data Sources
- Trackman: Launch monitor data and golf simulator rounds
- Arccos: On-course performance tracking via club sensors
- SkyTrak: Personal launch monitor and simulator data

## Database Design

The application uses a relational database with the following core tables:

1. `users` - User accounts and authentication
2. `golf_rounds` - Golf rounds played by users
3. `golf_holes` - Individual holes within a round
4. `golf_shots` - Individual shots within a hole
5. `round_stats` - Aggregated statistics for a round
6. `clubs` - User's golf club inventory
7. `user_preferences` - User configuration and preferences

## Security Model

### Authentication
- Supabase Auth for user management
- JWT tokens for API authorization
- OAuth integration with Google
- Service roles for administrative access

### Row Level Security (RLS)
The application implements Row Level Security at the database level to ensure users can only access their own data. RLS policies are applied to all user-specific tables.

#### Multi-Layer Security Approach

1. **Authentication Layer**
   - Email/password or Google OAuth authentication
   - JWT tokens issued by Supabase Auth
   - Token validation on every request

2. **Authorization Layer**
   - User ID extracted from JWT token
   - Role-based access control (standard users vs admins)
   - Route-specific access restrictions

3. **Database Security Layer (RLS)**
   - Row-level security policies in PostgreSQL
   - Data isolation based on user identity
   - Service role bypass for administrative functions

#### Key RLS Policy Examples:

1. **Direct Ownership** - Users can only view/modify their own profile
```sql
CREATE POLICY "Users can view their own profile"
    ON users FOR SELECT
    USING (auth.uid()::text = id::text);
```

2. **Primary Records** - Users can only access their own golf rounds
```sql
CREATE POLICY "Users can view their own golf rounds"
    ON golf_rounds FOR SELECT
    USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can create their own golf rounds"
    ON golf_rounds FOR INSERT
    WITH CHECK (auth.uid()::text = user_id::text);
```

3. **Related Records** - Users can only access holes from their own rounds
```sql
CREATE POLICY "Users can view holes from their own rounds"
    ON golf_holes FOR SELECT
    USING (
        round_id IN (
            SELECT id FROM golf_rounds WHERE user_id::text = auth.uid()::text
        )
    );
```

4. **Nested Relationships** - Users can only access shots from their own holes
```sql
CREATE POLICY "Users can view shots from their own rounds"
    ON golf_shots FOR SELECT
    USING (
        hole_id IN (
            SELECT h.id FROM golf_holes h
            JOIN golf_rounds r ON h.round_id = r.id
            WHERE r.user_id::text = auth.uid()::text
        )
    );
```

5. **Administrative Access** - Service role has full access to all tables
```sql
CREATE POLICY "Service role has full access"
    ON users FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');
```

### RLS Policy Management

RLS policies are:
- Defined in SQL files in the database/migrations directory
- Applied automatically on application startup
- Managed through the migration system
- Can be manually updated by administrators via API

## Data Flow

1. **Data Collection**
   - Web scrapers authenticate with golf platforms
   - Extract data from user accounts or uploads
   - Store raw data in staging area
   - Automated daily ETL via GitHub Actions

2. **Data Processing**
   - Normalize data from different sources
   - Calculate derived statistics
   - Generate aggregated metrics
   - Log processing results for monitoring

3. **Data Access**
   - User requests data via API
   - RLS policies ensure data isolation
   - API returns only authorized data

4. **Visualization**
   - Frontend displays statistics and trends
   - Interactive charts and data exploration
   - Performance insights and recommendations

## Future Enhancements
- Advanced machine learning for swing analysis and recommendations
- Integration with Tableau for advanced data visualization
- Performance predictions and equipment optimization
- Mobile app for on-the-go access to golf statistics
- Social features like leaderboards and competitive tracking
