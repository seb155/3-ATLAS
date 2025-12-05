# Rule 30: Workspace Navigation

## Purpose

Define how AI agents navigate hierarchical `.dev/` structures in monorepos and multi-project workspaces.

---

## Manifest System

### File: `.dev/.dev-manifest.json`

Every `.dev/` directory MUST have a manifest declaring its context type:

| Type | Description |
|------|-------------|
| `parent` | Monorepo root with children projects |
| `child` | Sub-project within a parent |
| `standalone` | Independent project |

---

## Session Start Behavior

### 1. Read Manifest First

At session start (`/0-new-session`, `/1-dev`), ALWAYS read the manifest:

```
1. Read .dev/.dev-manifest.json
2. Determine context_type
3. Apply context-specific loading
```

### 2. Context-Specific Loading

**Standalone:**
```
Load local .dev/ only
→ context/project-state.md
→ context/hot-context.md
→ 1-sessions/active/
```

**Child:**
```
1. Load local .dev/
2. Read parent manifest (parent.path)
3. Load inherited resources from parent
   → credentials, infrastructure, etc.
4. Create session in LOCAL .dev/1-sessions/
```

**Parent:**
```
1. Load local .dev/
2. Display workspace.md overview
3. Ask "Which app do you want to work on?"
4. Navigate to selected child OR stay in parent context
```

---

## Parent Context

### workspace.md Display

When starting in a parent, show the workspace map:

```markdown
## AXIOM Workspace

| Project | Status | Progress |
|---------|--------|----------|
| SYNAPSE | Active | 85% |
| NEXUS | Dev | 40% |
...

Which app do you want to work on?
1. SYNAPSE
2. NEXUS
3. Stay in parent (cross-cutting work)
```

### Cross-Cutting Work

Parent context is for:
- Infrastructure changes affecting all apps
- Shared credentials management
- Architecture decisions (ADRs)
- Multi-app refactoring

---

## Child Context

### Resource Inheritance

Children inherit resources from parent via `inherit_from_parent` array:

```json
{
  "inherit_from_parent": ["credentials", "infrastructure"]
}
```

**Loading inherited resources:**
```
parent_path = manifest.parent.path
parent_manifest = read(parent_path + "/.dev-manifest.json")

for resource in manifest.inherit_from_parent:
    resource_path = parent_manifest.shared_resources[resource]
    load(parent_path + "/" + resource_path)
```

### Session Isolation

Sessions are ALWAYS created in the child's `.dev/1-sessions/`, not parent's.

---

## Navigation Commands

### From Parent to Child

```
# User in AXIOM root
User: "Work on SYNAPSE"

AI:
1. Read AXIOM/.dev/.dev-manifest.json
2. Find child "synapse" → path: "apps/synapse/.dev"
3. cd apps/synapse
4. Load apps/synapse/.dev/.dev-manifest.json
5. Load context + parent inherited resources
```

### From Child to Parent

```
# User in apps/synapse
User: "Access infrastructure registry"

AI:
1. Read apps/synapse/.dev/.dev-manifest.json
2. parent.path = "../../../.dev"
3. Read parent shared_resources.infrastructure
4. Load ../../../.dev/infra/registry.yml
```

---

## Shared Resources Reference

### Standard Shared Resources

| Resource Key | Typical Path | Purpose |
|--------------|--------------|---------|
| `credentials` | `context/credentials.md` | DB passwords, API keys |
| `infrastructure` | `infra/registry.yml` | Ports, networks, services |
| `decisions` | `decisions/` | Architecture Decision Records |
| `apps_registry` | `ai/active-apps.json` | App status tracking |

### Custom Resources

Parents can define any shared resources:

```json
{
  "shared_resources": {
    "credentials": "context/credentials.md",
    "infrastructure": "infra/registry.yml",
    "styleguide": "docs/styleguide.md",
    "api_specs": "docs/api/"
  }
}
```

---

## Implementation Checklist

When implementing workspace navigation:

- [ ] Read `.dev-manifest.json` at session start
- [ ] Handle all three context types
- [ ] Load inherited resources for children
- [ ] Display workspace map for parents
- [ ] Create sessions in local `.dev/` only
- [ ] Allow cross-context resource access
- [ ] Update manifest when structure changes

---

## Error Handling

### Missing Manifest

```
IF .dev/.dev-manifest.json not found:
    WARN "No manifest found, treating as standalone"
    context_type = "standalone"
```

### Invalid Parent Reference

```
IF child.parent.path points to non-existent .dev/:
    ERROR "Parent manifest not found at {path}"
    SUGGEST "Run /1-init-project in parent directory"
```

### Missing Inherited Resource

```
IF inherited resource not in parent:
    WARN "Resource '{key}' not found in parent"
    CONTINUE without that resource
```

---

## See Also

- `.claude/commands/1-init-project.md` - Project initialization
- `.claude/templates/dev/.dev-manifest-*.json` - Manifest templates
- `.claude/agents/rules/session-management.md` - Session rules
