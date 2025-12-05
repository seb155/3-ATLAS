# ATLAS 3.0 History System (UOCS)

Based on PAI's UOCS (Universal Output Capture System).

## Directory Structure

```
history/
├── sessions/           # Session summaries (YYYY-MM/)
│   └── 2025-12/
│       └── session-2025-12-04-abc123.md
├── logs/               # JSONL event logs
│   └── events-2025-12-04.jsonl
└── learnings/          # Problem-solving narratives
    └── 2025-12/
```

## Session Summary Format

```markdown
# Session Summary - 2025-12-04

## CAPTURE
[Key decisions and context worth preserving]

## ACTIONS
[Steps taken during session]

## RESULTS
[Outcomes achieved]

## NEXT
[Recommended follow-up actions]
```

## Automatic Capture

The hook system automatically:
1. Initializes session tracking at start
2. Captures tool outputs
3. Generates summaries at session end
4. Archives to history directory

## Search

```bash
# Quick keyword search
rg -i "keyword" .atlas/core/history/

# Recent sessions
ls -lt .atlas/core/history/sessions/2025-12/ | head -10
```
