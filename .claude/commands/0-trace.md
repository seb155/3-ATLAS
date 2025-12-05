# Claude Trace - Visual Session Analysis

Generate interactive HTML reports from Claude Code sessions using [claude-trace](https://github.com/badlogic/lemmy/tree/main/apps/claude-trace).

## Quick Actions

### 1. List Available Sessions

```bash
bash /home/seb/projects/.claude/scripts/trace-report.sh --list
```

### 2. Generate Report for Current Project

```bash
bash /home/seb/projects/.claude/scripts/trace-report.sh
```

### 3. Generate Report for Specific Session

```bash
bash /home/seb/projects/.claude/scripts/trace-report.sh --file <path-to-jsonl>
```

## What claude-trace Captures (vs native JSONL)

| Data | Native JSONL | claude-trace |
|------|--------------|--------------|
| Messages user/assistant | Yes | Yes |
| Tool calls & outputs | Yes | Yes |
| Token usage | Yes | Yes |
| **System prompts** | No | **Yes** |
| **Thinking blocks (full)** | Partial | **Yes** |
| **HTTP headers/timing** | No | **Yes** |
| **Failed requests** | No | **Yes** |
| **Detailed cache hits** | Partial | **Yes** |

## Command Options

| Command | Description |
|---------|-------------|
| `/0-trace` | Generate report for current project |
| `/0-trace --list` | List all available sessions |
| `/0-trace --latest` | Analyze most recent session |
| `/0-trace --all` | Generate index of all sessions |

## Shell Aliases (added to ~/.bashrc)

```bash
ct                  # Launch Claude with full tracing
claude-full         # Same as ct
ct-report <file>    # Generate HTML from JSONL
ct-index            # Generate session index
```

## Session Locations

Sessions are stored in:
```
~/.claude/projects/-{encoded-path}/*.jsonl
```

Example paths:
- `~/.claude/projects/-home-seb-projects/` - This workspace
- `~/.claude/projects/-home-seb-projects-AXIOM/` - AXIOM project

## Generated Reports

Reports are saved to:
```
~/.claude/reports/
├── 2024-12-03_projects_trace.html
├── 2024-12-03_AXIOM_trace.html
└── index.html  (via ct-index)
```

## Workflow Recommendation

1. **Start session with tracing:**
   ```bash
   ct   # instead of 'claude'
   ```

2. **Work normally** - ATLAS functions as usual

3. **After session, analyze:**
   ```
   /0-trace
   ```

4. **View report** - Opens automatically in browser

## Complementary Commands

| Command | Purpose |
|---------|---------|
| `/0-tokens` | Real-time token dashboard |
| `/0-analyze` | Tool usage analysis |
| `/0-trace` | Visual HTML report |
