# Langfuse Integration for ATLAS

LLM Observability for Claude Code sessions.

## Setup

### 1. Start Langfuse in Forge

```bash
cd modules/forge
docker-compose -f docker-compose.yml -f docker-compose.langfuse.yml up -d
```

Access: http://localhost:3001 or https://langfuse.axoiq.com

### 2. Create API Keys

1. Open Langfuse UI
2. Go to Settings → API Keys
3. Create a new key pair (Public + Secret)

### 3. Configure Environment

Add to your shell profile (`~/.bashrc` or `~/.zshrc`):

```bash
export LANGFUSE_ENABLED=true
export LANGFUSE_HOST=http://localhost:3001
export LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
export LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
```

Or create `.env.langfuse` in your home directory:

```env
LANGFUSE_ENABLED=true
LANGFUSE_HOST=http://localhost:3001
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxx
```

## Usage

### Automatic Session Tracking

The `langfuse-session.sh` hook automatically sends trace events when:

- Session starts (SessionStart hook calls it)
- Session ends (Stop hook calls it)

### Manual Tracing

```bash
# From command line
node .claude/lib/langfuse/index.js trace start
node .claude/lib/langfuse/index.js trace stop

# Sync a transcript
node .claude/lib/langfuse/index.js sync ~/.claude/projects/xxx/transcript.jsonl
```

### Programmatic Usage

```javascript
const langfuse = require("./.claude/lib/langfuse");

// Trace session events
await langfuse.traceSession("start", { agent: "ATLAS", project: "myapp" });
await langfuse.traceSession("checkpoint", { note: "Feature complete" });
await langfuse.traceSession("stop");

// Log token usage
await langfuse.logUsage(traceId, {
  inputTokens: 5000,
  outputTokens: 1500,
  cacheRead: 10000,
  model: "claude-opus-4-5",
});

// Sync transcript file
await langfuse.syncTranscript(
  "~/.claude/projects/xxx/transcript.jsonl",
  sessionId
);
```

## Features

| Feature               | Description                    |
| --------------------- | ------------------------------ |
| Session Traces        | Track start/stop/checkpoints   |
| Token Usage           | Input/Output/Cache breakdown   |
| Cost Calculation      | Opus 4.5 pricing ($5/$25/M)    |
| Agent Tracking        | Which agent ran each operation |
| Project Association   | Group traces by project        |
| Transcript Sync       | Parse JSONL and send to Fuse   |

## Dashboard Views

In Langfuse UI:

- **Traces** → All ATLAS sessions with metadata
- **Generations** → Token usage per session
- **Metrics** → Cost/latency aggregations
- **Scores** → (Future) Quality metrics

## Troubleshooting

### Check Langfuse is running

```bash
curl http://localhost:3001/api/public/health
```

### Test API connection

```bash
curl -X POST http://localhost:3001/api/public/ingestion \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n 'pk-xxx:sk-xxx' | base64)" \
  -d '{"batch":[]}'
```

### View logs

```bash
docker logs forge-langfuse -f
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Claude Code                       │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐                │
│  │ SessionStart │  │     Stop     │  (hooks)       │
│  └──────┬───────┘  └──────┬───────┘                │
│         │                 │                         │
│         └────────┬────────┘                         │
│                  ▼                                  │
│  ┌───────────────────────────────────────────────┐ │
│  │           langfuse-session.sh                  │ │
│  │              or index.js                       │ │
│  └───────────────────────┬───────────────────────┘ │
└──────────────────────────│──────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────┐
│                  Langfuse (Forge)                    │
│                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   Traces    │  │ Generations │  │   Metrics   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
└──────────────────────────────────────────────────────┘
```
