# ATLAS Development

Ce dossier contient le **développement** du système ATLAS lui-même.

## Distinction importante

| Mode | Dossier | Usage |
|------|---------|-------|
| **ATLAS (Dev)** | `.atlas/` | Construire/améliorer le système AI |
| **ATLAS (Prod)** | `.claude/` | Utiliser le système pour développer les apps |

## Structure

```
.atlas/
├── README.md                 # Ce fichier
├── ROADMAP.md               # Plan de développement ATLAS
├── CURRENT-STATE.md         # État actuel vs planifié
├── ARCHITECTURE.md          # Architecture du système AI
├── sessions/                # Logs des sessions de développement
│   └── 2025-11-30.md       # Session courante
└── drafts/                  # Brouillons d'agents/commands en dev
    ├── agents/
    ├── commands/
    └── skills/
```

## Comment reprendre le développement

1. Lire `.atlas/CURRENT-STATE.md` pour voir où on en est
2. Lire `.atlas/ROADMAP.md` pour les prochaines étapes
3. Continuer le développement
4. Mettre à jour les fichiers de suivi

## Workflow

```
Session ATLAS Dev → Améliorer système → Commit → Deploy vers .claude/
                                                         ↓
                                        Session ATLAS Prod → Développer apps
```
