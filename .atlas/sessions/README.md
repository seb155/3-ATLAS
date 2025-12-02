# ATLAS Sessions Directory

Session state management for Document & Clear pattern.

## Structure

```
.atlas/sessions/
├── README.md              # This file
├── current.md             # Active session state (auto-updated)
├── compact-{timestamp}.md # Saved before /compact
├── archive/               # Completed sessions
│   └── {date}.md
└── templates/             # Templates for session files
    ├── compact-template.md
    └── session-summary.md
```

## Workflow

### During Session

1. `/0-new-session` or `/0-next` → Creates/updates `current.md`
2. Work progresses → `current.md` updated with state
3. `/0-compact` → Saves to `compact-{timestamp}.md`
4. `/0-resume` → Loads from latest compact file

### End of Day

1. `/0-compact` → Final state save
2. Move `compact-*.md` to `archive/` if desired
3. Next day: `/0-new-session` starts fresh

### Recovery

```bash
# After /compact
/0-resume

# New conversation
@CLAUDE.md @.atlas/sessions/compact-{latest}.md
Continue from saved state
```

## File Naming

| File | Format | Purpose |
|------|--------|---------|
| current.md | Static | Active session |
| compact-*.md | `compact-YYYY-MM-DD-HHmm.md` | Pre-compact snapshots |
| archive/*.md | `YYYY-MM-DD.md` | Completed sessions |

## Auto-Update Triggers

`current.md` should be updated:
- After each significant task completion
- Before any /compact
- When switching apps
- On TodoWrite state change

## Integration with .claudeignore

```
# Sessions archive excluded from auto-load
.atlas/sessions/archive/
.atlas/sessions/archive/**
```

Only `current.md` and latest `compact-*.md` loaded by default.

## Commands

| Command | Session Action |
|---------|----------------|
| `/0-new-session` | Create new current.md |
| `/0-next` | Update current.md |
| `/0-compact` | Save to compact-{ts}.md |
| `/0-resume` | Load from compact-{ts}.md |
| `/0-dashboard` | Display current.md state |
