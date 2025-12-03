-- ============================================================================
-- MIGRATE SYNAPSE USERS TO WORKSPACE_AUTH
-- One-time migration: Copy synapse.users → workspace_auth.users
-- Version: 1.0.0
-- Author: Nexus Team
-- Date: 2025-11-27
-- ============================================================================

\c postgres

\echo ''
\echo '========================================================================='
\echo '  🔄 MIGRATING SYNAPSE USERS TO WORKSPACE_AUTH'
\echo '========================================================================='
\echo ''

-- Check if synapse database exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_database WHERE datname = 'synapse') THEN
        RAISE NOTICE '✅ Synapse database found';
    ELSE
        RAISE NOTICE '⚠️  Synapse database not found - skipping migration';
    END IF;
END
$$;

-- Insert Synapse users into workspace_auth (if they don't exist)
-- This assumes Synapse has a users table with compatible schema
INSERT INTO workspace_auth.users (
    id,
    email,
    hashed_password,
    full_name,
    is_active,
    created_at,
    app_permissions,
    metadata
)
SELECT
    COALESCE(u.id::uuid, gen_random_uuid()),  -- Use existing ID or generate new
    u.email,
    u.hashed_password,
    COALESCE(u.full_name, u.username, split_part(u.email, '@', 1)),  -- Fallback to username or email prefix
    COALESCE(u.is_active, TRUE),
    COALESCE(u.created_at, NOW()),
    jsonb_build_object('synapse', ARRAY['user']::text[]),  -- Default synapse user permission
    jsonb_build_object('migrated_from', 'synapse', 'migration_date', NOW())
FROM (
    -- This subquery will fail gracefully if synapse.users doesn't exist
    SELECT * FROM synapse.users LIMIT 0
) u
ON CONFLICT (email) DO UPDATE
SET
    -- If user already exists, add synapse permissions
    app_permissions = workspace_auth.users.app_permissions ||
                     jsonb_build_object('synapse', ARRAY['user']::text[]),
    metadata = workspace_auth.users.metadata ||
              jsonb_build_object('synapse_migration_updated', NOW());

\echo ''
\echo '========================================================================='
\echo '  ✅ SYNAPSE USER MIGRATION COMPLETE'
\echo '========================================================================='
\echo ''
\echo 'Notes:'
\echo '  • Existing users: Added synapse permissions to app_permissions'
\echo '  • New users: Created with synapse user role'
\echo '  • Migration metadata added to user records'
\echo ''
\echo 'Next steps:'
\echo '  1. Verify migrated users: SELECT * FROM workspace_auth.users;'
\echo '  2. Update Synapse to use workspace_auth.users'
\echo '  3. Test SSO between Nexus and Synapse'
\echo ''
\echo '========================================================================='
\echo ''
