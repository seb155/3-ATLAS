# Optimisation des Coûts - Atlas Framework

Guide complet pour comprendre et optimiser la consommation de tokens dans Atlas.

## Vue d'Ensemble

### Taille du Framework

| Catégorie | Fichiers | Lignes | Tokens (approx.) |
|-----------|----------|--------|------------------|
| Agents | 28 | 7,570 | 12,500 |
| Commands | 41 | 4,665 | 7,700 |
| Docs | 10 | 3,450 | 5,700 |
| Skills | 12 | 2,874 | 4,700 |
| Templates | 20+ | 2,664 | 4,400 |
| Rules | 11 | 2,423 | 4,000 |
| Context | 10 | 972 | 1,600 |
| Hooks | 6 | 156 | 260 |
| **TOTAL** | **138+** | **26,519** | **~43,700** |

> **Note**: Tu ne charges jamais tout! Le système lazy-load charge **3,700-6,600 tokens** par session.

---

## Prix API Claude (Décembre 2025)

| Modèle | Input/M | Output/M | Cache Read/M |
|--------|---------|----------|--------------|
| **Opus 4.5** | $5 | $25 | $0.50 |
| **Sonnet 4.5** | $3 | $15 | $0.50 |
| **Haiku 3.5** | $0.80 | $4 | $0.50 |

### Économies Possibles

- **Prompt Caching**: 90% réduction sur input ($5 → $0.50/M)
- **Batch Processing**: 50% réduction
- **Model Routing**: Haiku pour tâches simples = 85% économie vs Opus

---

## Coût par Type de Session

### Session Dev Standard (~10 interactions)

```
Chargement initial:
├── Base Framework (cached)    2,500 tokens  → $0.00125
├── ATLAS agent                  600 tokens  → $0.003
├── Commands                     300 tokens  → $0.0015
└── Context                      200 tokens  → $0.001
                               ─────────────────────────
                               3,600 tokens  → $0.006

Par interaction (moyenne):
├── Prompt utilisateur           200 tokens  → $0.001
├── Réponse Claude               800 tokens  → $0.02 (output)
└── Tool calls                   500 tokens  → $0.015
                               ─────────────────────────
                               1,500 tokens  → $0.036

TOTAL SESSION: ~$0.37
```

### Session Infrastructure

```
Chargement:
├── Base + DevOps Manager      4,700 tokens  → $0.024
├── Infrastructure rules       1,700 tokens  → $0.009
└── Docker/Network skills        500 tokens  → $0.003
                               ─────────────────────────
                               6,900 tokens  → $0.035

TOTAL SESSION (5 interactions): ~$0.40
```

### Session Workshop/Brainstorm

```
Chargement:
├── Base + Workshop Agent      3,220 tokens  → $0.016
├── Workshop templates         1,270 tokens  → $0.006
└── Workshop skill               540 tokens  → $0.003
                               ─────────────────────────
                               5,030 tokens  → $0.025

TOTAL SESSION (8 interactions): ~$0.51
```

---

## Estimation Mensuelle

### Workflow Typique

| Activité | Sessions/jour | Coût/session | Coût/jour |
|----------|---------------|--------------|-----------|
| Dev standard | 3 | $0.37 | $1.11 |
| Debug | 1 | $0.25 | $0.25 |
| Infrastructure | 0.3 | $0.40 | $0.12 |
| Brainstorm | 0.2 | $0.51 | $0.10 |
| Quick queries | 5 | $0.08 | $0.40 |
| **Total/jour** | - | - | **~$2.00** |

### Coût Mensuel

| État | Coût/mois |
|------|-----------|
| Sans optimisation | ~$62 |
| Avec Prompt Caching | ~$45 |
| Avec toutes optimisations | **~$35-40** |

---

## Fichiers par Type de Chargement

### Systématique (Toujours chargés) - 2,500 tokens

```
.claude/CLAUDE.md                           365 lignes   600 tokens
context/temporal.md                          21 lignes    35 tokens
context/environment.md                      141 lignes   230 tokens
context/project.md                           60 lignes   100 tokens
context/preferences.md                       55 lignes    90 tokens
agents/rules/response-protocol.md           254 lignes   420 tokens
agents/rules/session-management.md          205 lignes   340 tokens
agents/rules/workspace-navigation.md        228 lignes   380 tokens
settings.json                               173 lignes   280 tokens
```

### Conditionnel (Selon contexte) - 1,800-3,500 tokens

```
agents/atlas.md                             367 lignes   600 tokens
agents/orchestrators/genesis.md             403 lignes   680 tokens
agents/builders/*.md                        ~300 lignes  ~500 tokens
commands/0-session-*.md                     ~120 lignes  ~200 tokens
```

