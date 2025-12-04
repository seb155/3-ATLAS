# Rule 50: Tool Usage Optimization

Règles d'optimisation pour minimiser la consommation de tokens lors de l'utilisation des outils Claude Code.

**Priorité:** HAUTE - Appliqué à chaque utilisation d'outil

---

## Principe Fondamental

> **Chaque token compte.** Un outil mal choisi peut coûter 10-100x plus qu'un outil approprié.

---

## 1. Write vs Edit - Économie 70-90%

### ❌ ANTI-PATTERN: Write pour modifier un fichier existant

```
Write(file_path, entire_new_content)
→ Envoie TOUT le contenu dans la requête
→ Fichier 500 lignes = ~2,000 tokens
```

### ✅ PATTERN: Edit pour modifications partielles

```
Edit(file_path, old_string, new_string)
→ Envoie seulement les parties modifiées
→ Modification 10 lignes = ~50 tokens
```

### Règle

| Situation | Outil | Justification |
|-----------|-------|---------------|
| Nouveau fichier | `Write` | Pas d'alternative |
| Modification <50% du fichier | `Edit` | Économie majeure |
| Réécriture >50% du fichier | `Write` | Edit serait plus complexe |
| Renommage variable global | `Edit` avec `replace_all: true` | Une seule opération |

### Exemple Concret

```
Fichier: 200 lignes (800 tokens)

AVEC Write (modifier 5 lignes):
├── Input: 800 tokens
├── Coût: $0.004
└── Efficacité: 2.5%

AVEC Edit (modifier 5 lignes):
├── Input: 40 tokens (old + new strings)
├── Coût: $0.0002
└── Efficacité: 100%

ÉCONOMIE: 95%
```

---

## 2. Pyramide de Recherche

Toujours commencer par l'outil le plus léger et escalader seulement si nécessaire.

```
              ┌─────────┐
              │  Task   │ ← Dernier recours (~2,000-5,000 tokens)
              ├─────────┤
           ┌──┴─────────┴──┐
           │   WebFetch    │ ← Si externe (~5,000-20,000 tokens)
           ├───────────────┤
        ┌──┴───────────────┴──┐
        │        Read         │ ← Fichier spécifique (~100-5,000 tokens)
        ├─────────────────────┤
     ┌──┴─────────────────────┴──┐
     │          Grep             │ ← Recherche contenu (~50-200 tokens)
     ├───────────────────────────┤
  ┌──┴───────────────────────────┴──┐
  │            Glob                 │ ← Recherche fichiers (~20-100 tokens)
  └─────────────────────────────────┘
```

### Règle des 3 Appels

- Si une recherche nécessite **≤3 appels** Glob/Grep → Utiliser directement
- Si une recherche nécessite **>3 appels** → Considérer `Task` avec agent `Explore`

### Exemples

| Besoin | ❌ Coûteux | ✅ Économique |
|--------|-----------|---------------|
| Trouver un fichier | `Task("find config file")` | `Glob("**/config*.{json,yaml}")` |
| Chercher une fonction | `Task("where is handleAuth")` | `Grep("handleAuth", type="ts")` |
| Lire une classe | `Task("read UserService")` | `Glob` → `Read` |
| Explorer architecture | `Read` de 20 fichiers | `Task(subagent_type="Explore")` |

---

## 3. Read Optimisé

### ❌ ANTI-PATTERN: Lire fichiers entiers systématiquement

```
Read(file_path)  # Fichier 2000 lignes = 8000 tokens
```

### ✅ PATTERN: Utiliser offset/limit pour gros fichiers

```
# D'abord trouver la ligne pertinente
Grep("class UserService", file_path, output_mode="content", -n=true)
→ Résultat: ligne 450

# Puis lire seulement la section
Read(file_path, offset=440, limit=100)
→ 100 lignes = 400 tokens au lieu de 8000
```

### Seuils Recommandés

| Taille fichier | Stratégie |
|----------------|-----------|
| <200 lignes | `Read` complet OK |
| 200-500 lignes | `Read` complet ou ciblé selon contexte |
| >500 lignes | **Toujours** `Grep` d'abord, puis `Read` ciblé |

---

## 4. Parallélisation Intelligente

### ✅ PATTERN: Appels indépendants en parallèle

Quand plusieurs recherches sont indépendantes, les lancer **dans le même message**:

```
Message 1:
├── Glob("**/*.test.ts")
├── Glob("**/*.spec.ts")
└── Grep("describe\\(")

→ 3 résultats en 1 round-trip
→ Économie: 2 messages = ~1,000 tokens
```

### ❌ ANTI-PATTERN: Appels séquentiels inutiles

```
Message 1: Glob("**/*.test.ts")
Message 2: Glob("**/*.spec.ts")
Message 3: Grep("describe\\(")

→ 3 round-trips
→ Surcoût: contexte répété 3x
```

### Quand Séquentialiser

Séquentialiser **seulement** si le résultat d'un appel est nécessaire pour le suivant:

```
1. Glob("**/config.json")     → Trouve: src/config.json
2. Read("src/config.json")    → Dépend du résultat de 1
```

---

