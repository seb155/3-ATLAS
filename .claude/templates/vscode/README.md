# VS Code Templates for ATLAS

Templates VS Code optimisés pour le développement ATLAS sur `axoiq.com`.

## Utilisation

### Option 1: Commande ATLAS
```bash
/1-init-vscode
```

### Option 2: Copie manuelle
```bash
cp -r .claude/templates/vscode/.  .vscode/
```

## Fichiers inclus

| Fichier | Description |
|---------|-------------|
| `settings.json` | Settings optimisés pour Python, TypeScript, Docker |
| `extensions.json` | Extensions recommandées (Claude Code, Python, Docker...) |
| `tasks.json` | Tâches FORGE et SYNAPSE |
| `launch.json` | Configs de debug (FastAPI, Pytest, Chrome) |
| `axiom.code-workspace` | Workspace multi-root pour monorepo |
| `devcontainer/base/` | Template devcontainer avec Python 3.11, Node 20 |

## URLs (axoiq.com)

| Service | URL |
|---------|-----|
| code-server | https://code.axoiq.com |
| SYNAPSE | https://synapse.axoiq.com |
| SYNAPSE API | https://api.axoiq.com |
| NEXUS | https://nexus.axoiq.com |
| Grafana | https://grafana.axoiq.com |
| Traefik | https://traefik.axoiq.com |

## Tâches disponibles

- `FORGE: Start All` - Démarrer infrastructure
- `FORGE: Start with code-server` - Démarrer avec VS Code WebUI
- `FORGE: Stop All` - Arrêter tout
- `SYNAPSE: Dev Backend` - Backend en mode dev
- `SYNAPSE: Dev Frontend` - Frontend en mode dev
- `SYNAPSE: Test Backend` - Lancer les tests

## Ports utilisés

| Port | Service | Domaine |
|------|---------|---------|
| 3050 | code-server (seb) | code.axoiq.com |
| 3051 | code-server (user1) | code-user1.axoiq.com |
| 4000 | SYNAPSE frontend | synapse.axoiq.com |
| 8000 | SYNAPSE backend | api.axoiq.com |

## Prérequis

- Docker + Docker Compose
- Traefik avec certificats `*.axoiq.com`
- Pi-hole DNS ou entrées hosts
- (Optionnel) Sysbox pour Docker-in-Docker sécurisé
