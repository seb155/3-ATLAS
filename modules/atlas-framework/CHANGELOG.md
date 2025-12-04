# Changelog

All notable changes to ATLAS Framework will be documented in this file.

## [3.0.0] - 2025-12-03

### Added - Inspired by [Lemmy](https://github.com/badlogic/lemmy)

#### 🔀 Multi-Provider Abstraction
- **Factory functions** for unified LLM access: `providers.anthropic()`, `providers.openai()`, `providers.google()`
- **Fallback chain** - Automatic failover between providers
- **Configuration** via `~/.atlas/providers.json`
- **New command** `/0-provider` for provider management

```javascript
// Lemmy-style API
const claude = providers.anthropic({ model: 'opus' });
const response = await claude.chat(messages);
```

#### 📊 Langfuse Integration (LLM Observability)
- **Docker service** `docker-compose.langfuse.yml` for self-hosted Langfuse
- **Session tracing** - Automatic trace events on session start/stop
- **Token tracking** - Real usage from JSONL transcripts
- **Cost analytics** - Per-session cost breakdown

#### 🖥️ Status Line Node.js
- **Migrated from Bash** - 2.5x faster (~20ms vs ~50ms)
- **Responsive modes** - Ultra Compact, Compact, Standard, Full
- **Modular architecture** - Easy to extend
- **Fallback** - Automatic fallback to Bash if Node.js unavailable

#### 💾 Context Serialization
- **New commands** `/0-context-save` and `/0-context-restore`
- **Checkpoint system** - Save/restore session state
- **Automatic cleanup** - Keeps last 10 checkpoints
- **Rich metadata** - Git state, tokens, files, notes

### Changed

- **Hooks** - SessionStart and Stop now integrate with Langfuse
- **Structure** - New `.claude/lib/` directory for Node.js modules:
  - `lib/providers/` - Multi-provider abstraction
  - `lib/langfuse/` - Langfuse integration
  - `lib/statusline/` - Status line Node.js
  - `lib/context/` - Context serialization

### Files Added

```
.claude/
├── lib/
│   ├── providers/
│   │   ├── index.js          # Multi-provider abstraction
│   │   └── README.md
│   ├── langfuse/
│   │   ├── index.js          # Langfuse integration
│   │   └── README.md
│   ├── statusline/
│   │   ├── index.js          # Node.js status line
│   │   └── README.md
│   └── context/
│       └── index.js          # Context serialization
├── commands/
│   ├── 0-provider.md         # Provider management
│   ├── 0-context-save.md     # Save checkpoint
│   └── 0-context-restore.md  # Restore checkpoint
├── hooks/
│   └── langfuse-session.sh   # Langfuse tracing hook
└── scripts/
    └── statusline-node.sh    # Node.js wrapper

forge/
└── docker-compose.langfuse.yml  # Langfuse Docker service

~/.atlas/
└── providers.json            # Provider configuration
```

## [2.3.0] - 2025-11-XX

### Added
- Temporal Context auto-generation
- Configurable Web Search (`/0-web-toggle`)
- Cost documentation per feature
- Cache optimization (static/dynamic separation)

## [2.2.0] - 2025-11-XX

### Added
- Accurate Token Monitoring from JSONL transcripts
- Token Breakdown (Input/Output/Cache)
- Responsive Status Line
- Tool Analytics (`/0-analyze`)

## [2.1.0] - 2025-10-XX

### Added
- Layering System (`.atlas/` overrides)
- Token Optimization commands
- MCP Management (`/0-mcp`)
- QA Tester Agent
- Context System (hot-files, thresholds)

---

## Migration Guide

### Upgrading to v3.0

1. **Enable Node.js status line** (optional):
   ```json
   // ~/.claude/settings.json
   {
     "statusLine": {
       "type": "command",
       "command": "bash /path/to/.claude/scripts/statusline-node.sh"
     }
   }
   ```

2. **Configure providers** (optional):
   ```bash
   # Set API keys
   export OPENAI_API_KEY=sk-...
   export GOOGLE_API_KEY=...
   ```

3. **Start Langfuse** (optional):
   ```bash
   cd forge
   docker-compose -f docker-compose.yml -f docker-compose.langfuse.yml up -d
   # Access: http://localhost:3001
   ```

4. **Enable Langfuse tracing** (optional):
   ```bash
   export LANGFUSE_ENABLED=true
   export LANGFUSE_HOST=http://localhost:3001
   export LANGFUSE_PUBLIC_KEY=pk-...
   export LANGFUSE_SECRET_KEY=sk-...
   ```
