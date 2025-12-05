# ATLAS Layering System

## Overview

ATLAS supports a layered architecture allowing projects to:
1. Use the shared framework as a base
2. Override specific components locally
3. Add project-specific agents, commands, and skills

## Directory Structure

```
project/
├── .claude -> atlas-framework/.claude  # Framework (symlink or submodule)
├── .atlas/                              # Project layer
│   ├── atlas.config.json               # Configuration
│   ├── agents/                         # Project-specific agents
│   ├── overrides/                      # Override framework components
│   ├── commands/                       # Project-specific commands
│   ├── skills/                         # Project-specific skills
│   └── runtime/                        # Sessions, checkpoints
└── .dev/                               # Project context (backlog, journal, etc.)
```

## Resolution Priority Chain

When loading a component (agent, command, skill):

```
Priority 3 (highest): .atlas/agents/{name}.md      # Project-local
Priority 2:           .atlas/overrides/{name}.md   # Override
Priority 1 (base):    .claude/agents/{name}.md     # Framework
```

## Configuration: atlas.config.json

```json
{
  "version": "2.1",
  "project": {
    "id": "my-project",
    "name": "My Project",
    "type": "standalone"  // standalone | child | parent
  },
  "framework": {
    "source": "symlink",  // symlink | submodule | local
    "path": "~/atlas-framework/.claude",
    "version": "2.1.0"
  },
  "layering": {
    "mode": "merge",      // merge | replace
    "priority": ["framework", "overrides", "local"]
  },
  "inherit_from": {
    "parent": "../.atlas",  // For child projects in monorepo
    "resources": ["credentials", "infrastructure"]
  }
}
```

## Project Types

### Standalone
Independent project with its own `.atlas/`:
```json
{ "project": { "type": "standalone" } }
```

### Parent (Monorepo root)
Contains shared resources for children:
```json
{
  "project": { "type": "parent" },
  "children": ["apps/synapse", "apps/nexus"],
  "shared_resources": {
    "credentials": "context/credentials.md",
    "infrastructure": "infra/registry.yml"
  }
}
```

### Child
Inherits from parent:
```json
{
  "project": { "type": "child" },
  "inherit_from": {
    "parent": "../../.atlas",
    "resources": ["credentials", "infrastructure"]
  }
}
```

## Override Examples

### Override a builder
Create `.atlas/overrides/backend.md` to replace `builders/backend.md`:
- File completely replaces framework version
- Use for project-specific tooling, conventions

### Add project agent
Create `.atlas/agents/my-specialist.md`:
- Agent only exists in this project
- Referenced as `my-specialist` in Task tool

### Extend settings
Create `.atlas/settings.local.json`:
- Merged with framework settings.json
- Project-specific model preferences, permissions

## Commands

- `/1-init-atlas` - Initialize .atlas/ structure in a project
- `/0-session-start` - Detects and loads layered configuration

## Best Practices

1. **Don't duplicate** - Only override what needs changing
2. **Document overrides** - Explain why in the override file header
3. **Keep .dev/ separate** - Project context stays in .dev/, not .atlas/
4. **Version your framework** - Track which framework version project uses
