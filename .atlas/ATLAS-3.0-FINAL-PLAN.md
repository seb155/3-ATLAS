# ATLAS 3.0 - Plan de Développement Final

**Créé:** 2025-12-04
**Auteur:** Claude + Seb
**Statut:** APPROUVÉ - EN COURS
**Cible:** Q1 2025 (8 semaines)
**Source:** `/home/seb/.claude/plans/silly-booping-wave.md`

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

## Quick Reference

### Repositories Cibles

```
seb155/2-ATLAS                    # PRODUCTION (stable v2.x)
seb155/3-ATLAS                    # DEVELOPMENT (v3.0)
seb155/Personal_AI_Infrastructure # UPSTREAM FORK
seb155/fabric                     # UPSTREAM FORK
```

### Timeline

```
Semaine 1:  Phase 0-1: Repos + PAI Core
Semaine 2:  Phase 2: Miessler Suite (248+ patterns)
Semaine 3:  Phase 3: Extensions ATLAS
Semaine 4:  Phase 4: Cost Optimization
Semaine 5:  Phase 5: Platform & Testing
Semaine 6:  Phase 6: Migration & Docs
Semaine 7:  Phase 7a: Alpha + Beta 1
Semaine 8:  Phase 7b: Beta 2 + Release
```

### Économies Attendues

| Initiative | Économie |
|------------|----------|
| Lazy Loading | 20-30% |
| Consolidation Commandes (47→12) | 10-15% |
| Agent Optimization (3 modes) | 15-25% |
| Tool Optimization | 10-15% |
| **TOTAL** | **35-50%** |

---

## Phase 0: Actions Immédiates

### GitHub Actions (Manuelles)

1. **Renommer atlas-framework → 2-ATLAS**
   - GitHub → Settings → Repository name
   - URL: https://github.com/seb155/atlas-framework/settings

2. **Fork 2-ATLAS → 3-ATLAS**
   - Après rename, cliquer Fork
   - Nom: 3-ATLAS

3. **Fork Miessler repos**
   - https://github.com/danielmiessler/Personal_AI_Infrastructure → Fork
   - https://github.com/danielmiessler/fabric → Fork

### WSL2 Setup

```powershell
# PowerShell (Admin)
wsl --install -d Ubuntu-24.04
```

```bash
# Inside WSL2
sudo apt update && sudo apt install -y git curl wget python3 nodejs npm
curl -fsSL https://bun.sh/install | bash
npm install -g @anthropic-ai/claude-code
git clone https://github.com/seb155/3-ATLAS.git ~/ATLAS-3
```

---

## Structure Cible v3.0

```
.atlas/
├── VERSION                    # "3.0.0"
├── atlas.config.json          # Config unifiée
├── CONSTITUTION.md            # Philosophie PAI
├── core/
│   ├── skills/CORE/           # Tier 1: PAI (immutable)
│   ├── hooks/                 # 7 types
│   └── history/               # UOCS
├── integrations/
│   ├── fabric/patterns/       # 248+ patterns
│   ├── telos/templates/       # TCF files
│   ├── substrate/knowledge/   # 17+ types
│   ├── daemon/                # MCP (optional)
│   └── seclists/              # Config only
├── extensions/
│   ├── sessions/              # From v2
│   ├── routing/               # Model routing
│   └── layering/              # Override system
└── upstream/
    ├── check-updates.sh
    └── SYNC_LOG.md
```

---

## Checklist Phase 0

- [ ] Renommer atlas-framework → 2-ATLAS
- [ ] Fork 2-ATLAS → 3-ATLAS
- [ ] Fork danielmiessler/Personal_AI_Infrastructure
- [ ] Fork danielmiessler/fabric
- [ ] Setup WSL2 ATLAS3-Dev
- [ ] Clone 3-ATLAS dans WSL2

---

## Document Complet

Le plan détaillé complet (716 lignes) est disponible dans:
- `/home/seb/.claude/plans/silly-booping-wave.md`

Contient:
- Architecture détaillée (structure, 3-tier skills, config)
- Intégration Miessler Suite (6 projets)
- Optimisation des coûts (commandes, lazy loading, agents)
- Stratégie repositories (fork, sync policy)
- 7 phases de développement avec Go/No-Go
- Mapping commandes v2 → v3
- Risques et mitigation
- Analyse de gap (fonctionnalités manquantes)
- Checklists complètes

---

*Plan approuvé le 2025-12-04*
