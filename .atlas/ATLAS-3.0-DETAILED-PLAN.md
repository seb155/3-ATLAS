# ATLAS 3.0 - Plan de Développement Complet

**Créé:** 2025-12-04
**Auteur:** Claude + Seb
**Statut:** PLANIFICATION
**Cible:** Q1 2025 (8 semaines)

---

## Vision Exécutive

ATLAS 3.0 est une réécriture complète du framework d'orchestration AI, basée sur **PAI (Personal AI Infrastructure)** de Daniel Miessler et intégrant le **Miessler Suite** complet (Fabric, Telos, Substrate, Daemon, SecLists).

### Objectifs Principaux

| Objectif | Métrique | Cible |
|----------|----------|-------|
| Réduction coûts tokens | % économie vs v2.x | 35-50% |
| Simplification UX | Nombre de commandes | 47 → 12 |
| Extensibilité | Système de skills | 3-tier (CORE/Domain/Custom) |
| Migration | Temps par projet | < 30 minutes |

---

## 1. Architecture Cible

### 1.1 Structure des Répertoires

```
project/
├── .atlas/                              # ATLAS 3.0 Core
│   ├── VERSION                          # "3.0.0"
│   ├── atlas.config.json                # Configuration unifiée
│   ├── CONSTITUTION.md                  # Philosophie PAI
│   │
│   ├── core/                            # PAI FOUNDATION (vendored)
│   │   ├── skills/                      # Système Skills 3-tier
│   │   │   ├── CORE/                    # Tier 1: PAI core (immutable)
│   │   │   │   ├── SKILL.md
│   │   │   │   └── SkillSystem.md
│   │   │   ├── observability/
│   │   │   └── research/
│   │   │
│   │   ├── hooks/                       # Système Hooks
│   │   │   ├── PreToolUse/
│   │   │   ├── PostToolUse/
│   │   │   └── UserFeedback/
│   │   │
│   │   ├── history/                     # UOCS History
│   │   │   ├── sessions/
│   │   │   └── logs/
│   │   │
│   │   └── personas/                    # Agent Personalities
│   │
│   ├── integrations/                    # MIESSLER SUITE
│   │   ├── fabric/
│   │   │   ├── config.yml
│   │   │   ├── patterns/                # 242+ patterns (vendored)
│   │   │   └── custom/                  # Patterns personnalisés
│   │   │
│   │   ├── telos/
│   │   │   ├── templates/               # Corporate, Personal TCFs
│   │   │   └── contexts/                # Project TCFs
│   │   │
│   │   ├── substrate/
│   │   │   ├── schema.json
│   │   │   ├── templates/               # 17 types de composants
│   │   │   └── knowledge/               # Problems, Solutions, Data
│   │   │
│   │   ├── daemon/                      # MCP Server (optional)
│   │   │   └── daemon.md
│   │   │
│   │   └── seclists/                    # Security wordlists (ref only)
│   │       └── config.yml               # Points to ~/.cache/seclists
│   │
│   ├── extensions/                      # ATLAS-SPECIFIC
│   │   ├── sessions/                    # Session management (from v2)
│   │   ├── routing/                     # Model routing engine
│   │   ├── layering/                    # Project override system
│   │   └── multiproject/                # Cross-project support
│   │
│   ├── upstream/                        # VENDOR MANAGEMENT
│   │   ├── README.md                    # "SYNC REQUIRES EXPLICIT APPROVAL"
│   │   ├── SYNC_LOG.md
│   │   ├── check-updates.sh
│   │   └── approve-sync.sh
│   │
│   └── tools/
│       ├── setup/bootstrap.sh
│       ├── platform/detect.sh
│       └── migrate/v2-to-v3.sh
│
├── .claude/                             # Claude Code interface (minimal)
│   ├── CLAUDE.md                        # Instructions générées (~600 tokens)
│   ├── settings.json
│   └── commands/                        # 12 commandes simplifiées
│
└── .dev/                                # Contexte projet (inchangé)
    ├── 0-backlog/
    ├── 1-sessions/
    ├── context/
    └── journal/
```

### 1.2 Système de Skills 3-Tier

