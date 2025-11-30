# Archive AXIOM

Ce dossier contient les fichiers archivés lors des restructurations du projet.

## Structure

```
.archive/
└── YYYY-MM-DD/           # Date d'archivage
    ├── dev-context/      # Anciens fichiers .dev/context/
    ├── claude-context/   # Anciens fichiers .claude/context/
    └── dev-backlog/      # Anciens fichiers backlog
```

## Politique d'archivage

- Les fichiers sont archivés plutôt que supprimés pour conserver l'historique
- Chaque archivage est daté
- Les fichiers peuvent être restaurés si nécessaire
- Après 6 mois, les archives peuvent être supprimées

## Archives

### 2025-11-30 - Restructuration Monorepo

**Raison:** Migration vers nouvelle structure AI-first avec support monorepo

**Fichiers archivés:**
- `dev-context/`: Anciens fichiers de contexte DevConsole et workflow
- `claude-context/`: Anciens fichiers session MD (remplacés par JSON)
- `dev-backlog/`: Ancien backlog (fusionné dans roadmap/)

---

*Ne pas modifier ce dossier sans raison valide*
