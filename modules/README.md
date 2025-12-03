# AXIOM Modules

Composants réutilisables et infrastructure partagée.

## Structure

```
modules/
├── forge/              # Infrastructure Docker & configs
│   ├── docker-compose*.yml
│   ├── config/         # Traefik, Loki, Prometheus, etc.
│   └── services/       # Services custom (ccusage-exporter)
│
└── atlas-framework/    # Framework Claude Code
    ├── agents/         # Définitions d'agents
    ├── commands/       # Slash commands
    ├── sessions/       # Gestion de sessions
    └── config.yml      # Configuration ATLAS
```

## Utilisation

### FORGE (Infrastructure)

```bash
# Démarrer l'infrastructure
cd modules/forge
docker compose up -d

# Avec observabilité
docker compose -f docker-compose.yml -f docker-compose.observability.yml up -d
```

### ATLAS Framework

Le framework est automatiquement chargé via le symlink `.claude` à la racine d'AXIOM.

```bash
# Le symlink pointe vers:
.claude -> modules/atlas-framework/claude/
```

## Extraction vers repo séparé (optionnel)

Si tu veux extraire un module vers son propre repo :

```bash
# Méthode 1: Copie simple (sans historique git)
cp -r modules/forge /nouveau/chemin/forge
cd /nouveau/chemin/forge
git init
git add .
git commit -m "Initial commit from AXIOM"
git remote add origin git@github.com:seb155/forge.git
git push -u origin main

# Méthode 2: Avec historique (git filter-repo)
git clone AXIOM AXIOM-forge-only
cd AXIOM-forge-only
git filter-repo --subdirectory-filter modules/forge
git remote add origin git@github.com:seb155/forge.git
git push -u origin main
```

## Pourquoi modules/ au lieu de submodules ?

| Aspect | Submodules | Dossier modules/ |
|--------|-----------|------------------|
| Complexité | Élevée | Simple |
| Clone | `--recurse-submodules` | Standard |
| Synchronisation | Manuelle | Automatique |
| Extraction future | N/A | Possible |
| Repos externes | Requis | Optionnel |

Pour un projet solo ou une petite équipe, le dossier modules/ est plus pragmatique.
