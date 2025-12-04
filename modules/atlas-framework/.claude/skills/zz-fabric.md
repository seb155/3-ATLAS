# Fabric Pattern Bridge (Native Mode)

Applique les patterns Fabric **directement dans Claude Code** - sans CLI, sans clé API supplémentaire.

**[Fabric](https://github.com/danielmiessler/fabric)** by Daniel Miessler fournit 234 patterns crowd-sourcés pour transformer du contenu.

---

## Usage

**Invoke with**:
- Skill tool: `skill: "zz-fabric"`
- Direct: "Utilise le pattern summarize sur ce texte"

**Parameters**:
```yaml
skill: "zz-fabric"
pattern: "summarize"           # Required: nom du pattern
input: "texte ou fichier"      # Optional: contenu à traiter
```

---

## Core Patterns

### Résumé & Extraction

| Pattern | Description | Usage ATLAS |
|---------|-------------|-------------|
| `summarize` | Résumé structuré (1 phrase + points + takeaways) | Sessions, docs longs |
| `extract_wisdom` | Extrait IDEAS, INSIGHTS, QUOTES, HABITS, FACTS | Podcasts, vidéos, articles |
| `create_summary` | Résumé structuré avec sections | Notes de réunion |
| `create_micro_summary` | Résumé ultra-court | Changelogs |

### Développement & Code

| Pattern | Description | Usage ATLAS |
|---------|-------------|-------------|
| `review_code` | Code review expert (sécurité, perf, best practices) | Avant chaque commit |
| `explain_code` | Explique le code en langage clair | Onboarding, documentation |
| `create_coding_project` | Structure complète projet + code + setup | Nouveaux projets |
| `create_coding_feature` | Génère feature avec tests | Nouvelles fonctionnalités |

### Git & Versioning

| Pattern | Description | Usage ATLAS |
|---------|-------------|-------------|
| `summarize_git_changes` | Résume changements des 7 derniers jours | Release notes |
| `summarize_git_diff` | Analyse les diffs Git | PR descriptions |
| `create_git_diff_commit` | Message de commit depuis diff | `/9-git-ship` |
| `write_pull-request` | Génère description PR complète | GitHub workflow |

### Architecture & Design

| Pattern | Description | Usage ATLAS |
|---------|-------------|-------------|
| `create_design_document` | Doc C4 complète (contexte, container, deployment) | Architecture |
| `create_prd` | Product Requirements Document | Specs fonctionnelles |
| `refine_design_document` | Améliore un design doc existant | Itération |

### Agile & Planning

| Pattern | Description | Usage ATLAS |
|---------|-------------|-------------|
| `create_user_story` | User stories formatées | Backlog |
| `agility_story` | Stories agiles complètes | Sprint planning |

### Prompts & AI

| Pattern | Description | Usage ATLAS |
|---------|-------------|-------------|
| `improve_prompt` | Améliore les prompts LLM | Agents ATLAS |
| `improve_writing` | Améliore clarté et style | Documentation |
| `create_pattern` | Crée un nouveau pattern Fabric | Étendre vos skills |

### Analyse

| Pattern | Description | Usage ATLAS |
|---------|-------------|-------------|
| `analyze_claims` | Évalue assertions critiquement | Review de specs |
| `analyze_logs` | Analyse de logs | Debugging |
| `analyze_paper` | Analyse articles techniques | Veille techno |
| `find_logical_fallacies` | Détecte erreurs logiques | Review de design |

### Sécurité

| Pattern | Description | Usage ATLAS |
|---------|-------------|-------------|
| `create_stride_threat_model` | STRIDE threat modeling | Architecture sécurité |
| `create_threat_scenarios` | Scénarios de menaces | Security review |
| `ask_secure_by_design_questions` | Questions sécurité | Design review |

### Visualisation

| Pattern | Description | Usage ATLAS |
|---------|-------------|-------------|
| `create_mermaid_visualization` | Diagrammes Mermaid | Architecture |
| `create_markmap_visualization` | Mind maps | Brainstorm |

---

## Comment ça marche (Mode Natif)

```
┌─────────────────────────────────────────────────────┐
│  Mode Natif (RECOMMANDÉ)                            │
│  User → Claude Code (lit pattern + applique)        │
│         ✅ Pas de clé API supplémentaire !          │
└─────────────────────────────────────────────────────┘
```

---

## Implementation

Quand ce skill est invoqué, suivre ces étapes :

### Étape 1 : Lire le Pattern

```bash
cat ~/.config/fabric/patterns/{pattern}/system.md
```

**Chemin des patterns** : `~/.config/fabric/patterns/`

Si le pattern n'existe pas :
```bash
ls ~/.config/fabric/patterns/ | grep -i "{pattern}"
```

### Étape 2 : Obtenir l'Input

- **Si fichier** : Lire avec l'outil Read
- **Si texte** : Utiliser directement
- **Si non spécifié** : Demander à l'utilisateur

### Étape 3 : Appliquer le Pattern

1. Lire le contenu de `system.md` du pattern
2. Suivre EXACTEMENT les instructions du pattern
3. Respecter le format de sortie spécifié
4. Respecter les contraintes (nombre de mots, sections, etc.)

### Étape 4 : Présenter les Résultats

Afficher la sortie dans le format exact demandé par le pattern.

---

## Exemples d'Usage

### Code Review avant commit

```yaml
skill: "zz-fabric"
pattern: "review_code"
input: "mon_fichier.py"
```

### Créer un PRD

```yaml
skill: "zz-fabric"
pattern: "create_prd"
input: "Description de mon idée de produit..."
```

### Design Document C4

```yaml
skill: "zz-fabric"
pattern: "create_design_document"
input: "Description du système à documenter..."
```

### Message de commit depuis diff

```yaml
skill: "zz-fabric"
pattern: "create_git_diff_commit"
input: "<output de git diff>"
```

### Améliorer un prompt d'agent

```yaml
skill: "zz-fabric"
pattern: "improve_prompt"
input: "Le prompt actuel de mon agent..."
```

### Threat Model STRIDE

```yaml
skill: "zz-fabric"
pattern: "create_stride_threat_model"
input: "Description de l'architecture..."
```

---

## Intégration ATLAS Workflows

### Avant `/9-git-ship`
```
pattern: review_code → Vérifier le code
pattern: create_git_diff_commit → Générer message de commit
```

### Nouveau projet
```
pattern: create_prd → Définir les requirements
pattern: create_design_document → Architecture C4
pattern: create_coding_project → Structure + code
```

### Sprint Planning
```
pattern: create_user_story → User stories
pattern: agility_story → Stories détaillées
```

### Améliorer ATLAS
```
pattern: improve_prompt → Améliorer agents
pattern: create_pattern → Nouveaux patterns custom
```

---

## Patterns Additionnels Disponibles

**234 patterns au total !** Voir la liste complète :
```bash
ls ~/.config/fabric/patterns/
```

Patterns notables non listés ci-dessus :
- `youtube_summary` - Résumer vidéos YouTube
- `analyze_incident` - Post-mortem
- `create_keynote` - Créer présentation
- `write_essay` - Rédiger essai
- `translate` - Traduction
- `humanize` - Rendre texte plus humain
- `clean_text` - Nettoyer texte

---

## Troubleshooting

### Pattern non trouvé
```bash
ls ~/.config/fabric/patterns/ | grep -i "keyword"
```

### Voir le contenu d'un pattern
```bash
cat ~/.config/fabric/patterns/{pattern}/system.md
```

### Mettre à jour les patterns
```bash
fabric --updatepatterns
```

---

## Références

- [Fabric GitHub](https://github.com/danielmiessler/fabric)
- [Patterns Directory](https://github.com/danielmiessler/fabric/tree/main/patterns)
- [Daniel Miessler Blog](https://danielmiessler.com/)
