# Project Registry System

The Atlas Agent Framework includes a project discovery and registry system that enables workspace-level awareness of all projects.

## Overview

The registry system provides:
- **Auto-discovery**: Scan filesystem to detect projects automatically
- **Structured registry**: JSON-based project metadata storage
- **ROOT context**: Workspace-level awareness when not in a specific project
- **Cross-project queries**: Find projects by name, tech stack, or type

## Architecture

```
Workspace Root (D:\Projects\)
    │
    ├── .registry/                    # Local registry (not in git)
    │   ├── projects.json             # Project metadata
    │   └── discovery-config.json     # Scan configuration
    │
    └── .claude/scripts/              # Registry scripts
        ├── discover-projects.ps1     # Scanner engine
        ├── sync-registry.ps1         # User-friendly wrapper
        └── query-registry.ps1        # Query tool
```

## Setup

### 1. Create Registry Directory

```powershell
mkdir "D:\Projects\.registry"
```

### 2. Create Configuration

Create `.registry/discovery-config.json`:

```json
{
  "version": "1.0.0",
  "workspace_root": "D:\\Projects",
  "scan_paths": [
    "D:\\Projects\\MyProject1",
    "D:\\Projects\\MyProject2"
  ],
  "auto_sync": {
    "enabled": true,
    "interval_days": 1
  },
  "detection_rules": {
    "signals": ["CLAUDE.md", ".git", "package.json", "requirements.txt"],
    "type_inference": {
      "monorepo": ["apps/", "packages/"],
      "mcp-server": ["server.py", "start_server.sh"]
    }
  }
}
```

### 3. Run Initial Discovery

```powershell
.claude\scripts\sync-registry.ps1 -Force
```

## Usage

### List All Projects

```powershell
.claude\scripts\query-registry.ps1 -ListAll
```

Output:
```
  Atlas Project Registry
  ======================

  [*] AXIOM (monorepo)
      Path: AXIOM
      Tech: python, typescript, react, fastapi, docker

  [*] FinDash (application)
      Path: 8-Perso\FinDash
      Tech: react, typescript, vite
```

### Query Specific Project

```powershell
.claude\scripts\query-registry.ps1 -ProjectId axiom
```

### Filter by Technology

```powershell
.claude\scripts\query-registry.ps1 -TechFilter python
```

### Filter by Type

```powershell
.claude\scripts\query-registry.ps1 -TypeFilter monorepo
```

### JSON Output

```powershell
.claude\scripts\query-registry.ps1 -ListAll -Json
```

### Brief Output

```powershell
.claude\scripts\query-registry.ps1 -ListAll -Brief
```

## Registry Schema

### projects.json

```json
{
  "version": "1.0.0",
  "last_updated": "2025-11-29T00:00:00Z",
  "workspace_root": "D:\\Projects",
  "projects": [
    {
      "id": "my-project",
      "name": "MyProject",
      "display_name": "MyProject",
      "path": "D:\\Projects\\MyProject",
      "relative_path": "MyProject",
      "type": "application",
      "status": "active",
      "description": "Project description",
      "tech_stack": ["python", "fastapi"],
      "quick_commands": [
        {
          "name": "Dev",
          "command": "python main.py",
          "description": "Start development server"
        }
      ],
      "sub_projects": [],
      "metadata": {
        "has_claude_md": true,
        "has_git": true,
        "has_dev_folder": false
      }
    }
  ]
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (lowercase, alphanumeric) |
| `name` | string | Directory name |
| `display_name` | string | Short display name for CLI |
| `path` | string | Absolute path |
| `relative_path` | string | Path relative to workspace root |
| `type` | string | `application`, `monorepo`, `mcp-server`, `infrastructure`, `framework` |
| `status` | string | `active`, `archived`, `development` |
| `description` | string | Project description (from CLAUDE.md) |
| `tech_stack` | array | Technologies detected |
| `quick_commands` | array | Common commands |
| `sub_projects` | array | Sub-projects for monorepos |
| `metadata` | object | Detection flags |

## Auto-Discovery

The discovery script detects projects by looking for these signals:

| Signal | Detection |
|--------|-----------|
| `CLAUDE.md` | Atlas-managed project |
| `.git` | Git repository |
| `package.json` | Node.js project |
| `requirements.txt` | Python project |
| `pyproject.toml` | Python project |
| `docker-compose*.yml` | Docker project |
| `apps/` directory | Monorepo |
| `server.py` | MCP server |

### Type Inference

| Type | Signals |
|------|---------|
| `monorepo` | Has `apps/`, `packages/`, or `services/` directory |
| `mcp-server` | Has `server.py` or `start_server.sh` |
| `infrastructure` | Has `docker-compose.yml` + `scripts/` directory |
| `application` | Default |

## Integration with detect-project.ps1

The `detect-project.ps1` script (used by CLI status line) reads from the registry:

1. Loads `.registry/projects.json`
2. Builds project maps from registry data
3. Falls back to hardcoded values if registry not found

This ensures:
- New projects are automatically recognized
- CLI status line shows correct project name
- Backwards compatibility if registry is missing

## ROOT Context Mode

When `/0-new-session` is invoked from the workspace root:

1. Detects ROOT context (no project-specific directory)
2. Loads registry
3. Lists all active projects with:
   - Display name and type
   - Tech stack
   - Description
4. Offers navigation to specific projects

Example output:
```
ATLAS: "Bonjour! Contexte ROOT detecte.

**Workspace**: D:\Projects
**Projets actifs**: 6 detectes

| Projet | Type | Tech | Description |
|--------|------|------|-------------|
| AXIOM | monorepo | Python, TS | Engineering platform |
| FinDash | app | React, TS | Financial dashboard |
...

**Que veux-tu faire?**
1. Ouvrir AXIOM
2. Ouvrir FinDash
3. Sync registre
..."
```

## Adding New Projects

### Method 1: Manual

1. Add path to `discovery-config.json`:
   ```json
   "scan_paths": [
     "D:\\Projects\\NewProject"
   ]
   ```

2. Run sync:
   ```powershell
   .claude\scripts\sync-registry.ps1 -Force
   ```

### Method 2: Direct Edit

Add project entry directly to `projects.json` following the schema above.

## Troubleshooting

### Registry Not Found

```
Error: Registry not found
```

Solution: Run initial sync:
```powershell
.claude\scripts\sync-registry.ps1 -Force
```

### Project Not Detected

Check that:
1. Path is in `discovery-config.json` `scan_paths`
2. Project has at least one detection signal
3. Project is not in `exclude_patterns`

### Stale Registry

Force re-scan:
```powershell
.claude\scripts\sync-registry.ps1 -Force
```

## Best Practices

1. **Keep scan_paths explicit**: Only include projects you actively work on
2. **Sync regularly**: Run sync after adding new projects
3. **Use quick_commands**: Document common commands for easy reference
4. **Add descriptions**: Include project descriptions in CLAUDE.md for auto-extraction
