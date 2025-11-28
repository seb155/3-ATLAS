# /release

Prepare et execute une release.

## Usage

```text
/release              # Release avec version auto (patch)
/release minor        # Release minor version
/release major        # Release major version
/release [version]    # Release version specifique
```

## Actions

1. GIT-MANAGER analyse les commits depuis la derniere release
2. Determine le type de version (semantic versioning)
3. Genere le CHANGELOG
4. Cree le tag Git
5. Prepare la release GitHub (optionnel)

## Agent Invoque

- GIT-MANAGER (haiku) - Gestion des releases

## Semantic Versioning

```text
MAJOR.MINOR.PATCH

- MAJOR: Breaking changes
- MINOR: Nouvelles features (backward compatible)
- PATCH: Bug fixes
```

## Exemple

```text
User: /release minor

GIT-MANAGER:
"Preparation de release minor...

Version actuelle: 1.2.3
Nouvelle version: 1.3.0

Commits depuis v1.2.3:
- feat(synapse): add refresh button
- feat(synapse): add export functionality
- fix(nexus): resolve graph rendering issue
- docs: update API documentation

CHANGELOG genere:
## [1.3.0] - 2025-11-28

### Added
- Refresh button on project list (SYNAPSE)
- Export functionality (SYNAPSE)

### Fixed
- Graph rendering issue (NEXUS)

### Documentation
- Updated API documentation

Actions a effectuer:
1. Mettre a jour package.json / pyproject.toml
2. Mettre a jour CHANGELOG.md
3. Creer commit de release
4. Creer tag v1.3.0
5. Push avec tags

Tu confirmes la release v1.3.0?"
```
