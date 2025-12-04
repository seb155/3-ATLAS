# ATLAS v3.0 - Roadmap & Prochaines Étapes

## ✅ Complété (v3.0.0)

| Feature | Status | Notes |
|---------|--------|-------|
| Multi-Provider Abstraction | ✅ | Anthropic, OpenAI, Google |
| Langfuse Integration | ✅ | Docker + hooks + API |
| Status Line Node.js | ✅ | 4 modes responsifs |
| Context Serialization | ✅ | Save/restore checkpoints |
| Documentation | ✅ | CHANGELOG + docs |

---

## 🔜 Prochaines Étapes

### Phase 1: Enrichir Langfuse (Priorité Haute)

#### 1.1 Dashboard Grafana pour Langfuse
- [ ] Créer datasource Langfuse → Grafana
- [ ] Dashboard: Coûts par jour/semaine/mois
- [ ] Dashboard: Usage par agent
- [ ] Alertes: Budget dépassé

**Fichiers à créer:**
```
forge/config/grafana/provisioning/dashboards/langfuse.json
```

#### 1.2 Enrichir les traces automatiques
- [ ] Ajouter tokens à chaque trace (depuis transcript)
- [ ] Tracker les tool calls (Read, Write, Bash)
- [ ] Scorer la qualité des réponses (optionnel)

**Fichiers à modifier:**
```
.claude/hooks/PostToolUse-*.sh  # Tracer chaque tool
.claude/lib/langfuse/index.js   # Ajouter métadonnées
```

#### 1.3 Sync automatique des transcripts
- [ ] Cron/service qui sync les JSONL → Langfuse
- [ ] Historique complet des sessions
- [ ] Replay des conversations

---

### Phase 2: Améliorer Multi-Provider (Priorité Moyenne)

#### 2.1 Cost-Based Routing
- [ ] Router automatiquement selon la complexité
- [ ] Haiku pour simple, Sonnet pour code, Opus pour archi
- [ ] Configurable via `.atlas/routing.json`

```javascript
// Exemple
const router = providers.smartRouter({
  simple: 'haiku',
  code: 'sonnet',
  architecture: 'opus'
});
```

#### 2.2 Local LLM Support
- [ ] Ajouter Ollama comme provider
- [ ] Support LM Studio
- [ ] Fallback vers local si API down

```json
// ~/.atlas/providers.json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://localhost:11434",
      "models": { "llama3": "llama3:70b" }
    }
  }
}
```

#### 2.3 Streaming Support
- [ ] Ajouter `streamChat()` à tous les providers
- [ ] Event emitter pour progress
- [ ] Compatible avec status line

---

### Phase 3: TUI Avancée (Priorité Basse)

#### 3.1 Composants lemmy-tui style
- [ ] TextEditor interactif
- [ ] SelectList pour choix
- [ ] MarkdownRenderer
- [ ] Autocomplete pour commandes

**Inspiration:** `lemmy-tui/src/components/`

#### 3.2 Differential Rendering
- [ ] Ne redessiner que les parties changées
- [ ] Réduire le flickering
- [ ] Meilleure performance sur SSH

---

### Phase 4: Context Avancé

#### 4.1 Hot Context automatique
- [ ] Détecter les fichiers critiques
- [ ] Auto-loader au démarrage
- [ ] Sync avec `.dev/context/`

#### 4.2 Semantic Search
- [ ] Indexer les checkpoints dans MeiliSearch
- [ ] Recherche: "quand ai-je travaillé sur auth?"
- [ ] Timeline des décisions

#### 4.3 Context Sharing
- [ ] Exporter un contexte pour partage
- [ ] Importer dans autre session
- [ ] URL publique (optionnel)

---

## 📅 Timeline suggérée

| Semaine | Focus |
|---------|-------|
| S1 | Phase 1.1 - Dashboard Grafana |
| S2 | Phase 1.2 - Traces enrichies |
| S3 | Phase 2.1 - Cost routing |
| S4 | Phase 2.2 - Local LLM |
| S5+ | Phase 3 & 4 selon besoins |

---

## 🎯 Quick Wins (< 1h chacun)

1. **Ajouter MeiliSearch indexing** pour les checkpoints
2. **Créer `/0-langfuse`** pour ouvrir le dashboard
3. **Ajouter cost au trace** depuis le transcript actuel
4. **Webhook Discord** pour alertes budget

---

## 📊 Métriques de succès

| Métrique | Cible |
|----------|-------|
| Coût moyen session | -20% via routing intelligent |
| Temps status line | < 15ms |
| Traces perdues | 0% |
| Checkpoints utilisés | +50% adoption |

---

## 💡 Idées futures

- **MCP Langfuse** - Outil Claude pour query les traces
- **VS Code Extension** - Voir les traces inline
- **CLI `atlas`** - Commande standalone pour gérer ATLAS
- **Web Dashboard** - Interface React pour ATLAS
