# Rule 31: Project ID Resolution

## Purpose

Define how AI agents resolve `[project-id]` arguments to actual project paths.

---

## When This Rule Applies

Any command that accepts a `[project-id]` argument:

| Command | Example |
|---------|---------|
| `/0-session-continue` | `/0-session-continue echo` |
| `/0-session-start` | `/0-session-start synapse` |
| `/0-session-recover` | `/0-session-recover mechvision` |
| `/0-view-status` | `/0-view-status axiom` |
| `/0-view-roadmap` | `/0-view-roadmap nexus` |
| `/1-start-dev` | `/1-start-dev echo tests` |
| `/1-start-brainstorm` | `/1-start-brainstorm cortex` |
| `/1-start-debug` | `/1-start-debug synapse` |
| `/9-git-ship` | `/9-git-ship echo` |

---

## Resolution Algorithm

```
INPUT: project_id (string, case-insensitive)

1. WORKSPACE SCAN
   - Find all .dev/.dev-manifest.json in workspace
   - Build project registry from manifests

2. MATCH PROJECT ID
   - Normalize: project_id.lower()
   - Search registry for exact match
   - If found: return project_path
   - If NOT found: show available IDs

3. LOAD PROJECT CONTEXT
   - Read {project_path}/.dev/.dev-manifest.json
   - Apply context_type rules (from Rule 30)
   - Load session files from that project's .dev/
```

---

## Workspace Scan Logic

```
FUNCTION scan_workspace(workspace_root):
    projects = {}

    # Direct children of workspace
    FOR each dir in workspace_root:
        IF dir/.dev/.dev-manifest.json exists:
            manifest = read(dir/.dev/.dev-manifest.json)
            projects[manifest.project.id] = dir

            # If parent, also register all children
            IF manifest.context_type == "parent":
                FOR child in manifest.children:
                    child_path = dir + "/" + child.path.replace("/.dev", "")
                    projects[child.id] = child_path

    RETURN projects
```

**Example registry for /home/seb/projects:**

```json
{
  "axiom": "/home/seb/projects/AXIOM",
  "synapse": "/home/seb/projects/AXIOM/apps/synapse",
  "nexus": "/home/seb/projects/AXIOM/apps/nexus",
  "echo": "/home/seb/projects/AXIOM/apps/echo",
  "cortex": "/home/seb/projects/AXIOM/apps/cortex",
  "apex": "/home/seb/projects/AXIOM/apps/apex",
  "forge": "/home/seb/projects/AXIOM/forge",
  "mechvision": "/home/seb/projects/mechvision"
}
```

---

## Priority When No Argument

When command is called without `[project-id]`:

```
1. Check current directory for .dev/
   IF exists: use current project

2. Scan workspace for active sessions
   IF one active session: use that project
   IF multiple: ask user to choose

3. Scan workspace for all projects
   Show list and ask user to choose
```

---

## Error Handling

### Project Not Found

```
IF project_id NOT in registry:
    Display:
    "Project '[project_id]' not found."
    ""
    "Available projects:"
    "  axiom      - AXIOM Platform"
    "  synapse    - MBSE Platform"
    "  echo       - Voice Assistant"
    "  mechvision - AI Drawing Analyzer"
    ""
    "Usage: /0-session-continue [project-id]"
```

### No Manifest Found

```
IF .dev/.dev-manifest.json not found:
    WARN "No manifest in [dir], treating as standalone"
    Use directory name as project_id
```

---

## Examples

| Command | Resolution | Result |
|---------|------------|--------|
| `/0-session-continue echo` | registry["echo"] → AXIOM/apps/echo | Load ECHO context |
| `/0-session-continue SYNAPSE` | normalize → "synapse" → registry match | Load SYNAPSE |
| `/0-session-continue mechvision` | registry["mechvision"] → mechvision/ | Load MechVision |
| `/0-session-continue` | Current dir OR active session OR ask | Auto-detect |

---

## Implementation Notes

### For AI Agents

When processing a command with `[project-id]`:

1. Parse the argument (first word after command)
2. Call resolution algorithm
3. If resolved: set working context to that project
4. If not resolved: show error with available projects
5. Continue with command execution in resolved context

### Argument Parsing

```
/0-session-continue echo
                    ^^^^
                    project_id = "echo"

/1-start-dev synapse backend-tests
             ^^^^^^^
             project_id = "synapse"
             topic = "backend-tests"
```

---

## See Also

- Rule 30: Workspace Navigation (manifest system)
- session-management.md (session lifecycle)