### À la demande (Quand invoqué) - 500-2,000 tokens

```
agents/devops-manager.md                    719 lignes  1,200 tokens
agents/rules/1*-*.md (infrastructure)     1,075 lignes  1,700 tokens
docs/*.md                                   ~350 lignes  ~580 tokens
templates/**/*.md                           ~130 lignes  ~220 tokens
```

---

## Top 10 Fichiers les Plus Coûteux

| Rang | Fichier | Tokens | Fréquence |
|------|---------|--------|-----------|
| 1 | `devops-manager.md` | 1,200 | Parfois |
| 2 | `infrastructure rules (3)` | 1,700 | Parfois |
| 3 | `genesis.md` | 680 | Souvent |
| 4 | `CLAUDE.md` | 600 | Toujours |
| 5 | `atlas.md` | 600 | Toujours |
| 6 | `environment-variables.md` | 830 | Rarement |
| 7 | `workshop-facilitator.md` | 720 | Parfois |
| 8 | `templates-reference.md` | 1,090 | Rarement |
| 9 | `response-protocol.md` | 420 | Toujours |
| 10 | `workspace-navigation.md` | 380 | Toujours |

---

## Stratégies d'Optimisation

### 1. Prompt Caching (90% économie sur input)

Les fichiers systématiques sont identiques chaque session.
Avec le cache, 2,500 tokens à $5/M deviennent $0.50/M.

**Économie**: ~$15-20/mois

