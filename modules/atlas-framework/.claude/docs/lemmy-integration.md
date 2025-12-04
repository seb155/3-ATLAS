# ATLAS v3.0 - Intégration Lemmy

Documentation des améliorations inspirées de [badlogic/lemmy](https://github.com/badlogic/lemmy).

## Vue d'ensemble

ATLAS v3.0 adapte les patterns de Lemmy au paradigme config-first d'ATLAS:

| Pattern Lemmy | Adaptation ATLAS |
|---------------|------------------|
| Factory functions (`lemmy.anthropic()`) | `providers.anthropic()` |
| Context serialize/deserialize | `/0-context-save`, `/0-context-restore` |
| Differential TUI rendering | Status line Node.js responsive |
| Cost tracking intégré | Langfuse + status line |

---

## 1. Multi-Provider Abstraction

### Fichiers
```
.claude/lib/providers/
├── index.js      # Abstraction unifiée
└── README.md     # Documentation
```

### Usage

```javascript
const providers = require('./.claude/lib/providers');

// Factory functions (Lemmy-style)
const claude = providers.anthropic({ model: 'opus' });
const gpt = providers.openai({ model: 'gpt-4o' });
const gemini = providers.google({ model: 'gemini-pro' });

// Chat completion
const response = await claude.chat([
  { role: 'user', content: 'Hello!' }
]);

// Fallback chain
const chain = providers.withFallback();
const response = await chain.chat(messages); // Tries Anthropic → OpenAI → Google
```

### Configuration

```json
// ~/.atlas/providers.json
{
  "default": "anthropic",
  "fallback": ["openai", "google"],
  "providers": {
    "anthropic": { "defaultModel": "sonnet" },
    "openai": { "defaultModel": "gpt-4o" },
    "google": { "defaultModel": "gemini-pro" }
  }
}
```

### Commande

```bash
/0-provider              # Voir status
/0-provider set openai   # Changer provider
/0-provider test gemini  # Tester connexion
/0-provider fallback on  # Activer fallback
```

---

## 2. Langfuse Integration

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Claude Code                       │
│  SessionStart ──────────────────────────── Stop     │
│       │                                       │      │
│       └──────────── langfuse-session.sh ──────┘      │
└─────────────────────────│────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│              Langfuse (Docker)                       │
│  http://localhost:3001                               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ Traces  │ │Generations│ │ Metrics │ │ Scores  │   │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
└─────────────────────────────────────────────────────┘
```

### Fichiers

```
.claude/lib/langfuse/
├── index.js      # API client
└── README.md     # Documentation

.claude/hooks/
└── langfuse-session.sh   # Hook automatique

forge/
└── docker-compose.langfuse.yml   # Service Docker
```

### Démarrage

```bash
# Démarrer Langfuse
cd modules/forge
docker-compose -f docker-compose.yml -f docker-compose.langfuse.yml up -d

# Accès
open http://localhost:3001
```

### Configuration

```bash
# ~/.atlas/langfuse.env (auto-sourcé par ~/.bashrc)
export LANGFUSE_ENABLED=true
export LANGFUSE_HOST=http://localhost:3001
export LANGFUSE_PUBLIC_KEY=pk-lf-xxxxx
export LANGFUSE_SECRET_KEY=sk-lf-xxxxx
```

### Usage programmatique

```javascript
const langfuse = require('./.claude/lib/langfuse');

// Tracer une session
const { traceId } = await langfuse.traceSession('start', {
  agent: 'BACKEND-BUILDER',
  project: 'SYNAPSE'
});

// Logger l'usage tokens
await langfuse.logUsage(traceId, {
  inputTokens: 5000,
  outputTokens: 1500,
  model: 'claude-opus-4-5'
});

// Sync depuis transcript JSONL
await langfuse.syncTranscript('/path/to/transcript.jsonl', traceId);
```

---

## 3. Status Line Node.js

### Fichiers

```
.claude/lib/statusline/
├── index.js      # Status line Node.js
└── README.md     # Documentation

.claude/scripts/
└── statusline-node.sh   # Wrapper avec fallback
```

### Modes responsifs

| Largeur | Mode | Affichage |
|---------|------|-----------|
| < 60 | Ultra Compact | `💰 $0.45 │ 🟢 37%` |
| 60-89 | Compact | `🏛️ ATLAS │ 🧠 Opus │ 💰 $0.45 │ 🟢 37%` |
| 90-119 | Standard | `+ 📝 75K` |
| ≥ 120 | Full | `+ 📥 5K │ 📤 2K │ 💾 68K` |

### Activation

```json
// ~/.claude/settings.json
{
  "statusLine": {
    "type": "command",
    "command": "bash /home/seb/atlas-framework/.claude/scripts/statusline-node.sh"
  }
}
```

### Performance

| Aspect | Bash | Node.js |
|--------|------|---------|
| Temps | ~50ms | ~20ms |
| Subshells | Nombreux | Aucun |
| Maintenance | Complexe | Modulaire |

---

## 4. Context Serialization

### Fichiers

```
.claude/lib/context/
└── index.js      # Serialize/deserialize

.claude/commands/
├── 0-context-save.md      # /0-context-save
└── 0-context-restore.md   # /0-context-restore
```

### Usage

```bash
# Sauvegarder
/0-context-save Feature authentication complete

# Lister
node .claude/lib/context/index.js list

# Restaurer
/0-context-restore latest.json
```

### Format checkpoint

```json
{
  "version": 1,
  "id": "ctx-1701234567890",
  "timestamp": "2025-12-03T10:15:00.000Z",
  "project": "SYNAPSE",
  "session": {
    "current_agent": "BACKEND-BUILDER",
    "agent_stack": ["ATLAS", "BACKEND-BUILDER"]
  },
  "git": {
    "branch": "feature/auth",
    "commit": "a1b2c3d",
    "changes": 3
  },
  "usage": {
    "totalTokens": 50000,
    "cost": 1.25
  },
  "note": "API endpoints complete",
  "recentFiles": ["src/api/auth.py", "tests/test_auth.py"]
}
```

### Stockage

```
~/.atlas/context/
├── latest.json                    # Dernier checkpoint
├── checkpoint-1701234567890.json  # Historique
└── checkpoint-1701234500000.json  # (max 10 conservés)
```

---

## Commits

| Hash | Description |
|------|-------------|
| `10179381` | feat(atlas): v3.0 - Multi-provider, Langfuse, Node.js statusline |
| `1839057c` | fix(langfuse): correct batch format for Langfuse v2 API |

---

## Prochaines étapes

Voir: [ROADMAP.md](./roadmap-v3.md)