```
Requête utilisateur: "summarize this document"
        │
        ▼
┌──────────────────────────────────────────────────┐
│  TIER 1: CORE SKILLS (.atlas/core/skills/CORE/)  │
│  - SkillSystem.md - Meta-skill                   │
│  - SKILL.md - Création/invocation                │
│  Status: VERROUILLÉ (vendored PAI)               │
└──────────────────────────────────────────────────┘
        │ Non trouvé?
        ▼
┌──────────────────────────────────────────────────┐
│  TIER 2: DOMAIN SKILLS (integrations/fabric/)    │
│  - summarize/system.md                           │
│  - extract_wisdom/system.md                      │
│  - 240+ autres patterns                          │
│  Status: VENDORED (sync périodique)              │
└──────────────────────────────────────────────────┘
        │ Non trouvé?
        ▼
┌──────────────────────────────────────────────────┐
│  TIER 3: CUSTOM SKILLS                           │
│  - .atlas/extensions/ - Skills ATLAS             │
│  - integrations/fabric/custom/                   │
│  - project/.atlas/local/skills/                  │
│  Status: ÉDITABLE (créé par utilisateur)         │
└──────────────────────────────────────────────────┘
```

### 1.3 Configuration Unifiée

```json
{
  "$schema": "atlas-config-v3",
  "version": "3.0.0",

  "project": {
    "id": "my-project",
    "type": "standalone|parent|child"
  },

  "core": {
    "pai_version": "1.0.0",
    "skills": { "tiers": ["core", "domain", "custom"] },
    "hooks": { "enabled": true },
    "history": { "format": "uocs" }
  },

  "integrations": {
    "fabric": { "enabled": true, "auto_sync": false },
    "telos": { "enabled": true },
    "substrate": { "enabled": false },
    "daemon": { "enabled": false },
    "seclists": { "enabled": false }
  },

  "extensions": {
    "sessions": { "enabled": true, "checkpoint_threshold": 70 },
    "routing": { "enabled": true, "default_model": "sonnet" },
    "layering": { "enabled": true, "mode": "merge" }
  },

  "tokens": {
    "budget": { "session_max": 100000, "alert_threshold": 70 },
    "optimization": { "edit_over_write": true, "lazy_loading": true }
  }
}
```

---

## 2. Intégration Miessler Suite

### 2.1 PAI (Personal AI Infrastructure)

| Composant | Source | Intégration |
|-----------|--------|-------------|
| Skills System | `.claude/skills/` | Full vendor → `.atlas/core/skills/` |
| Hooks System | `.claude/hooks/` | Full vendor → `.atlas/core/hooks/` |
| UOCS History | Sessions/Logs | Full vendor → `.atlas/core/history/` |
| Voice Server | ElevenLabs | Optional (defer to Phase 5) |

### 2.2 Fabric (242+ Patterns)

**Pattern comme Skill:**
```
patterns/summarize/      → skill: fabric:summarize
patterns/extract_wisdom/ → skill: fabric:extract_wisdom
custom/axiom_review/     → skill: fabric:custom:axiom_review
```

**Fabric Bridge Skill:** Lit `system.md` du pattern et l'applique comme system prompt.

### 2.3 Telos (Purpose Documentation)

**TCF (Telos Context Files):**
- `corporate_telos.md` - Template entreprise
- `personal_telos.md` - Template personnel
- `atlas.telos.md` - Purpose ATLAS 3.0
- `synapse.telos.md` - Purpose SYNAPSE

### 2.4 Substrate (Knowledge Base)

**17+ types de composants:**
- `Problems/` - Problèmes documentés
- `Solutions/` - Solutions prouvées
- `Arguments/` - Chaînes de raisonnement
- `Claims/` - Assertions vérifiables
- `Data-Sources/` - Sources de données cataloguées

### 2.5 Daemon (Public API)

**MCP Server exposant:**
- Données daemon personnelles
- Calendrier/disponibilités
- Préférences de communication

### 2.6 SecLists (Security Testing)

**Référence externe seulement (7-8 GB trop large):**
```yaml
seclists:
  path: "~/.cache/seclists"
  repo: "https://github.com/danielmiessler/SecLists"
```

---

## 3. Optimisation des Coûts

### 3.1 Réduction des Commandes (47 → 12)

| Catégorie | v2.x | v3.0 | Économie |
|-----------|------|------|----------|
| Session | 7 commandes | `/session` | 6 fichiers |
| View | 4 commandes | `/view` | 3 fichiers |
| Init | 4 commandes | `/init` | 3 fichiers |
| Dev | 3 commandes | `/dev` | 2 fichiers |
| Git | 3 commandes | `/ship` | 2 fichiers |
| Tokens | 4 commandes | `/cost` | 3 fichiers |
| Standard | 13 commandes | Smart routing | 13 fichiers |
| **TOTAL** | **47** | **12** | **74% réduction** |

