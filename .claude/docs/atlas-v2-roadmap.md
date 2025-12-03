# ATLAS v2.0 - Intelligent Agent Framework Roadmap

**Status**: Approved
**Created**: 2025-12-01
**Version**: 2.0.0

---

## Vision

Système d'agent AI **hybride local/cloud** qui :
- Utilise la **puissance locale** (CPU/GPU) pour le traitement
- Envoie **uniquement le nécessaire** au cloud (Claude)
- Maintient une **mémoire persistante** (court/long terme)
- Supporte des **context blocks assemblables**
- Est **extensible** via MCP et agents spécialisés

---

## Architecture (7 Layers)

```
L1: Interface     → CLI / VS Code / NEXUS (future)
L2: Orchestrator  → ATLAS Core (Plan/Act/Review modes)
L3: Local Process → Repo Analyzer + Context System + Memory (0 tokens)
L4: Optimizer     → Context Compression
L5: AI Router     → Claude / Gemini / Ollama / OpenAI
L6: Tool Executor → Native Tools + MCP
L7: Execution     → Job Engine + Rule Engine + Trace Engine
```

---

## Composants à Créer

### context/atlas.py (CLI principal)
- `search "query"` → Fichiers pertinents
- `extract file.md "section"` → Sections ciblées
- `assemble blocks` → Contexte combiné
- `index` → Régénère l'index

### context/repo_analyzer.py
- Tree-sitter pour parser AST
- PageRank pour identifier symboles importants
- Génère repo map optimisé (~2K tokens)

### context/blocks.py
- ContextBlock: id, type, version, content
- ContextAssembler: combine blocks avec budget token
- Types: profile, project, client, product, custom

### context/memory.py
- Working Memory (session, volatile)
- Short-Term Memory (project, SQLite)
- Long-Term Memory (persistent, decay + consolidation)
- Temporal awareness: history, snapshots, restore

### context/optimizer.py
- Relevance scoring par tâche
- Semantic deduplication
- Hierarchical packing
- Token budget enforcement

### context/router.py
- AIModel enum: OLLAMA, HAIKU, SONNET, OPUS, GEMINI, GPT4O
- Route par complexité + context size + cost

---

## Structure Fichiers

```
.claude/context/
├── __init__.py
├── atlas.py           # CLI principal
├── repo_analyzer.py   # Tree-sitter + PageRank
├── blocks.py          # Context blocks
├── memory.py          # Memory system
├── optimizer.py       # Compression
├── router.py          # AI routing
├── index.json         # Auto-généré
├── memory.db          # SQLite
└── blocks/            # Blocks stockés
    ├── profile_default.json
    └── project_*.json
```

---

## Phases d'Implémentation

### Phase 1: Core
- [ ] context/atlas.py - CLI search/extract/index
- [ ] context/repo_analyzer.py - Tree-sitter + PageRank
- [ ] context/index.json - Auto-génération

### Phase 2: Memory
- [ ] context/memory.py - STM/LTM
- [ ] context/memory.db - SQLite schema

### Phase 3: Blocks
- [ ] context/blocks.py - Assemblage
- [ ] Templates blocks

### Phase 4: Optimization
- [ ] context/optimizer.py
- [ ] context/router.py

### Phase 5: Integration
- [ ] Hook SessionStart
- [ ] Integration agents

---

## Économies Estimées

| Scénario | Sans | Avec | Économie |
|----------|------|------|----------|
| Refactoring | 50K | 8K | 84% |
| Debug | 20K | 4K | 80% |
| Simple fix | 5K | 0 (local) | 100% |

---

## Sources

- [Aider Repo Map](https://aider.chat/docs/repomap.html)
- [Cline Plan/Act](https://github.com/cline/cline)
- [Mem0 Memory](https://mem0.ai/research)
- [Microsoft Foundry Hybrid](https://techcommunity.microsoft.com)
- [mcp-agent](https://github.com/lastmile-ai/mcp-agent)

---

**Next**: Implémenter Phase 1 (context/atlas.py + repo_analyzer.py)
