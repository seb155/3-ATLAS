# MCP Server Management

Gestion des serveurs MCP pour optimiser la consommation de tokens.

## Contexte

Les serveurs MCP peuvent consommer **30,000-60,000 tokens** avant même de commencer à travailler. Un seul serveur avec 20 outils = ~14,000 tokens.

## Commandes

```bash
# Voir les serveurs actifs
/mcp

# Désactiver un serveur
/mcp disable {server_name}

# Activer un serveur
/mcp enable {server_name}
```

## Profils MCP

Définis dans `.atlas/config.yml`:

| Profil | Serveurs | Usage | Tokens estimés |
|--------|----------|-------|----------------|
| **minimal** | filesystem | Opérations fichiers basiques | ~5k |
| **development** | filesystem, git | Dev standard | ~15k |
| **full** | filesystem, git, docker, database | Infrastructure complète | ~40k+ |

## Workflow

### 1. Vérifier l'usage MCP

```
/mcp
```

Affiche:
```
╔══════════════════════════════════════════════════════════════╗
║  🔌 MCP SERVER STATUS                                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Active Servers: 3                                           ║
║  Estimated tokens: ~35,000                                   ║
║                                                              ║
║  ├─ filesystem     ✅ Active    (~5,000 tokens)              ║
║  ├─ git            ✅ Active    (~8,000 tokens)              ║
║  ├─ docker         ✅ Active    (~12,000 tokens)             ║
║  └─ database       ⚪ Inactive                               ║
║                                                              ║
║  Recommendation: Disable 'docker' if not needed              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### 2. Optimiser selon la tâche

| Tâche | Profil recommandé |
|-------|-------------------|
| Lecture/édition code | minimal |
| Dev avec git commits | development |
| Infrastructure Docker | full |
| Exploration codebase | minimal |

### 3. Changer de profil

```bash
# Désactiver les serveurs non utilisés
/mcp disable docker
/mcp disable database

# Ou utiliser McPick (si installé)
npx mcpick
```

## Configuration

### .atlas/config.yml

```yaml
token_optimization:
  mcp:
    auto_disable_unused: true
    max_active_servers: 2
    warn_at_tokens: 30000
    profiles:
      minimal:
        servers: ["filesystem"]
      development:
        servers: ["filesystem", "git"]
      full:
        servers: ["filesystem", "git", "docker", "database"]
```

### .claude/settings.json

```json
{
  "mcp": {
    "max_active_servers": 2,
    "warn_token_threshold": 30000
  }
}
```

## Alertes

| Condition | Action |
|-----------|--------|
| MCP tokens > 30k | Warning affiché |
| Serveurs > max_active | Suggestion désactivation |
| Serveur inutilisé 10+ min | Auto-disable (si configuré) |

## Best Practices

1. **Démarrer minimal** - Activer serveurs au besoin
2. **Désactiver après usage** - Docker après deploy
3. **Monitorer régulièrement** - `/0-tokens` inclut MCP
4. **Profils par tâche** - Changer selon le contexte

## Notes

- Les tokens MCP sont consommés au DÉMARRAGE de session
- Chaque outil déclaré = ~700 tokens
- Préférer outils natifs Claude Code quand possible
- McPick permet toggle rapide par session
