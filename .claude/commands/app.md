# /app

Gestion du contexte d'application dans le monorepo AXIOM.

## Usage

```text
/app                    # Affiche l'app courante
/app synapse            # Switch vers SYNAPSE
/app synapse backend    # Switch vers SYNAPSE backend
/app nexus              # Switch vers NEXUS
/app prism              # Switch vers PRISM
/app forge              # Switch vers FORGE (infrastructure)
/app global             # Mode monorepo (cross-app)
```

## Applications

| App | Description | Path |
|-----|-------------|------|
| SYNAPSE | MBSE Platform | apps/synapse/ |
| NEXUS | Knowledge Graph | apps/nexus/ |
| PRISM | Enterprise Portal | apps/prism/ |
| ATLAS | AI Collaboration | apps/atlas/ |
| FORGE | Infrastructure | forge/ |

## Comportement

Apres `/app [name]`:

1. Met a jour `.claude/context/current-app.md`
2. Charge les conventions specifiques de l'app
3. Adapte les templates et patterns
4. Ajuste les paths par defaut

## Exemple

```text
User: /app

ATLAS: "Application courante: SYNAPSE (backend + frontend)

Apps disponibles:
- synapse (MVP Dec 2025)
- nexus (Phase 1.5)
- prism (Development)
- forge (Infrastructure)

Pour changer: /app [name]"

---

User: /app nexus

ATLAS: "Switch vers NEXUS.

**NEXUS - Knowledge Graph**
- Stack: React 19 + TypeScript
- Path: apps/nexus/
- Port: 5173
- Status: Phase 1.5

Contexte charge. Pret a travailler sur NEXUS."
```

## Agent invoque

- ATLAS (gestion contexte)