### 3.2 Lazy Loading

**Chargement au démarrage (~985 tokens):**
```
CLAUDE.md (slim)         600 tokens
temporal.md               35 tokens
project.md               100 tokens
routing-index.json        50 tokens
active-session.json      200 tokens
```

**Chargement à la demande:**
```
agents/*.md              → Seulement quand Task spawn
commands/*.md            → Seulement quand /command invoqué
rules/*.md               → Seulement quand trigger détecté
skills/*.md              → Seulement quand skill invoqué
```

### 3.3 Agent Optimization (3 modes)

| Mode | Tokens | Cas d'usage |
|------|--------|-------------|
| **Lite** | 50-100 | Tâches simples, routing |
| **Standard** | 200-400 | Opérations normales |
| **Expert** | 500-1200 | Tâches complexes |

### 3.4 Model Routing

**Distribution cible:**
- 60% Haiku ($0.80/M) - Simple CRUD, configs, docs
- 30% Sonnet ($3.00/M) - Code, planning, debugging
- 10% Opus ($5.00/M) - Architecture, multi-système

### 3.5 Économies Attendues

| Initiative | Conservative | Aggressive |
|------------|-------------|------------|
| Lazy Loading | 20% | 30% |
| Consolidation Commandes | 10% | 15% |
| Agent Optimization | 15% | 25% |
| Tool Optimization | 10% | 15% |
| **TOTAL** | **35%** | **50%** |

---

## 4. Stratégie de Repositories

### 4.1 État Cible

```
GitHub Repositories:
│
├── seb155/2-ATLAS                    # PRODUCTION (stable)
│   ├── Renommé depuis atlas-framework
│   └── ATLAS 2.x (maintenance only)
│
├── seb155/3-ATLAS                    # DEVELOPMENT (actif)
│   ├── Fork de 2-ATLAS
│   ├── ATLAS 3.0 development
│   └── PAI + Miessler Suite
│
├── seb155/Personal_AI_Infrastructure # UPSTREAM FORK
│   ├── Fork de danielmiessler/PAI
│   └── Tracking upstream (manual sync)
│
└── seb155/fabric                     # UPSTREAM FORK
    ├── Fork de danielmiessler/fabric
    └── Tracking upstream (manual sync)
```

### 4.2 Politique de Sync

**RÈGLES CRITIQUES:**
1. NO automatic sync - Tous les changements upstream nécessitent approbation explicite
2. Check monthly - `./upstream/check-updates.sh`
3. Review avant sync - Examiner les changements
4. Log all syncs - `SYNC_LOG.md`

```bash
# Workflow de sync
./upstream/check-updates.sh           # Vérifier nouveautés
./upstream/check-updates.sh --diff pai # Voir les changements
./upstream/request-sync.sh pai         # Créer requête (optionnel)
./upstream/approve-sync.sh pai         # APPROBATION REQUISE
```

---

## 5. Phases de Développement

### Phase 0: Setup Repositories (2 jours)

| Tâche | Effort | Livrable |
|-------|--------|----------|
| Renommer `atlas-framework` → `2-ATLAS` | 30 min | Repo renommé |
| Fork `2-ATLAS` → `3-ATLAS` | 15 min | Fork créé |
| Fork `danielmiessler/PAI` | 15 min | Upstream tracking |
| Fork `danielmiessler/fabric` | 15 min | Upstream tracking |
| Setup WSL2 instance "ATLAS3-Dev" | 2h | Environnement dev |
| Clone et config | 1h | Dev prêt |

**Go/No-Go:** Tous les repos accessibles, WSL2 fonctionnel

---

### Phase 1: PAI Core (1 semaine)

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Créer structure `.atlas/` | 2h | P1 |
| Vendor PAI core (skills, hooks, history) | 4h | P1 |
| Implémenter 3-tier Skills system | 8h | P1 |
| Implémenter Hooks system | 6h | P1 |
| Implémenter UOCS History | 4h | P2 |
| Créer schema config unifié | 4h | P1 |
| Script bootstrap | 2h | P2 |
| Tests unitaires | 8h | P1 |

**Go/No-Go:** Skills invocables, Hooks fonctionnels, Config chargée

