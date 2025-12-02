# Token Monitoring Skill

Quick access to token usage and optimization status.

## Activation

```
skill: "tokens"
```

## Output

```
╔══════════════════════════════════════════════════════════════╗
║  📊 ATLAS TOKEN MONITOR                                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  CONTEXT WINDOW                                              ║
║  ════════════════                                            ║
║  Used:    {tokens} / 200,000 ({percent}%)                    ║
║  Status:  {OK | WARNING | CRITICAL}                          ║
║  [████████████░░░░░░░░░░░░░░░░░░] {percent}%                 ║
║                                                              ║
║  BREAKDOWN                                                   ║
║  ════════════════                                            ║
║  ├─ Conversation:  {conv_tokens}                             ║
║  ├─ CLAUDE.md:     ~450 tokens (optimized)                   ║
║  ├─ MCP Servers:   ~{mcp_tokens} ({server_count} active)     ║
║  └─ Files loaded:  {file_count}                              ║
║                                                              ║
║  SESSION COST                                                ║
║  ════════════════                                            ║
║  Input:   {input_tokens}                                     ║
║  Output:  {output_tokens}                                    ║
║  Total:   ${cost}                                            ║
║                                                              ║
║  AGENTS                                                      ║
║  ════════════════                                            ║
║  Running: {running_count}                                    ║
║  Budget:  {used}/{max_budget} tokens                         ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  RECOMMENDATION                                              ║
║  {action_recommendation}                                     ║
╚══════════════════════════════════════════════════════════════╝
```

## Status Thresholds

| Percent | Status | Color | Action |
|---------|--------|-------|--------|
| 0-50% | OK | Green | Continue |
| 50-70% | WARNING | Yellow | Consider /0-compact |
| 70-80% | HIGH | Orange | Run /0-compact soon |
| 80-95% | CRITICAL | Red | Run /0-compact NOW |
| 95%+ | AUTO | - | Auto-compact triggered |

## Commands Triggered

Based on status, suggest:

- **OK**: "Continue working normally"
- **WARNING**: "Run `/0-compact` when convenient"
- **HIGH**: "Run `/0-compact` before next major task"
- **CRITICAL**: "Run `/0-compact` immediately to avoid auto-compact"

## Integration

This skill reads from:
- `/context` command output
- `/cost` command output
- `.atlas/config.yml` for thresholds
- `.claude/context/agent-status.json` for agent tracking

## Usage

```
# Quick check
skill: "tokens"

# Detailed with commands
/0-tokens

# Just context
/context

# Just cost
/cost
```
