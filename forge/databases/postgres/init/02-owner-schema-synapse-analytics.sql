-- Owner Analytics Schema for synapse_analytics
-- This script should be run against the synapse_analytics database.

CREATE SCHEMA IF NOT EXISTS owner;

CREATE TABLE IF NOT EXISTS owner.health_scorecards (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version TEXT NOT NULL,
    area TEXT NOT NULL, -- backend, frontend, infra, rule-engine, etc.
    reliability INTEGER NOT NULL,
    dx INTEGER NOT NULL,
    observability INTEGER NOT NULL,
    ux INTEGER NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS owner.test_runs (
    id UUID PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    project TEXT NOT NULL,   -- synapse
    component TEXT NOT NULL, -- backend, frontend, e2e
    version TEXT NOT NULL,
    suite TEXT NOT NULL,     -- smoke, full, regression, etc.
    total INTEGER NOT NULL,
    passed INTEGER NOT NULL,
    failed INTEGER NOT NULL,
    skipped INTEGER NOT NULL,
    report_url TEXT,
    origin TEXT NOT NULL     -- ai, human, ci
);

CREATE TABLE IF NOT EXISTS owner.tech_debt_items (
    id UUID PRIMARY KEY,
    code TEXT NOT NULL,      -- CR-YYYYMMDD-XX
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    area TEXT NOT NULL,      -- backend, frontend, infra, docs, cross-cutting
    title TEXT NOT NULL,
    context TEXT,
    impact TEXT NOT NULL,    -- high, medium, low
    effort TEXT NOT NULL,    -- S, M, L
    risk TEXT NOT NULL,      -- high, medium, low
    type TEXT NOT NULL,      -- refactor, bug, dx, perf, arch
    status TEXT NOT NULL,    -- open, in_progress, done, wont_fix
    target_version TEXT,
    source_file TEXT         -- e.g. .dev/roadmap/backlog/core-platform-v0.2.x.md
);

CREATE TABLE IF NOT EXISTS owner.architecture_checkpoints (
    id UUID PRIMARY KEY,
    version TEXT NOT NULL,          -- v0.2.3, v0.3.0, etc.
    planned_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL,           -- planned, in_progress, done, skipped
    summary TEXT,
    main_risks TEXT,
    main_decisions TEXT
);

