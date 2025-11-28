-- ============================================================================
-- NEXUS DATABASE INITIALIZATION
-- Creates: nexus database + workspace_auth schema for shared authentication
-- Version: 1.0.0
-- Author: Nexus Team
-- Date: 2025-11-27
-- ============================================================================

-- Create Nexus application databases
CREATE DATABASE nexus;
CREATE DATABASE nexus_test;  -- For integration tests

\echo '✅ Nexus databases created'

-- Connect to postgres database for workspace_auth schema
\c postgres

-- ============================================================================
-- WORKSPACE_AUTH SCHEMA - Shared Authentication
-- Used by: Synapse, Nexus, future apps
-- Provides: SSO-like authentication across workspace applications
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS workspace_auth;

\echo '✅ workspace_auth schema created'

-- Users table - Shared across all workspace apps
CREATE TABLE IF NOT EXISTS workspace_auth.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,

    -- App-specific permissions (JSONB for flexibility)
    -- Example: {"synapse": ["admin"], "nexus": ["editor"], "portal": ["viewer"]}
    app_permissions JSONB DEFAULT '{}'::jsonb,

    -- Metadata for extensibility
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Email validation constraint
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_email ON workspace_auth.users(email);
CREATE INDEX idx_users_is_active ON workspace_auth.users(is_active);
CREATE INDEX idx_users_app_permissions ON workspace_auth.users USING GIN (app_permissions);

\echo '✅ workspace_auth.users table created'

-- JWT Refresh Tokens (for token rotation strategy)
CREATE TABLE IF NOT EXISTS workspace_auth.refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES workspace_auth.users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,  -- SHA-256 hash of refresh token
    app_name VARCHAR(50) NOT NULL,     -- 'nexus', 'synapse', etc.
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,

    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES workspace_auth.users(id)
);

CREATE INDEX idx_refresh_tokens_user_id ON workspace_auth.refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_token_hash ON workspace_auth.refresh_tokens(token_hash);
CREATE INDEX idx_refresh_tokens_expires_at ON workspace_auth.refresh_tokens(expires_at);

\echo '✅ workspace_auth.refresh_tokens table created'

-- Audit log for auth events
CREATE TABLE IF NOT EXISTS workspace_auth.audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES workspace_auth.users(id) ON DELETE SET NULL,
    app_name VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- 'login', 'logout', 'register', 'password_change', etc.
    ip_address INET,
    user_agent TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_log_user_id ON workspace_auth.audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON workspace_auth.audit_log(created_at);
CREATE INDEX idx_audit_log_event_type ON workspace_auth.audit_log(event_type);

\echo '✅ workspace_auth.audit_log table created'

-- Updated trigger function for timestamp updates
CREATE OR REPLACE FUNCTION workspace_auth.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON workspace_auth.users
FOR EACH ROW
EXECUTE FUNCTION workspace_auth.update_updated_at_column();

\echo '✅ workspace_auth triggers created'

-- ============================================================================
-- NEXUS SCHEMA - Application-specific tables
-- ============================================================================

\c nexus

\echo '✅ Connected to nexus database'

-- Notes table (user_id references workspace_auth.users)
CREATE TABLE IF NOT EXISTS notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,  -- References workspace_auth.users(id)
    title VARCHAR(500) NOT NULL,
    content TEXT,
    content_plain TEXT,  -- Plain text for search indexing
    parent_id UUID REFERENCES notes(id) ON DELETE CASCADE,  -- For hierarchical notes
    is_folder BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,  -- Soft delete

    -- Full-text search vector
    content_tsvector TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content_plain, ''))
    ) STORED
);

CREATE INDEX idx_notes_user_id ON notes(user_id);
CREATE INDEX idx_notes_parent_id ON notes(parent_id);
CREATE INDEX idx_notes_content_tsvector ON notes USING GIN (content_tsvector);
CREATE INDEX idx_notes_deleted_at ON notes(deleted_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_notes_title ON notes(title);

\echo '✅ notes table created'

-- Updated trigger for notes
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_notes_updated_at
BEFORE UPDATE ON notes
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Wiki Links (bidirectional links between notes)
CREATE TABLE IF NOT EXISTS wiki_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    target_note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    link_text VARCHAR(255),  -- Text used in the wiki link
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(source_note_id, target_note_id)
);

CREATE INDEX idx_wiki_links_source ON wiki_links(source_note_id);
CREATE INDEX idx_wiki_links_target ON wiki_links(target_note_id);

\echo '✅ wiki_links table created'

-- Tags (for categorization)
CREATE TABLE IF NOT EXISTS tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,  -- References workspace_auth.users(id)
    name VARCHAR(100) NOT NULL,
    color VARCHAR(7) DEFAULT '#6366f1',  -- Hex color
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(user_id, name)
);

CREATE INDEX idx_tags_user_id ON tags(user_id);
CREATE INDEX idx_tags_name ON tags(name);

\echo '✅ tags table created'

-- Note-Tag associations
CREATE TABLE IF NOT EXISTS note_tags (
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (note_id, tag_id)
);

CREATE INDEX idx_note_tags_note ON note_tags(note_id);
CREATE INDEX idx_note_tags_tag ON note_tags(tag_id);

\echo '✅ note_tags table created'

-- ============================================================================
-- SEED DATA - Initial workspace admin user
-- ============================================================================

\c postgres

-- Seed initial workspace admin user (if not exists)
-- Default password: "admin" (CHANGE IN PRODUCTION!)
INSERT INTO workspace_auth.users (email, hashed_password, full_name, is_superuser, app_permissions, metadata)
VALUES (
    'admin@localhost',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS1qZ0yGO',  -- password: "admin"
    'Workspace Administrator',
    TRUE,
    '{"synapse": ["admin"], "nexus": ["admin"]}'::jsonb,
    '{"created_by": "init_script", "version": "1.0.0"}'::jsonb
)
ON CONFLICT (email) DO NOTHING;

\echo '✅ Default admin user created (email: admin@localhost, password: admin)'

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

-- Grant permissions on workspace_auth schema
GRANT USAGE ON SCHEMA workspace_auth TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA workspace_auth TO postgres;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA workspace_auth TO postgres;

\c nexus

-- Grant permissions on nexus database
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO postgres;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO postgres;

\echo '✅ Permissions granted'

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

\c postgres

\echo ''
\echo '========================================================================='
\echo '  ✅ NEXUS DATABASE INITIALIZATION COMPLETE'
\echo '========================================================================='
\echo ''
\echo 'Databases created:'
\echo '  • nexus           - Main application database'
\echo '  • nexus_test      - Testing database'
\echo ''
\echo 'Schemas created:'
\echo '  • workspace_auth  - Shared authentication (in postgres database)'
\echo ''
\echo 'Tables created:'
\echo '  workspace_auth:'
\echo '    • users          - Shared user accounts'
\echo '    • refresh_tokens - JWT refresh tokens'
\echo '    • audit_log      - Authentication events'
\echo ''
\echo '  nexus:'
\echo '    • notes          - User notes with full-text search'
\echo '    • wiki_links     - Bidirectional note links'
\echo '    • tags           - Note tags/categories'
\echo '    • note_tags      - Note-tag associations'
\echo ''
\echo 'Default admin account:'
\echo '  Email:    admin@localhost'
\echo '  Password: admin (CHANGE THIS IN PRODUCTION!)'
\echo ''
\echo '========================================================================='
\echo ''