## 5. TodoWrite Efficace

### Règle

- **Utiliser** pour tâches complexes (3+ étapes)
- **Ne pas utiliser** pour tâches simples (1-2 étapes)
- **Mettre à jour immédiatement** après chaque tâche complétée

### Coût

Chaque TodoWrite = ~200-400 tokens. Éviter les mises à jour trop fréquentes:

| ❌ Inefficace | ✅ Efficace |
|--------------|-------------|
| Mise à jour après chaque ligne de code | Mise à jour après chaque tâche logique |
| 10 todos pour une feature simple | 3-5 todos bien découpés |
| Todos vagues ("faire le truc") | Todos actionnables ("Créer UserService.ts") |

---

## 6. Bash vs Outils Spécialisés

### Règle Absolue

> **JAMAIS** utiliser Bash pour ce qu'un outil spécialisé fait mieux.

| Action | ❌ Bash | ✅ Outil |
|--------|---------|---------|
| Lire fichier | `cat file.txt` | `Read(file.txt)` |
| Chercher texte | `grep "pattern" .` | `Grep("pattern")` |
| Trouver fichiers | `find . -name "*.ts"` | `Glob("**/*.ts")` |
| Modifier fichier | `sed -i 's/old/new/'` | `Edit(old, new)` |
| Créer fichier | `echo "content" > file` | `Write(file, content)` |

### Bash Légitime

Utiliser Bash **uniquement** pour:
- Commandes système: `git`, `npm`, `docker`, `pytest`
- Scripts d'exécution: `npm run build`, `./deploy.sh`
- Diagnostic: `docker ps`, `ps aux`

---

## 7. Task (Agents) - Utilisation Stratégique

### Coût Élevé

Chaque `Task` spawn un sous-agent avec:
- Son propre system prompt (~1,000 tokens)
- Le contexte du projet (~1,000-3,000 tokens)
- Les instructions de tâche (~200-500 tokens)

**Total: 2,000-5,000 tokens minimum**

### Quand Utiliser Task

| Situation | Utiliser Task? |
|-----------|----------------|
| Recherche simple (1-2 Glob/Grep) | ❌ Non |
| Exploration codebase (5+ fichiers) | ✅ Oui, `Explore` |
| Implémentation code complexe | ✅ Oui, `backend-builder` |
| Question sur Claude Code | ✅ Oui, `claude-code-guide` |
| Lecture d'un fichier connu | ❌ Non, utiliser `Read` |

---

## Checklist Rapide

Avant chaque utilisation d'outil, vérifier:

- [ ] **Write** → Est-ce un nouveau fichier? Sinon, utiliser **Edit**
- [ ] **Read** → Fichier >500 lignes? Utiliser **Grep** d'abord
- [ ] **Task** → Puis-je faire avec ≤3 Glob/Grep? Si oui, pas de Task
- [ ] **Bash** → Y a-t-il un outil spécialisé? (Read/Edit/Grep/Glob)
- [ ] **Parallèle** → Ces appels sont-ils indépendants? Grouper si oui

---

## Métriques Cibles

| Métrique | Bon | Acceptable | À Optimiser |
|----------|-----|------------|-------------|
| Ratio Edit/Write | >3:1 | 1:1-3:1 | <1:1 |
| Task calls/session | <5 | 5-15 | >15 |
| Avg tool input size | <500 chars | 500-1K | >1K |
| Parallel tool calls | Oui | Parfois | Jamais |

---

## Enforcement Automatique

### Hook PreToolUse-Write

Un hook surveille automatiquement les appels `Write` et:
- **Mode warn** (défaut): Affiche un rappel si le fichier existe
- **Mode block**: Bloque le Write et force l'utilisation d'Edit

**Configuration:**
```bash
# Mode warn (défaut) - affiche rappel
export ATLAS_WRITE_MODE=warn

# Mode block - bloque Write sur fichiers existants
export ATLAS_WRITE_MODE=block

# Désactiver le hook
export ATLAS_WRITE_MODE=off
```

**Fichier:** `.claude/hooks/PreToolUse-Write.sh`

### Comment Claude Code charge les règles

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code Startup                       │
├─────────────────────────────────────────────────────────────┤
│  1. Charge ~/.claude/settings.json (global)                 │
│  2. Charge .claude/settings.json (projet) - override        │
│  3. Lit CLAUDE.md → Ajoute au contexte                      │
│  4. Exécute hooks SessionStart                              │
│  5. Les fichiers rules/*.md sont des RÉFÉRENCES             │
│     → Chargés quand explicitement lus ou référencés         │
└─────────────────────────────────────────────────────────────┘
```

**Important:** Les règles ne sont PAS injectées automatiquement dans chaque prompt.
Elles sont chargées quand:
1. CLAUDE.md les référence explicitement
2. Un hook affiche un message
3. Claude les lit avec `Read`

---

## Références

- [Cost Optimization](../../../docs/cost-optimization.md)
- [Token Monitoring](../../../docs/token-monitoring.md)
- [/0-analyze command](../../../commands/0-analyze.md)
- [Hook PreToolUse-Write](./../hooks/PreToolUse-Write.sh)
