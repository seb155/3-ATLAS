---
description: Start brainstorm/whiteboard session with auto-documentation
---

# /1-start-brainstorm

Start a brainstorm/whiteboard session with auto-documentation.

## Usage

```bash
/1-start-brainstorm                    # Start in current project
/1-start-brainstorm echo               # Start brainstorm on ECHO
/1-start-brainstorm synapse api-design # Start on SYNAPSE with topic
/1-start-brainstorm [project] [topic]  # General format
```

## Arguments

- `[project-id]` (optional): Identifiant du projet cible
  - Case-insensitive
  - Résolution via Rule 31 (project-resolution.md)
- `[topic]` (optional): Brainstorm topic

---

## Workflow

### Step 1: Resolve Project (if argument)

```
IF project-id provided:
    Resolve via Rule 31
    Change context to target project
    Display: "📂 Projet: [name] ([path])"
```

### Step 2: Check Active Session

```
Read .dev/1-sessions/active/current-session.md

IF EXISTS and Type != brainstorm:
    "⚠️ Session active trouvée: [topic]"
    "Type: [type]"

    1. Mettre en pause et démarrer brainstorm
    2. Archiver et démarrer brainstorm
    3. Annuler

IF EXISTS and Type == brainstorm:
    "📋 Session brainstorm en cours: [topic]"
    1. Continuer
    2. Archiver et nouvelle
```

### Step 3: Create Brainstorm Session

```
Create/Update .dev/1-sessions/active/current-session.md

# Session: [Topic] Brainstorm

**Started:** [timestamp]
**Type:** brainstorm
**Branch:** [git branch]
**Status:** active

---

## Objective
[What we want to explore/decide]

## Ideas Explored
[Will be populated during session]

## Key Insights
[Will be populated during session]

## Decisions Made
[Will be populated during session]

## Action Items
[Will be populated during session]

---

**Last updated:** [timestamp]
```

### Step 4: Start Brainstorming

```
Display:
"💭 Session brainstorm démarrée!"
"Project: [project name]"
"Topic: [topic]"

"Techniques disponibles:"
- Mind mapping
- Crazy 8s
- Decision matrix
- Trade-off analysis

"Décris ce que tu veux explorer:"
```

---

## During Session

### Auto-Save Points

After each major exploration:
1. Update session file with new ideas/insights
2. Append to daily journal

### Techniques Used

**Mind Mapping:**
```
            [Central Topic]
                  |
    +------+------+------+
    |      |      |      |
 [Idea1] [Idea2] [Idea3] [Idea4]
```

**Decision Matrix:**
```
| Option | Complexity | Impact | Risk |
|--------|------------|--------|------|
| A      | Low        | High   | Low  |
| B      | High       | High   | Med  |
```

---

## End Session

When brainstorm is complete:

1. Summarize key insights
2. List action items
3. Auto-append to journal
4. Option to archive or keep active

```
"📝 Brainstorm terminé!"

"Insights clés:"
- [Insight 1]
- [Insight 2]

"Actions à prendre:"
1. [Action 1]
2. [Action 2]

"Que veux-tu faire?"
1. Archiver et passer au dev
2. Continuer à explorer
3. Créer des items backlog
```

---

## Auto-Documentation

At session end, append to `.dev/journal/YYYY-MM/YYYY-MM-DD.md`:

```markdown
### [HH:MM] Brainstorm: [Topic]

**Insights:**
- [Key insight 1]
- [Key insight 2]

**Decisions:**
- [Decision made]

**Next Steps:**
- [Action item]
```

---

## See Also

- `/1-start-dev` - Switch to dev mode
- `/1-start-debug` - Debug session
- `/9-session-archive` - Archive session
- Rule 31 - Project ID resolution
