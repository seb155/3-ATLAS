# Multi-Provider Management

Manage LLM providers for ATLAS sessions.

## Arguments

- `$ARGUMENTS` - Provider action: `status`, `set <provider>`, `test <provider>`, `fallback <on|off>`

## Actions

Execute the requested provider action:

### If no arguments or `status`:
Display current provider configuration:
1. Read `~/.atlas/providers.json`
2. Show:
   - Current default provider
   - Fallback chain (if enabled)
   - Available providers and their models
   - API key status (configured/missing) for each provider

### If `set <provider>`:
Change the default provider:
1. Validate provider exists (anthropic, openai, google)
2. Update `~/.atlas/providers.json`
3. Confirm the change

### If `test <provider>`:
Test a provider connection:
1. Run: `node .claude/lib/providers/index.js test <provider>`
2. Report success/failure
3. Show response time and token usage

### If `fallback <on|off>`:
Toggle fallback mode:
1. Update `~/.atlas/providers.json`
2. When `on`: Enable fallback chain (default → fallback providers)
3. When `off`: Use only default provider

## Output Format

```
🔀 ATLAS Multi-Provider Status
═══════════════════════════════════════════════════════

📍 Default Provider: anthropic (opus)
🔄 Fallback Chain: openai → google

┌─────────────┬──────────────────────┬────────────┐
│ Provider    │ Models               │ API Key    │
├─────────────┼──────────────────────┼────────────┤
│ anthropic   │ opus, sonnet, haiku  │ ✅ Set     │
│ openai      │ gpt-4o, o1, o1-mini  │ ✅ Set     │
│ google      │ gemini-pro, flash    │ ❌ Missing │
└─────────────┴──────────────────────┴────────────┘

📝 Config: ~/.atlas/providers.json
```

## Environment Variables

Required API keys:
- `ANTHROPIC_API_KEY` - For Claude models
- `OPENAI_API_KEY` - For GPT models
- `GOOGLE_API_KEY` - For Gemini models

## Examples

```bash
/0-provider                    # Show status
/0-provider set openai         # Switch to OpenAI
/0-provider test anthropic     # Test Anthropic connection
/0-provider fallback on        # Enable fallback chain
```

## Notes

- Provider changes affect subagents spawned by Task tool
- Claude Code itself always uses Anthropic (this manages programmatic calls)
- Useful for cost optimization: use cheaper providers for simple tasks
