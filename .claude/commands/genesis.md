---
description: Acces direct a GENESIS - Meta-agent d'evolution AI
---

# /genesis

Invoque **GENESIS** pour l'evolution du systeme d'agents AXIOM.

## Mode de Fonctionnement

GENESIS fonctionne en **bypass** (jamais via ATLAS) et en **parallele** de tous les autres agents. Il est **semi-autonome**: il propose des drafts et attend ta validation avant de deployer.

## Sous-commandes

### /genesis analyze

Analyse les sessions recentes et identifie les patterns.

```text
- Lit les fichiers .dev/journal/
- Identifie les demandes recurrentes
- Detecte les gaps dans le systeme d'agents
- Propose des recommandations
```

### /genesis recommend

Affiche les recommandations en attente de validation.

```text
- Liste toutes les recommandations [REC-XXX]
- Montre le status de chaque recommandation
- Permet d'approuver ou rejeter
```

### /genesis create [type] [name]

Cree un draft de nouvel agent, skill ou commande.

```text
Types disponibles:
- agent [name]    -> Cree un draft d'agent
- skill [name]    -> Cree un draft de skill
- command [name]  -> Cree un draft de commande

Exemple: /genesis create agent security-auditor
```

### /genesis benchmark

Lance un benchmarking des agents actuels.

```text
- Analyse les metriques d'utilisation
- Compare les performances par categorie
- Identifie les agents sous-utilises
- Propose des optimisations
```

### /genesis watch

Active la veille technologique.

```text
- Recherche web des meilleures pratiques AI agents
- Surveille les nouveautes Claude/Anthropic
- Propose des integrations innovantes
```

### /genesis self

Declenche l'auto-analyse et l'auto-amelioration de GENESIS.

```text
- Analyse sa propre efficacite
- Propose des ameliorations a son fichier agent
- Demande validation avant modification
```

## Exemples d'Utilisation

```text
User: /genesis analyze
-> Analyse les 30 dernieres sessions et propose des recommandations

User: /genesis create agent api-monitor
-> Cree un draft d'agent pour monitorer les APIs

User: /genesis benchmark
-> Compare l'efficacite de tous les agents actuels

User: /genesis self
-> GENESIS analyse sa propre performance et propose des ameliorations
```

## Agent Invoque

**GENESIS** (`orchestrators/genesis.md`) - Mode Bypass

- Modele: Opus (raisonnement complexe)
- Autonomie: Semi-autonome (drafts -> validation)
- Scope: Evolution du systeme d'agents AI
