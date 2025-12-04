# Multi-Provider Abstraction

Unified LLM interface inspired by [Lemmy](https://github.com/badlogic/lemmy).

## Quick Start

```javascript
const providers = require("./.claude/lib/providers");

// Factory functions (Lemmy-style)
const claude = providers.anthropic({ model: "opus" });
const gpt = providers.openai({ model: "gpt-4o" });
const gemini = providers.google({ model: "gemini-pro" });

// Chat completion
const response = await claude.chat([
  { role: "system", content: "You are a helpful assistant." },
  { role: "user", content: "Hello!" },
]);

console.log(response.content);
console.log(response.usage); // { inputTokens, outputTokens }
```

## Providers

| Provider   | Models                       | Env Variable        |
| ---------- | ---------------------------- | ------------------- |
| anthropic  | opus, sonnet, haiku          | ANTHROPIC_API_KEY   |
| openai     | gpt-4o, gpt-4-turbo, o1      | OPENAI_API_KEY      |
| google     | gemini-pro, gemini-flash     | GOOGLE_API_KEY      |

## Fallback Chain

```javascript
// Automatic fallback on errors
const chain = providers.withFallback();

const response = await chain.chat([
  { role: "user", content: "Hello" }
]);

// If Anthropic fails, tries OpenAI, then Google
console.log(`Used: ${response.provider}`);
```

## Configuration

### File: `~/.atlas/providers.json`

```json
{
  "default": "anthropic",
  "fallback": ["openai", "google"],
  "providers": {
    "anthropic": {
      "baseUrl": "https://api.anthropic.com",
      "models": {
        "opus": "claude-opus-4-5-20251101",
        "sonnet": "claude-sonnet-4-5-20250929"
      },
      "defaultModel": "sonnet"
    }
  }
}
```

### Environment Variables

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export GOOGLE_API_KEY=...
```

## API Reference

### Factory Functions

```javascript
providers.anthropic(options)  // Create Anthropic provider
providers.openai(options)     // Create OpenAI provider
providers.google(options)     // Create Google provider
providers.create(name, opts)  // Create by provider name
providers.getDefault(opts)    // Create default provider
providers.withFallback(opts)  // Create fallback chain
```

### Provider Methods

```javascript
provider.chat(messages, options)
// messages: Array<{ role: string, content: string }>
// options: { maxTokens?: number }
// returns: { content, usage, model, provider }
```

### Response Format

```javascript
{
  content: "Hello! How can I help?",
  usage: {
    inputTokens: 15,
    outputTokens: 8
  },
  model: "claude-opus-4-5-20251101",
  provider: "anthropic"
}
```

## CLI Usage

```bash
# Test a provider
node .claude/lib/providers/index.js test anthropic
node .claude/lib/providers/index.js test openai

# Show configuration
node .claude/lib/providers/index.js config
```

## Integration with ATLAS

### Cost-Based Routing

```javascript
// Route simple tasks to cheaper providers
const simpleProvider = providers.openai({ model: "gpt-4o-mini" });
const complexProvider = providers.anthropic({ model: "opus" });

const provider = taskComplexity > 0.7 ? complexProvider : simpleProvider;
```

### With Langfuse Tracing

```javascript
const langfuse = require("../langfuse");
const providers = require("../providers");

const claude = providers.anthropic();
const trace = await langfuse.traceSession("start");

const response = await claude.chat(messages);

await langfuse.logUsage(trace.traceId, {
  inputTokens: response.usage.inputTokens,
  outputTokens: response.usage.outputTokens,
  model: response.model,
});
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Factory Functions                  │
│   anthropic() │ openai() │ google() │ withFallback()│
└─────────────────────────┬───────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│                   BaseProvider                      │
│         Unified interface: chat(), streamChat()     │
└─────────────────────────┬───────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌───────────────┐ ┌───────────────┐
│ AnthropicProvider│ │ OpenAIProvider│ │ GoogleProvider│
│  /v1/messages   │ │/chat/completions│ │:generateContent│
└─────────────────┘ └───────────────┘ └───────────────┘
```
