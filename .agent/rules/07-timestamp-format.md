# Timestamp Format Rules

**Version:** 1.0
**Date:** 2025-11-28
**Statut:** Actif

---

## Standard Universel

**FORMAT OBLIGATOIRE:** `YYYY-MM-DD HH:MM`

### Règle Générale

Tous les agents AI doivent **TOUJOURS** utiliser le format complet `YYYY-MM-DD HH:MM` dans:
- Contenu de documents
- Logs et entrées de journal
- Réponses et outputs
- Métadonnées et tracking
- Time ranges (plages horaires)

**Aucune exception** sauf pour les noms de fichiers système (voir section Exceptions).

---

## Exemples

### ✅ Corrects

```
2025-11-28 14:30
2025-12-01 09:15
2025-11-28 23:59
2025-01-15 00:00
```

### ❌ Incorrects

```
2025-11-28              # Manque HH:MM
14:30                   # Manque date
28/11/2025 14:30        # Format US/EU incorrect
11-28-2025 14:30        # Ordre incorrect
2025-11-28T14:30:00Z    # ISO complet (trop verbeux)
2025-11-28_14:30        # Séparateur incorrect
```

---

## Time Ranges (Plages Horaires)

### Format OBLIGATOIRE

`[YYYY-MM-DD HH:MM] - [YYYY-MM-DD HH:MM]`

### Exemples Corrects

```markdown
## Session 1 [2025-11-28 09:00] - [2025-11-28 12:30]
## Session 2 [2025-11-28 14:00] - [2025-11-28 17:45]
## Work Period [2025-11-27 15:30] - [2025-11-27 18:00]
```

### ❌ Formats Interdits

```markdown
## Session 1 [09:00]-[12:30]           # Manque date
## Session 2 [HH:MM]-[HH:MM]           # Placeholder
## Work Period 09:00 - 12:30           # Sans brackets et sans date
```

**Raison:** Les time ranges complets permettent:
- Historique non-ambigu
- Reconstruction chronologique précise
- Traçabilité même hors contexte
- Support de plages multi-jours

---

## Exceptions Autorisées

### 1. Noms de Fichiers Système

**Seuls les noms de fichiers** peuvent utiliser des formats alternatifs pour respecter les contraintes filesystem.

#### Journal Quotidien
```
Format: YYYY-MM-DD
Exemple: .dev/journal/2025-11/2025-11-28.md
```

#### Session Summary
```
Format: YYYY-MM-DD-HH-MM
Exemple: .dev/journal/2025-11/2025-11-28-14-30.md
```

**Important:** Ces exceptions s'appliquent **UNIQUEMENT** aux noms de fichiers, **JAMAIS** au contenu des documents.

### 2. Aucune Autre Exception

- Pas d'exception pour "lisibilité"
- Pas d'exception pour "contexte évident"
- Pas d'exception pour "économie d'espace"
- Pas d'exception pour "formats courts"

---

## Application par Agent

### ATLAS (Orchestrator)

**Tous les outputs doivent inclure:**
- Headers de session: `YYYY-MM-DD HH:MM`
- Choix numérotés: Timestamps complets
- Logs de décisions: Format complet
- Time ranges: `[YYYY-MM-DD HH:MM] - [YYYY-MM-DD HH:MM]`

**Référence:** [.claude/agents/atlas.md](d:\Projects\AXIOM\.claude\agents\atlas.md)

### GENESIS (Meta-Agent)

**Toutes les observations et recommandations:**
- Date field: `YYYY-MM-DD HH:MM` (changement depuis 2025-11-28)
- Benchmarks: Format complet
- Recommendations: Format complet
- Observations: Format complet

**Référence:** [.claude/agents/orchestrators/genesis.md](d:\Projects\AXIOM\.claude\agents\orchestrators\genesis.md)

### Specialist Agents

**Tous les agents spécialisés (backend-builder, frontend-builder, etc.):**
- Outputs: `YYYY-MM-DD HH:MM`
- Documentation générée: Format complet
- Comments de code: Format complet si timestamp nécessaire
- Logs et traces: Format complet

### Workflows et Commands

**Tous les workflows et slash commands:**
- Instructions de logging: Format complet
- Exemples dans documentation: Format complet
- Templates: Format complet

---

## Guide de Validation

### Question Clé

**"Un humain lisant ce timestamp dans 6 mois saura-t-il EXACTEMENT quand cela s'est passé?"**

- Si **NON** → Ajouter la partie manquante (date ou heure)
- Si **OUI** → Format correct ✅

### Checklist Rapide

Avant d'écrire un timestamp, vérifier:
- [ ] Format `YYYY-MM-DD HH:MM`?
- [ ] Date complète (année, mois, jour)?
- [ ] Heure complète (heures, minutes)?
- [ ] Séparateur espace entre date et heure?
- [ ] Pas un nom de fichier (exception autorisée)?

Si **tous** cochés → ✅ Correct

---

## Rationale

### Pourquoi ce Standard?

1. **Traçabilité Totale**
   - Chaque événement daté avec précision minute
   - Aucune ambiguïté temporelle
   - Reconstruction chronologique fiable

2. **Cohérence Universelle**
   - Un seul format à retenir
   - Pas de confusion entre agents
   - Documentation homogène

3. **Historique Complet**
   - Time ranges autonomes (pas besoin de contexte)
   - Support plages multi-jours
   - Archive consultable à long terme

4. **Maintenabilité**
   - Format ISO-like universel
   - Tri chronologique naturel
   - Compatible parsing automatique

### Pourquoi Interdire les Formats Courts?

**Formats courts** (`[HH:MM]-[HH:MM]`) sont:
- ❌ Ambigus hors contexte
- ❌ Nécessitent contexte date implicite
- ❌ Problématiques pour historique long terme
- ❌ Incompatibles avec plages multi-jours

**Le gain en lisibilité est annulé par la perte en traçabilité.**

---

## Références

### Documents Principaux

| Document | Section | Notes |
|----------|---------|-------|
| [.claude/agents/atlas.md](d:\Projects\AXIOM\.claude\agents\atlas.md) | Lines 112-117 | Instructions ATLAS |
| [.dev/journal/session-template.md](d:\Projects\AXIOM\.dev\journal\session-template.md) | Lines 158-165 | Template format |
| [.claude/agents/orchestrators/genesis.md](d:\Projects\AXIOM\.claude\agents\orchestrators\genesis.md) | Line 152 | GENESIS format |
| [.claude/context/genesis-observations.md](d:\Projects\AXIOM\.claude\context\genesis-observations.md) | Line 12 | Template observations |

### Workflows Impactés

- [.agent/workflows/01-new-session.md](d:\Projects\AXIOM\.agent\workflows\01-new-session.md)
- [.agent/rules/06-navigation.md](d:\Projects\AXIOM\.agent\rules\06-navigation.md)
- [.claude/commands/0-ship.md](d:\Projects\AXIOM\.claude\commands\0-ship.md)

---

## Historique des Changements

### v1.0 - 2025-11-28

**Changements initiaux:**
- Création du guide central
- Standardisation `YYYY-MM-DD HH:MM` universelle
- Élimination format court `[HH:MM]-[HH:MM]`
- GENESIS aligné sur standard (était `YYYY-MM-DD`)
- Documentation exceptions filesystem

**Fichiers modifiés:**
- 1 créé (ce guide)
- 9 modifiés (agents, templates, workflows, docs)

**Scope:** Prospectif uniquement (documents existants préservés)