Voir: [Prompt Caching](#prompt-caching-expliqué)

### 2. Lazy-Loading (20-30% économie)

Ne charger les fichiers lourds que quand nécessaire:
- DevOps Manager: seulement si infrastructure mentionnée
- Infrastructure rules: seulement si Docker/Traefik mentionné
- Workshop: seulement si `/1-start-brainstorm`

**Économie**: ~$5-10/mois

Voir: [Lazy-Loading](#lazy-loading-expliqué)

### 3. Model Routing (40-60% économie par tâche)

| Tâche | Modèle Recommandé | vs Opus |
|-------|-------------------|---------|
| CRUD, configs | Haiku | -85% |
| Code standard | Sonnet | -40% |
| Architecture | Opus | baseline |

**Économie**: ~$10-15/mois

### 4. Index Légers (5-10% économie)

Créer des index JSON pour docs/templates au lieu de charger le contenu complet.

**Économie**: ~$3-5/mois

---

## Commandes de Monitoring

```bash
/0-tokens          # Dashboard tokens (Input/Output/Cache)
/0-analyze         # Analyse patterns d'utilisation
/0-cost-report     # Rapport de coûts (à implémenter)
```

---

---

## Prompt Caching - Expliqué

### Le Problème

À chaque message, Claude reçoit TOUT le contexte (system prompt, CLAUDE.md, rules, etc.).
Si tu envoies 50 messages/jour avec 3,000 tokens de contexte identique, tu paies 150,000 tokens d'input... pour la même chose répétée 50 fois!

### La Solution

Prompt Caching permet à Anthropic de "mémoriser" les parties statiques du prompt.
Tu paies le prix plein une fois, puis **90% moins cher** pour les réutilisations.

### Comparaison

```
SANS CACHE (10 messages):
├── Contexte statique: 3,600 tokens × 10 = 36,000 tokens
├── Messages variables: 2,000 tokens
├── Coût: 38,000 × $5/M = $0.19
└── Total: $0.19

AVEC CACHE (10 messages):
├── Cache write (1x): 3,600 tokens × $6.25/M = $0.023
├── Cache read (9x): 3,600 × 9 × $0.50/M = $0.016
├── Messages variables: 2,000 × $5/M = $0.01
└── Total: $0.049

ÉCONOMIE: 74%
```

### Comment Maximiser le Cache

1. **Garder le contexte stable** - Ne pas modifier CLAUDE.md/rules fréquemment
2. **Grouper les fichiers statiques** - Au début du contexte
3. **Sessions longues** - Plus de messages = plus de cache hits
4. **Éviter les modifications dynamiques** - temporal.md 1x/session suffit

### Ce qui est Caché Automatiquement

- System prompt de Claude Code
- Contenu de CLAUDE.md
- Rules chargées
- Context files stables

---

## Lazy-Loading - Expliqué

### Le Problème

Si Atlas charge TOUS ses 43,700 tokens au démarrage, chaque session coûterait $0.22 juste pour le contexte! Et 80% de ce contenu ne serait jamais utilisé.

### La Solution

Lazy-loading = charger les fichiers **seulement quand ils sont nécessaires**.
Le DevOps Manager (1,200 tokens) n'est chargé que si tu parles d'infrastructure.

### Comparaison

```
CHARGEMENT EAGER (tout):
├── Tous les fichiers: 26,400 tokens
├── Coût: $0.132
└── Utilisation: ~15%

CHARGEMENT LAZY (à la demande):
├── Base minimale: 3,100 tokens
├── + Fichiers nécessaires: ~1,500 tokens
├── Coût: $0.023
└── Utilisation: ~90%

ÉCONOMIE: 83%
```

### Triggers de Chargement dans Atlas

| Contexte Détecté | Fichiers Chargés |
|------------------|------------------|
| Défaut | CLAUDE.md, rules essentielles, ATLAS agent |
| "docker", "traefik", "deploy" | + DevOps Manager, infrastructure rules |
| `/1-start-brainstorm` | + Workshop Facilitator, templates |
| "error", "bug", "debug" | + Debugger agent |
| "react", "component" | + Frontend Builder |
| "API", "endpoint" | + Backend Builder |
| "test", "pytest" | + QA Tester agent |

### Comment Atlas Implémente le Lazy-Loading

**1. Agents via Task tool**
```
Task(subagent_type="backend-builder")
→ Charge SEULEMENT backend.md (500 tokens)
→ Pas les 27 autres agents
```

**2. Commands à la demande**
```
/0-session-start
→ Charge SEULEMENT 0-session-start.md (~200 tokens)
→ Pas les 40 autres commands
```

**3. Rules conditionnelles**
```
Mention de "traefik"
→ Charge 10-traefik-routing.md (440 tokens)
→ Sinon: jamais chargé
```

---

## Résumé des Économies

| Optimisation | Mécanisme | Économie |
|--------------|-----------|----------|
| **Prompt Caching** | Réutiliser contexte statique | 70-90% sur input répété |
| **Lazy-Loading** | Charger à la demande | 60-80% sur contexte |
| **Model Routing** | Haiku/Sonnet pour tâches simples | 40-85% par tâche |
| **Batch Processing** | Grouper les requêtes | 50% |

### Coût Mensuel Comparé

| Configuration | Coût/mois |
|---------------|-----------|
| Sans optimisation | ~$80-100 |
| Lazy-loading seul | ~$60-70 |
| + Prompt Caching | ~$40-50 |
| + Model Routing | ~$30-40 |
| **Optimisé complet** | **~$25-35** |

---

## Implémentation Status

### ✅ Phase 1: Cache Optimization (DONE)

CLAUDE.md restructuré avec séparation statique/dynamique:
- **Section Statique** (lignes 1-287): ~1500 tokens - Contenu stable, caché automatiquement
- **Section Dynamique** (lignes 288-fin): ~450 tokens - OK de modifier

Fichiers créés:
- `CLAUDE-static.md` - Référence du contenu stable
- `CLAUDE-dynamic.md` - Référence du contenu variable
- `CLAUDE.md.backup` - Backup avant restructuration

**Impact estimé**: 30-40% réduction sur coûts input répétés

---

### 📋 Phase 2: Rule Registry (À FAIRE)

Charger uniquement les règles pertinentes au contexte de session.

```
Fichiers à créer:
├── agents/rules/index.json     # Mapping session-type → rules
└── scripts/load-rules.sh       # Script de chargement conditionnel

Fichiers à modifier:
├── hooks/SessionStart.sh       # Détection session type
└── agents/atlas.md             # Triggers de chargement
```

**Impact estimé**: +20-30% réduction supplémentaire

---

### 📋 Phase 3: Hot Files Optimization (À FAIRE)

Utiliser le tracking de fréquence pour prioriser le chargement.

```
Fichiers à modifier:
├── context/hot-files.json      # Activer auto_load_top_n
└── scripts/load-context.sh     # Créer script intelligent
```

**Impact estimé**: +10-15% réduction supplémentaire

---

### 📋 Phase 4: Agent Splitting (À FAIRE)

Diviser les gros agents en base + extensions chargeables.

```
Transformation:
agents/devops-manager.md (719 lignes)
    ↓
agents/devops-manager/
├── base.md         # Core (~200 lignes)
├── docker.md       # Docker specifics
├── traefik.md      # Routing specifics
└── networking.md   # Network config
```

**Impact estimé**: +15-20% réduction supplémentaire

---

## Références

- [Claude Pricing](https://www.claude.com/pricing)
- [Prompt Caching Docs](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- [Token Monitoring](./token-monitoring.md)
- [Plan complet](~/.claude/plans/sequential-booping-wind.md)
