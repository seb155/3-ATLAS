# System Tools Reference

Guide des outils système disponibles dans Claude Code.

---

## Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture JSON Schema](#architecture-json-schema)
3. [Catalogue des Outils](#catalogue-des-outils)
4. [Extensibilité](#extensibilité)

---

## Vue d'Ensemble

Les **System Tools** sont les fonctions natives que Claude Code peut invoquer pour interagir avec le système. Ils représentent environ **15k tokens** du contexte (~7.5% sur 200k).

### Cycle d'Appel

```
┌─────────────────────────────────────────────────────────────┐
│                      CLAUDE (LLM)                           │
│                                                             │
│  1. Génère appel XML    ──────────────────────────────┐    │
│                                                        │    │
│                                                        ▼    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              CLAUDE CODE (Runtime)                    │  │
│  │                                                       │  │
│  │  2. Parse XML ──► 3. Valide JSON Schema              │  │
│  │                          │                            │  │
│  │                          ▼                            │  │
│  │              4. Exécute l'outil                       │  │
│  │                          │                            │  │
│  │                          ▼                            │  │
│  │              5. Retourne résultat                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                        │    │
│  6. Reçoit résultat   ◄───────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Architecture JSON Schema

Chaque outil est défini avec un schéma JSON (draft-07) qui spécifie ses paramètres.

### Structure Type

```json
{
  "name": "NomOutil",
  "description": "Description de l'outil...",
  "parameters": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "param_required": {
        "type": "string",
        "description": "Un paramètre obligatoire"
      },
      "param_optional": {
        "type": "boolean",
        "default": false,
        "description": "Un paramètre optionnel"
      }
    },
    "required": ["param_required"]
  }
}
```

### Types de Paramètres

| Type | Exemple | Usage |
|------|---------|-------|
| `string` | `"/path/file.ts"` | Chemins, texte, patterns |
| `number` | `42`, `3.14` | Timeouts, limites, offsets |
| `boolean` | `true`/`false` | Flags, options on/off |
| `array` | `["a", "b"]` | Listes de valeurs |
| `object` | `{"key": "val"}` | Structures imbriquées |

### Contraintes Courantes

| Contrainte | Effet |
|------------|-------|
| `required` | Paramètre obligatoire |
| `default` | Valeur par défaut si omis |
| `enum` | Liste de valeurs permises |
| `minLength`/`maxLength` | Longueur de string |
| `minimum`/`maximum` | Bornes numériques |
| `minItems`/`maxItems` | Taille de tableau |

---

## Catalogue des Outils

### Fichiers

| Outil | Description | Paramètres Requis |
|-------|-------------|-------------------|
| **Read** | Lire un fichier (texte, image, PDF, notebook) | `file_path` |
| **Write** | Créer/écraser un fichier | `file_path`, `content` |
| **Edit** | Rechercher/remplacer dans un fichier | `file_path`, `old_string`, `new_string` |
| **Glob** | Trouver des fichiers par pattern | `pattern` |
| **Grep** | Chercher du contenu (regex) | `pattern` |

### Exécution

| Outil | Description | Paramètres Requis |
|-------|-------------|-------------------|
| **Bash** | Exécuter une commande shell | `command` |
| **BashOutput** | Lire sortie d'un shell background | `bash_id` |
| **KillShell** | Terminer un shell background | `shell_id` |

### Web

| Outil | Description | Paramètres Requis |
|-------|-------------|-------------------|
| **WebSearch** | Recherche web | `query` |
| **WebFetch** | Récupérer contenu d'une URL | `url`, `prompt` |

### Agents

| Outil | Description | Paramètres Requis |
|-------|-------------|-------------------|
| **Task** | Lancer un sous-agent | `prompt`, `subagent_type`, `description` |

### Interaction

| Outil | Description | Paramètres Requis |
|-------|-------------|-------------------|
| **AskUserQuestion** | Poser des questions structurées | `questions` (array) |
| **TodoWrite** | Gérer la liste de tâches | `todos` (array) |

### Autres

| Outil | Description | Paramètres Requis |
|-------|-------------|-------------------|
| **NotebookEdit** | Éditer cellule Jupyter | `notebook_path`, `new_source` |
| **SlashCommand** | Exécuter commande slash | `command` |
| **Skill** | Exécuter un skill | `skill` |
| **EnterPlanMode** | Entrer en mode planification | (aucun) |
| **ExitPlanMode** | Sortir du mode planification | (aucun) |

---

## Extensibilité

### Ce qu'on peut faire

| Méthode | Usage |
|---------|-------|
| **MCP Servers** | Ajouter des outils custom via Model Context Protocol |
| **Hooks** | Intercepter/modifier le comportement des outils |
| **Slash Commands** | Créer des workflows réutilisables |
| **Agents Custom** | Définir des personnalités avec prompts spécialisés |

### Ce qu'on ne peut pas faire

- Modifier le code source des outils natifs
- Remplacer un outil système par un custom
- Changer le schéma JSON des outils existants

### MCP (Model Context Protocol)

```bash
# Ajouter un serveur MCP
claude mcp add myserver -- /path/to/server

# Les outils apparaissent comme: mcp__myserver__tool_name
```

### Hooks

```json
// settings.json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit",
        "command": "echo 'Avant édition'"
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "command": "echo 'Après bash'"
      }
    ]
  }
}
```

| Hook | Moment | Capacités |
|------|--------|-----------|
| `PreToolUse` | Avant exécution | Bloquer, modifier inputs |
| `PostToolUse` | Après exécution | Formater output, ajouter contexte |

---

**Last Updated**: 2025-12-01
**Framework Version**: Atlas 1.2
**Claude Code Version**: Compatible toutes versions
