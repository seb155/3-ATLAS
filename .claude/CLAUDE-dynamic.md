# Atlas Framework - Dynamic Context

> **NOTE**: This file contains content that changes frequently.
> Place this content AFTER static content to preserve cache hits.

---

## Current Version

**Atlas Agent Framework v2.3**

This is a reusable Claude Code agent framework. Use it as `.claude/` in your projects.

---

## What's New

### V2.3 (Current)

- **Temporal Context**: Auto-generated date awareness (no more knowledge cutoff confusion!)
- **Configurable Web Search**: `/0-web-toggle` for economic or auto mode
- **Cost Documentation**: Full cost analysis per feature in `docs/cost-optimization.md`
- **Web Search Rules**: Smart triggers for when to search vs propose
- **Cache Optimization**: Static/dynamic content separation for better prompt caching

### V2.2

- **Accurate Token Monitoring**: Real token counts from JSONL transcripts (not estimates!)
- **Token Breakdown**: Separate Input/Output/Cache tracking with Opus 4.5 pricing
- **Responsive Status Line**: Adapts to terminal width (Full/Standard/Compact/Ultra)
- **Tool Analytics**: `/0-analyze` identifies expensive patterns
- **Cache Savings**: Track savings from prompt caching (up to 90%!)

### V2.1

- **Layering System**: Projects can override framework components via `.atlas/`
- **Token Optimization**: `/0-tokens`, `/0-compact` commands
- **MCP Management**: `/0-mcp` for managing MCP servers
- **QA Tester Agent**: Automated testing with pytest/vitest
- **Context System**: Hot-files, thresholds, smart loading
- **Infrastructure Rules**: Traefik, Docker networking, URL registry

---

## Quick Start

Start every session with:
- `/0-session-start` - Full context load (first session of day)
- `/0-session-continue` - Quick continue existing session
- `/0-session-recover` - Recovery after /compact

End sessions with:
- `/9-git-ship` - Git workflow (test + commit + push)

**All commands support `[project-id]` argument:**
```bash
/0-session-continue echo      # Continue ECHO project
/0-session-start synapse      # Start SYNAPSE session
/9-git-ship mechvision        # Ship MechVision changes
```

---

## Token Monitoring Features

- Real token counts from JSONL transcripts (not estimates!)
- Separate Input ($5/M) / Output ($25/M) / Cache ($0.50/M) tracking
- Responsive status line adapts to terminal width
- Cache savings calculator (up to 90% savings!)

**Cost Optimization:**
- Prompt Caching: 90% reduction on repeated context
- Lazy-Loading: Load agents/rules only when needed
- Model Routing: Haiku for simple tasks, Sonnet for code, Opus for architecture

See: `.claude/docs/token-monitoring.md`, `.claude/docs/cost-optimization.md`

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| `docs/cost-optimization.md` | Cost analysis and optimization strategies |
| `docs/token-monitoring.md` | Token tracking and monitoring |
| `docs/session-management.md` | Session lifecycle documentation |
| `docs/cli-customization.md` | CLI and statusline setup |
| `docs/commands-reference.md` | Full commands documentation |