---

### Phase 2: Miessler Suite (1 semaine)

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Vendor Fabric patterns (242+) | 4h | P1 |
| Créer Fabric bridge skill | 6h | P1 |
| Setup Telos templates | 3h | P2 |
| Créer structure Substrate | 4h | P2 |
| Config Daemon (optional) | 2h | P3 |
| Config SecLists reference | 1h | P3 |
| Tests d'intégration | 8h | P1 |

**Go/No-Go:** `fabric:summarize` fonctionne, Telos chargé au démarrage

---

### Phase 3: Extensions ATLAS (1 semaine)

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Porter session management | 8h | P1 |
| Porter model routing engine | 6h | P1 |
| Porter layering system | 6h | P2 |
| Porter multi-project support | 4h | P2 |
| Créer 12 commandes simplifiées | 8h | P1 |
| Porter response protocol | 4h | P1 |
| Tests | 8h | P1 |

**Go/No-Go:** `/session`, `/dev`, `/ship` fonctionnels

---

### Phase 4: Cost Optimization (1 semaine)

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Token attribution system | 3 jours | P1 |
| Lazy loading manifest | 1 jour | P1 |
| Agent skeleton system | 2 jours | P1 |
| Model routing optimizer | 2 jours | P2 |
| Edit/Write enforcement hook | 1 jour | P2 |

**Go/No-Go:** Métriques de coût visibles, Startup < 1000 tokens

---

### Phase 5: Platform & Testing (1 semaine)

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Script détection plateforme | 4h | P1 |
| Support WSL2/Linux/macOS | 8h | P1 |
| One-liner installer | 4h | P1 |
| Suite de tests complète | 8h | P1 |
| Tests cross-platform | 8h | P1 |

**Go/No-Go:** Installation réussie sur fresh WSL2

---

### Phase 6: Migration & Documentation (1 semaine)

| Tâche | Effort | Priorité |
|-------|--------|----------|
| Script migration v2→v3 | 6h | P1 |
| Guide utilisateur | 8h | P1 |
| Guide migration | 6h | P1 |
| API documentation | 4h | P2 |
| README files | 4h | P1 |
| CHANGELOG | 2h | P1 |

**Go/No-Go:** Migration ATLAS project réussie en < 30 min

---

### Phase 7: Beta & Release (2 semaines)

| Semaine | Activité | Scope |
|---------|----------|-------|
| S7 | Alpha testing | ATLAS project seul |
| S7 | Beta 1 | + CORTEX, NEXUS |
| S8 | Beta 2 | + ECHO, SYNAPSE |
| S8 | RC + Release | Full AXIOM |

**Rollout Order (par risque):**
1. Test project (aucun risque)
2. ATLAS (low risk, self-contained)
3. CORTEX (low risk, smaller scope)
4. NEXUS (medium risk, active dev)
5. ECHO (medium risk, desktop app)
6. SYNAPSE (high risk, production)
7. APEX (high risk, enterprise)
8. FORGE (low risk, infrastructure)

---

## 6. Mapping Commandes v2 → v3

| v2.x | v3.0 | Notes |
|------|------|-------|
| `/0-session-start` | `/session start` | Fusionné |
| `/0-session-continue` | `/session continue` | Fusionné |
| `/0-session-recover` | `/session recover` | Fusionné |
| `/1-start-dev` | `/dev` | Simplifié |
| `/1-start-brainstorm` | `/brainstorm` | Simplifié |
| `/0-view-status` | `/view status` | Fusionné |
| `/0-view-roadmap` | `/view roadmap` | Fusionné |
| `/9-git-ship` | `/ship` | Simplifié |
| `/0-tokens` | `/cost` | Renommé |
| `/architect` | `fabric:create_design_document` | Via Fabric |
| `/docs` | `fabric:improve_writing` | Via Fabric |
| `/debug` | `/dev --debug` | Flag mode |

---

## 7. Risques et Mitigation

### 7.1 Breaking Changes

| Changement | Impact | Mitigation |
|------------|--------|------------|
| Noms de commandes | Scripts cassés | Fichier d'alias |
| Format sessions | Historique perdu | Script migration |
| Location config | Update manuel | Documentation claire |
| Noms agents | Références cassées | Document mapping |

### 7.2 Rollback Procedure

