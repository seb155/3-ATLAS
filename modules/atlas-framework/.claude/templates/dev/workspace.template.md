# {{PROJECT_NAME}} Workspace

> Auto-generated workspace map for AI navigation

## Project Structure

```
{{PROJECT_ID}}/ (parent)
├── .dev/                  # Parent context
{{CHILDREN_TREE}}
```

## Children Projects

| Project | Path | Status | Progress |
|---------|------|--------|----------|
{{CHILDREN_TABLE}}

## Shared Resources

| Resource | Location | Purpose |
|----------|----------|---------|
| Credentials | `context/credentials.md` | DB, services, admin |
| Infrastructure | `infra/registry.yml` | Port registry |
| Decisions | `context/decisions.md` | ADRs |

## AI Navigation

```bash
# View this workspace
/0-workspace

# Start session in child
cd apps/{{CHILD_ID}} && /0-new-session

# Access parent context from child
# AI automatically loads via .dev-manifest.json
```

## Quick Status

**Last Updated:** {{TIMESTAMP}}

{{STATUS_SUMMARY}}

---

*This file is auto-generated. Edit `.dev-manifest.json` to update structure.*
