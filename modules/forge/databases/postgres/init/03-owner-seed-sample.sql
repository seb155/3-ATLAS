-- Optional demo seed for synapse_analytics.owner.*
-- Inserts sample rows only if the tables are currently empty.

DO $$
BEGIN
    -- Seed health_scorecards
    IF NOT EXISTS (SELECT 1 FROM owner.health_scorecards LIMIT 1) THEN
        INSERT INTO owner.health_scorecards (id, version, area, reliability, dx, observability, ux, notes)
        VALUES
            (md5(random()::text || clock_timestamp()::text)::uuid, 'v0.2.2', 'backend', 4, 4, 5, 4, 'Initial backend review'),
            (md5(random()::text || clock_timestamp()::text)::uuid, 'v0.2.2', 'frontend', 4, 4, 4, 4, 'UI polish needed'),
            (md5(random()::text || clock_timestamp()::text)::uuid, 'v0.2.2', 'infra', 5, 4, 5, 4, 'Stable infra stack');
    END IF;

    -- Seed test_runs
    IF NOT EXISTS (SELECT 1 FROM owner.test_runs LIMIT 1) THEN
        INSERT INTO owner.test_runs (id, started_at, finished_at, project, component, version, suite, total, passed, failed, skipped, report_url, origin)
        VALUES
            (md5(random()::text || clock_timestamp()::text)::uuid, NOW() - interval '1 day', NOW() - interval '1 day' + interval '5 minutes',
             'synapse', 'backend', 'v0.2.2', 'regression', 130, 124, 6, 0, 'backend HTML report (local)', 'demo'),
            (md5(random()::text || clock_timestamp()::text)::uuid, NOW() - interval '22 hours', NOW() - interval '22 hours' + interval '4 minutes',
             'synapse', 'frontend', 'v0.2.2', 'smoke', 104, 98, 6, 0, 'playwright HTML report (local)', 'demo'),
            (md5(random()::text || clock_timestamp()::text)::uuid, NOW() - interval '12 hours', NOW() - interval '12 hours' + interval '7 minutes',
             'synapse', 'e2e', 'v0.2.2', 'full', 42, 42, 0, 0, 'playwright HTML report (local)', 'demo');
    END IF;

    -- Seed tech_debt_items
    IF NOT EXISTS (SELECT 1 FROM owner.tech_debt_items LIMIT 1) THEN
        INSERT INTO owner.tech_debt_items (id, code, created_at, updated_at, area, title, context, impact, effort, risk, type, status, target_version, source_file)
        VALUES
            (md5(random()::text || clock_timestamp()::text)::uuid, 'CR-20251126-01', NOW(), NOW(),
             'backend', 'Stabilize import error handling', 'Handle CSV edge cases + retries', 'high', 'M', 'medium', 'bug', 'open', 'v0.2.3', '.dev/roadmap/backlog/core-platform-v0.2.x.md'),
            (md5(random()::text || clock_timestamp()::text)::uuid, 'CR-20251126-02', NOW(), NOW(),
             'cross-cutting', 'Standardize logging fields', 'Consistent request_id/session_id', 'medium', 'S', 'low', 'refactor', 'in_progress', 'v0.2.4', '.dev/roadmap/backlog/core-platform-v0.2.x.md');
    END IF;

    -- Seed architecture_checkpoints
    IF NOT EXISTS (SELECT 1 FROM owner.architecture_checkpoints LIMIT 1) THEN
        INSERT INTO owner.architecture_checkpoints (id, version, planned_at, completed_at, status, summary, main_risks, main_decisions)
        VALUES
            (md5(random()::text || clock_timestamp()::text)::uuid, 'v0.2.3', NOW() + interval '3 days', NULL, 'planned',
             '3-tier asset model readiness review', 'Data model alignment with procurement', NULL),
            (md5(random()::text || clock_timestamp()::text)::uuid, 'v0.2.4', NOW() - interval '1 day', NOW() - interval '1 day', 'done',
             'Breakdown structures navigation', 'Tree performance at scale', 'Use materialized path for FBS');
    END IF;
END;
$$;
