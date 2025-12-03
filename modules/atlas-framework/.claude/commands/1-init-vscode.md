---
description: Configure VS Code pour ATLAS (settings, extensions, tasks) - axoiq.com
---

# VS Code ATLAS Setup

Configure l'environnement VS Code avec les templates ATLAS optimisés pour axoiq.com.

## Ta tâche

### 1. Détecter l'environnement

Vérifie dans quel contexte tu opères:
- **Windows VS Code natif** - Copier vers `.vscode/`
- **code-server WebUI** - Copier vers `.vscode/` (accessible via https://code.axoiq.com)
- **WSL2** - Même chose, fichiers dans le filesystem Linux

### 2. Détecter le type de projet

Lis `.dev-manifest.json` si présent:
- `context_type: parent` → Monorepo (AXIOM), créer workspace file
- `context_type: child` → Sous-projet (SYNAPSE, NEXUS)
- `context_type: standalone` → Projet indépendant

### 3. Copier les templates

Depuis `.claude/templates/vscode/` vers `.vscode/`:

```
settings.json    → .vscode/settings.json
extensions.json  → .vscode/extensions.json
tasks.json       → .vscode/tasks.json
launch.json      → .vscode/launch.json
```

**Pour monorepos (AXIOM):**
```
axiom.code-workspace → AXIOM.code-workspace (à la racine)
```

**Pour devcontainers:**
```
devcontainer/base/ → .devcontainer/
```

### 4. Personnaliser selon le projet

- Adapter les chemins dans `tasks.json` selon la structure
- Vérifier que les ports correspondent au registry (`.dev/infra/registry.yml`)

### 5. Afficher les prochaines étapes

Après la copie, informer l'utilisateur:

1. **Ouvrir le workspace** (si monorepo):
   ```
   code AXIOM.code-workspace
   ```

2. **Installer les extensions recommandées**:
   - VS Code affichera une notification
   - Ou: `Ctrl+Shift+P` → "Extensions: Show Recommended Extensions"

3. **URLs disponibles** (axoiq.com):
   - https://code.axoiq.com - VS Code WebUI
   - https://synapse.axoiq.com - SYNAPSE
   - https://api.axoiq.com - SYNAPSE API

## Response Protocol

Utiliser le format standard avec Recap + choix numérotés:

```markdown
---

## Recap

- [done] Templates VS Code copiés dans .vscode/
- [done] Workspace file créé (si monorepo)
- [info] Extensions recommandées: X à installer

---

## What do you want to do?

1. **Installer extensions** - Lancer l'installation des extensions recommandées
2. **Ouvrir code.axoiq.com** - Accéder à VS Code WebUI
3. **Configurer devcontainer** - Ajouter support devcontainer
4. **Autre chose** - Décris ce que tu veux

> Tip: Type a number (1-4) or write your request.
```
