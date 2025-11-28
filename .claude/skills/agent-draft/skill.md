---
name: agent-draft
description: Genere un template complet d'agent AI pour le systeme AXIOM
---

# Skill: Agent Draft

Genere un fichier agent complet avec tous les elements necessaires pour le systeme d'agents AXIOM.

## Usage

```text
/skill agent-draft [agent-name]
```

## Parametres

| Parametre | Description | Exemple |
|-----------|-------------|---------|
| `agent-name` | Nom du nouvel agent (kebab-case) | `security-auditor` |

## Output

Fichier genere dans `.claude/agents/drafts/[agent-name].md`

## Structure Generee

Le skill genere un fichier agent complet avec:

### 1. Header YAML

```yaml
---
name: [agent-name]
description: |
  Description de l'agent.
  Exemples d'utilisation.
model: sonnet | opus | haiku
color: green | blue | purple | orange
---
```

### 2. Mission

Description claire du role et de la responsabilite de l'agent.

### 3. Responsabilites

Liste numerotee des responsabilites principales avec sous-sections detaillees.

### 4. Protocoles

Workflows et procedures que l'agent doit suivre.

### 5. Fichiers Manipules

Table des fichiers avec acces en lecture/ecriture.

### 6. Style de Communication

Exemples de dialogues montrant le ton et le format.

### 7. Exemples

Scenarios complets d'utilisation.

### 8. Limites

Ce que l'agent ne doit PAS faire.

## Template

```markdown
---
name: {{agent-name}}
description: |
  [A completer: Description de l'agent]

  Exemples:
  - "[Exemple d'invocation]" -> [Resultat]
model: sonnet
color: green
---

# {{AGENT-NAME}} - [Titre]

## Mission

Tu es le **{{AGENT-NAME}}**, [description de la mission].

## Caracteristiques

- [Caracteristique 1]
- [Caracteristique 2]

## Responsabilites

### 1. [Responsabilite Principale]

- [Detail 1]
- [Detail 2]

### 2. [Autre Responsabilite]

- [Detail]

## Protocole

### Analyse

1. [Etape 1]
2. [Etape 2]

### Execution

1. [Etape 1]
2. [Etape 2]

## Fichiers Manipules

| Fichier/Dossier | Lecture | Ecriture |
|-----------------|---------|----------|
| [fichier] | Y | N |

## Style de Communication

### [Style 1]

{{agent-name}}: "[Exemple de dialogue]"

## Exemple Complet

User: "[Demande]"

{{AGENT-NAME}}: "[Reponse]"

## Limites

- [Limite 1]
- [Limite 2]
```

## Workflow

1. **Invocation**: `/skill agent-draft my-agent`
2. **Generation**: Cree le fichier dans `.claude/agents/drafts/my-agent.md`
3. **Revision**: L'utilisateur ou GENESIS revise le draft
4. **Validation**: Approbation explicite requise
5. **Deploiement**: Deplace vers la categorie finale

## Integration GENESIS

Ce skill est principalement utilise par l'agent GENESIS pour creer des drafts d'agents. Il peut aussi etre invoque directement par l'utilisateur.

## Exemple

```text
User: /skill agent-draft performance-profiler