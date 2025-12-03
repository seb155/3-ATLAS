-- ==============================================================================
-- CREATE TEST USER FOR NEXUS AND SYNAPSE
-- ==============================================================================
-- Creates a test user with access to both Nexus and Synapse
-- Password: testuser123 (bcrypt hashed)
-- ==============================================================================

\c postgres

INSERT INTO workspace_auth.users (email, hashed_password, full_name, app_permissions, metadata)
VALUES (
    'test@example.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',  -- testuser123
    'Test User',
    '{"nexus": ["editor"], "synapse": ["viewer"]}'::jsonb,
    '{"created_by": "test_script", "purpose": "testing"}'::jsonb
)
ON CONFLICT (email) DO UPDATE
SET
    full_name = EXCLUDED.full_name,
    app_permissions = EXCLUDED.app_permissions;

\echo 'Test user created/updated:'
\echo '  Email: test@example.com'
\echo '  Password: testuser123'
\echo '  Permissions: Nexus (editor), Synapse (viewer)'
