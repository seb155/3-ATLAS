# Token Usage Dashboard

Affiche l'état du contexte et recommandations d'optimisation.

## Commandes à exécuter

```bash
# 1. Vérifier utilisation contexte
/context

# 2. Vérifier coût session
/cost
```

## Dashboard Format

```
╔══════════════════════════════════════════════════════════════╗
║  📊 TOKEN USAGE DASHBOARD                                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Context Window                                              ║
║  ├─ Used: {used_tokens} / 200,000 ({percent}%)               ║
║  ├─ Status: {OK/WARNING/CRITICAL}                            ║
║  └─ Recommendation: {action}                                 ║
║                                                              ║
║  Session Cost                                                ║
║  ├─ Input tokens: {input}                                    ║
║  ├─ Output tokens: {output}                                  ║
║  └─ Total: ${cost}                                           ║
║                                                              ║
║  Active Resources                                            ║
║  ├─ MCP Servers: {count} (~{mcp_tokens} tokens)              ║
║  ├─ Loaded files: {count}                                    ║
║  └─ Agents running: {count}                                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

## Thresholds & Actions

| Context % | Status | Action |
|-----------|--------|--------|
| 0-50% | ✅ OK | Continue normally |
| 50-70% | ⚠️ WARNING | Consider /0-compact |
| 70-80% | 🟠 HIGH | Run /0-compact soon |
| 80-95% | 🔴 CRITICAL | Run /0-compact NOW |
| 95%+ | ⛔ AUTO | Auto-compact triggered |

## Optimization Tips

### If context > 50%
```
/0-compact
```

### If MCP tokens > 30k
```
/mcp
# Disable unused servers
```

### If too many files loaded
```
# Use @imports instead of reading files
# Reference: @.claude/docs/platform.md
```

### If agents consuming too much
```
# Check .atlas/config.yml for limits
# Reduce max_concurrent or switch to haiku
```

## Quick Actions

| Command | Effect |
|---------|--------|
| `/context` | Show current usage |
| `/cost` | Show session cost |
| `/compact` | Compress history |
| `/0-compact` | Smart compress with state save |
| `/mcp` | Manage MCP servers |
| `/model haiku` | Switch to cheaper model |

## Budget Tracking

From `.atlas/config.yml`:
```yaml
token_optimization:
  budget:
    max_per_session: 500000
    warn_at_percent: 80
    critical_at_percent: 95
```

## Notes

- Check `/0-tokens` regularly during long sessions
- Prefer manual /0-compact at 50% over auto at 95%
- MCP servers can consume 30k+ tokens silently
- Each parallel agent uses its own context budget