```bash
#!/bin/bash
# rollback-to-v2.sh
if [ ! -d ".claude.v2.backup" ]; then
    echo "No v2 backup found!"
    exit 1
fi
rm -rf .claude .atlas
mv .claude.v2.backup .claude
echo "Rolled back to v2"
```

### 7.3 Critères de Succès

**Fonctionnel:**
- [ ] Toutes les commandes v2 essentielles fonctionnent en v3
- [ ] Continuité des sessions maintenue
- [ ] Pas de perte de données
- [ ] Performance égale ou meilleure

**UX:**
- [ ] Setup < 10 minutes
- [ ] Migration < 30 minutes/projet
- [ ] Courbe d'apprentissage < 1 jour

---

## 8. Fichiers Critiques

### À Créer

| Fichier | Purpose | Priorité |
|---------|---------|----------|
| `.atlas/atlas.config.json` | Configuration unifiée | P1 |
| `.atlas/core/skills/CORE/SKILL.md` | PAI skill system | P1 |
| `.atlas/integrations/fabric/bridge.md` | Fabric executor | P1 |
| `.atlas/extensions/sessions/manager.md` | Session lifecycle | P1 |
| `.atlas/tools/migrate/v2-to-v3.sh` | Script migration | P1 |
| `.atlas/upstream/check-updates.sh` | Sync checker | P2 |
| `.claude/CLAUDE.md` | Instructions slim (~600 tokens) | P1 |

### À Référencer (Existants)

| Fichier | Purpose |
|---------|---------|
| `/home/seb/projects/ATLAS/.atlas/ATLAS-3.0-DEVELOPMENT-PLAN.md` | Plan existant (base) |
| `/home/seb/projects/ATLAS/.claude/CLAUDE.md` | Instructions v2 (à slim) |
| `/home/seb/projects/ATLAS/.claude/agents/atlas.md` | Orchestrateur (rewrite) |
| `/home/seb/projects/ATLAS/.dev/.dev-manifest.json` | Manifest projet |

---

## 9. Timeline Résumé

```
Semaine 1:  ████████ Phase 0-1: Repos + PAI Core
Semaine 2:  ████████ Phase 2: Miessler Suite
Semaine 3:  ████████ Phase 3: Extensions ATLAS
Semaine 4:  ████████ Phase 4: Cost Optimization
Semaine 5:  ████████ Phase 5: Platform & Testing
Semaine 6:  ████████ Phase 6: Migration & Docs
Semaine 7:  ████████ Phase 7a: Alpha + Beta 1
Semaine 8:  ████████ Phase 7b: Beta 2 + Release
```

**Total:** 8 semaines
**Effort estimé:** 200-250 heures

---

## 10. Prochaines Actions

1. **Immédiat:** Renommer `atlas-framework` → `2-ATLAS` sur GitHub
2. **Jour 1:** Fork 3-ATLAS et upstream repos
3. **Jour 2:** Setup WSL2 ATLAS3-Dev
4. **Semaine 1:** Phase 1 PAI Core integration

---

## 11. Analyse de Gap - Fonctionnalités Miessler Non Couvertes

### 11.1 PAI - Fonctionnalités à Intégrer

| Fonctionnalité | Description | Phase | Priorité |
|----------------|-------------|-------|----------|
| **BrightData 4-tier scraping** | Fallback progressif: WebFetch → cURL → Playwright → Bright Data MCP | Phase 5 | P2 |
| **CreateSkill meta-skill** | Génère nouveaux skills automatiquement | Phase 1 | P1 |
| **CreateCLI meta-skill** | Génère nouveaux CLI tools | Phase 3 | P2 |
| **pai-paths.ts** | Bibliothèque centralisée résolution chemins (TypeScript) | Phase 1 | P1 |
| **Protection manifest** | `.pai-protected.json` pour bloquer modification fichiers critiques | Phase 1 | P1 |
| **Security obfuscation** | Masquage données sensibles dans observability dashboard | Phase 5 | P2 |
| **Voice notifications** | ElevenLabs TTS au démarrage session | Phase 5+ | P3 |
| **Art Skill** | Génération contenu visuel (DALL-E, Midjourney prompts) | Phase 5+ | P3 |
| **Observability Themes** | Tokyo Night, Nord, Catppuccin | Phase 5+ | P3 |

### 11.2 Fabric - Fonctionnalités à Intégrer

