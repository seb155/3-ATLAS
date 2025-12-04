# Toggle Recherche Web

Active/désactive la recherche web automatique pour Atlas.

## Usage

```
/0-web-toggle         # Affiche état actuel
/0-web-toggle on      # Active recherche auto (tech + temporel)
/0-web-toggle off     # Désactive (mode économique)
/0-web-toggle tech    # Toggle uniquement auto_tech
/0-web-toggle temporal # Toggle uniquement auto_temporal
```

## Configuration

Fichier: `.claude/config/web-search.json`

| Option | Défaut | Description |
|--------|--------|-------------|
| `auto_tech` | false | Recherche auto pour tech/dev |
| `auto_temporal` | false | Recherche auto pour dates récentes |
| `retry_threshold` | 2 | Échecs avant proposition |
| `propose_on_failure` | true | Proposer si incertain |

## Actions

### Si argument = (vide)
Afficher l'état actuel de la configuration web-search.json

### Si argument = "on"
Mettre `auto_tech: true` et `auto_temporal: true`

### Si argument = "off"
Mettre `auto_tech: false` et `auto_temporal: false`

### Si argument = "tech"
Inverser la valeur de `auto_tech`

### Si argument = "temporal"
Inverser la valeur de `auto_temporal`

## Coûts estimés

| Mode | Recherches/jour | Coût/mois |
|------|-----------------|-----------|
| OFF (économique) | ~5-10 | ~$1.50-3 |
| ON (auto) | ~20-50 | ~$6-15 |

## Exemple de sortie

```
🔍 Configuration Recherche Web

État actuel:
  auto_tech: false (économique)
  auto_temporal: false (économique)
  retry_threshold: 2
  propose_on_failure: true

Mode: ÉCONOMIQUE
Atlas proposera de chercher au lieu de chercher automatiquement.

Commandes:
  /0-web-toggle on    → Activer recherche auto
  /0-web-toggle tech  → Toggle recherche tech
```
