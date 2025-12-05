# Upstream Vendor Management

**SYNC REQUIRES EXPLICIT APPROVAL**

This directory manages vendored upstream dependencies from the Miessler Suite.

## Tracked Upstreams

| Project | Fork | Upstream |
|---------|------|----------|
| PAI | seb155/Personal_AI_Infrastructure | danielmiessler/Personal_AI_Infrastructure |
| Fabric | seb155/Fabric | danielmiessler/fabric |

## Sync Policy

1. **NO automatic sync** - All upstream changes require explicit approval
2. **Check monthly** - `./check-updates.sh`
3. **Review before sync** - Examine changes before applying
4. **Log all syncs** - Document in `SYNC_LOG.md`

## Commands

```bash
# Check for upstream updates
./check-updates.sh

# View diff for specific project
./check-updates.sh --diff pai

# Request sync (creates approval request)
./request-sync.sh pai

# Approve and apply sync (REQUIRES CONFIRMATION)
./approve-sync.sh pai
```