| Fonctionnalité | Description | Phase | Priorité |
|----------------|-------------|-------|----------|
| **248+ patterns** | Nombre corrigé (pas 242) | Phase 2 | P1 |
| **Per-pattern model mapping** | `FABRIC_MODEL_PATTERN_NAME=vendor|model` pour routing intelligent | Phase 2 | P1 |
| **REST API server** | Flag `--serve` pour exposer patterns via API | Phase 3 | P2 |
| **YouTube integration** | yt-dlp pour extraction transcripts | Phase 2 | P2 |
| **Speech-to-text** | Whisper pour transcription audio/vidéo | Phase 5 | P2 |
| **HTML concept maps** | Cartes conceptuelles interactives | Phase 5 | P2 |
| **Desktop notifications** | Alertes système natives | Phase 5+ | P3 |
| **AI changelog** | Génération automatique changelog | Phase 5+ | P3 |

### 11.3 Substrate - Fonctionnalités à Intégrer

| Fonctionnalité | Description | Phase | Priorité |
|----------------|-------------|-------|----------|
| **8-dimension evaluation** | Authority, Currency, Objectivity, Accuracy, Methodology, Coverage, Reliability, Provenance | Phase 2 | P2 |
| **Argument Quality Scoring** | Score automatique chaînes de raisonnement | Phase 5 | P2 |
| **Dual consumption format** | Markdown/CSV human-readable + machine-parseable | Phase 2 | P1 |
| **Knowledge graph generation** | AI génère graphes de connaissances automatiquement | Phase 5 | P2 |
| **13+ data sources** | GDP, Inflation, Health, Wellbeing datasets | Phase 5+ | P3 |

### 11.4 Actions Correctives par Phase

**Phase 1 (PAI Core) - Ajouts:**
- Intégrer `CreateSkill` meta-skill
- Implémenter `pai-paths.ts` équivalent
- Créer `.atlas-protected.json` manifest

**Phase 2 (Miessler Suite) - Ajouts:**
- Corriger à 248+ patterns Fabric
- Implémenter per-pattern model mapping
- Ajouter YouTube transcript extraction
- Créer format dual-consumption pour Substrate
- Ajouter 8-dimension evaluation schema

**Phase 3 (Extensions) - Ajouts:**
- REST API server mode pour Fabric patterns
- CreateCLI meta-skill

**Phase 5 (Future) - Ajouts:**
- BrightData 4-tier scraping
- Speech-to-text (Whisper)
- HTML concept maps
- Security obfuscation
- Argument quality scoring
- Knowledge graph generation

**Phase 5+ (Post-Launch) - Ajouts:**
- Voice server (ElevenLabs)
- Art skill
- Desktop notifications
- AI changelog
- 13+ data sources

---

## 12. Checklist Complète Miessler Suite

### PAI Integration Checklist

- [ ] Skills System (3-tier)
- [ ] Hooks System (7 types)
- [ ] UOCS History
- [ ] CreateSkill meta-skill
- [ ] CreateCLI meta-skill
- [ ] pai-paths.ts equivalent
- [ ] Protection manifest
- [ ] Bootstrap wizard
- [ ] Observability dashboard
- [ ] Voice server (optional)
- [ ] BrightData scraping (optional)

### Fabric Integration Checklist

- [ ] 248+ patterns vendored
- [ ] Fabric bridge skill
- [ ] Per-pattern model mapping
- [ ] Custom patterns directory
- [ ] YouTube transcript extraction
- [ ] REST API server mode
- [ ] Speech-to-text (optional)
- [ ] HTML concept maps (optional)

### Telos Integration Checklist

- [ ] Corporate TCF template
- [ ] Personal TCF template
- [ ] Project TCF structure
- [ ] Atlas.telos.md

### Substrate Integration Checklist

- [ ] 17+ component types
- [ ] Problems/Solutions structure
- [ ] Arguments/Claims structure
- [ ] 8-dimension evaluation schema
- [ ] Dual consumption format
- [ ] Data sources config
- [ ] Knowledge graph (optional)

### Daemon Integration Checklist

- [ ] daemon.md template
- [ ] MCP server config
- [ ] API endpoints (optional)

### SecLists Integration Checklist

- [ ] External reference config
- [ ] Cache path setup
- [ ] Security testing patterns (optional)

---

*Plan généré le 2025-12-04*
*Basé sur: PAI, Fabric, Telos, Substrate, Daemon, SecLists de Daniel Miessler*
*Analyse de gap complète effectuée*
