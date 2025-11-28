# When to Rebuild Docker - AI Rule

**CRITICAL:** Rebuild Docker after ANY frontend/backend code changes.

## Rebuild Required:

✅ **Frontend** (`apps/synapse/frontend/`): `.tsx`, `.ts` files, `vite.config.ts`, `package.json`
✅ **Backend** (`apps/synapse/backend/`): `.py` files, `requirements.txt`
✅ **Build configs**: Dockerfile, docker-compose changes

## NO Rebuild:

❌ Documentation (`.md` files)
❌ Agent files (`.agent/`)
❌ DB migrations (run at startup)

## Workflow

After code changes: `/07-docker-rebuild` (auto-executes via turbo)

## Enforcement

**BEFORE asking user to test:**
1. Run `/07-docker-rebuild`
2. Wait for completion
3. Verify logs show "ready"
4. THEN ask user to hard refresh

**Never ask user to test without rebuilding first.**
