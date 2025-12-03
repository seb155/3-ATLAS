---
description: Multi-project status - Health, sessions, git for all projects
---

# /0-view-projects

Affiche le status de tous les projets du workspace.

**Agent:** PROJECTS-SCANNER

## Usage

```bash
/0-view-projects    # Scan and display all projects
```

## Actions

1. **Execute scan script**
   ```powershell
   $scanData = .\.claude\scripts\scan-projects.ps1 | ConvertFrom-Json
   ```

2. **Generate Last Sessions section**
   Pour chaque projet, afficher une ligne:
   ```
   [emoji] **[name]** ([lastSession.lastDate]) ✓ [did] → [next]
   ```

3. **Generate status table**
   Pour chaque projet dans `$scanData.projects`:

   | Colonne | Source | Format |
   |---------|--------|--------|
   | Projet | emoji + display_name | `🏗️ **AXIOM**` |
   | Description | registry description | Short text |
   | Docker | docker.runningCount/totalCount | `🟢 X/Y` ou vide |
   | Sprint | project-state.md | `X/Y` ou vide |
   | Git | git.modified + git.untracked | `⚠️ N` ou vide |

4. **Generate suggestions**
   Top 3 projets avec "next" + Refresh + Other

## Project Emojis

| ID | Emoji |
|----|-------|
| axiom | 🏗️ |
| findash | 💰 |
| homelab-msh | 🖥️ |
| homeassistant | 🏠 |
| note-synch | 📝 |
| atlas-framework | 🤖 |

## Output Format

```markdown
## 📋 Last Sessions & What's Next

🏗️ **AXIOM** (25-11-28 16:30) ✓ Implement auth system → Finalize notifications
💰 **FinDash** (25-11-25 14:00) ✓ Initial setup, Gemini → Add portfolio charts
🖥️ **Homelab** (25-11-27 10:15) ✓ Proxmox inventory scan → GPU profile switching
🏠 **HA-MCP** (25-11-20 09:00) ✓ Install NPU drivers → Add energy monitoring
📝 **NoteSync** (25-11-15 11:30) ✓ Docker setup → Configure sync rules
🤖 **Atlas-Fw** (25-11-29 19:45) ✓ Add projects-scanner → Test integration

---

## 📊 Projects Status (25-11-29 20:00)

| Projet                | Description                    | Docker   | Sprint | Git      |
|-----------------------|--------------------------------|----------|--------|----------|
| 🏗️ **AXIOM**          | Platform engineering monorepo  | 🟢 10/10 | 4/12   | ⚠️ 23    |
| 💰 **FinDash**        | Financial dashboard AI         | 🟢 1/1   |        | ⚠️ 8     |
| 🖥️ **Homelab**        | Proxmox + UniFi inventory      |          |        | ⚠️ 1     |
| 🏠 **HA-MCP**         | Home Assistant MCP servers     |          |        | ⚠️ 1     |
| 📝 **NoteSync**       | Trilium bidirectional sync     | 🟢 3/3   |        |          |
| 🤖 **Atlas-Fw**       | Agent framework template       |          |        | ⚠️ 10    |

**Git:** ✅ clean | ⚠️ N fichiers modifies

---

## What do you want to do?

1. 🏗️ **AXIOM** - Continue auth system
2. 💰 **FinDash** - Add portfolio charts
3. 🖥️ **Homelab** - GPU profile switching
4. 🔄 **Refresh** - Re-scan all projects
5. 📋 **Other** - Different project or task

> Type 1-5 or describe what you want
```

## Display Rules

### Timestamps
- Format: `YY-MM-DD HH:MM`
- Header: scan_time du script
- Projects: lastSession.lastDate

### Empty Cells
- Pas d'emoji si vide
- Pas de "-" avec emoji
- Juste cellule vide

### Git Column
- `✅` si clean (isDirty = false)
- `⚠️ N` si dirty (N = modified + untracked)
- Vide si pas de git

### Docker Column
- `🟢 X/Y` si containers (X running, Y total)
- Vide si pas de containers

## Error Handling

### Registry Missing
```
Registry not found at .registry/projects.json

To create/sync the registry:
.claude\scripts\sync-registry.ps1
```

### No Session Data
```
🏗️ **AXIOM** (--) No session data
```

---

## See Also

- `/0-session-start` - Start session on specific project
- `/0-view-status` - Single project status
- `/0-view-roadmap` - Single project roadmap
