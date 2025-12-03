# Agent Standards - Atlas Framework

This document defines the standards for creating and maintaining agents in the Atlas framework for Claude Code 2.0.55+.

---

## Frontmatter Format

All agents MUST have a YAML frontmatter block at the top of their `.md` file:

```yaml
---
name: agent-name
description: Agent purpose and when to use it
type: orchestrator
model: opus
color: gold
---
```

---

## Required Fields

### name
**Format**: lowercase letters, numbers, hyphens only
**Example**: `backend-builder`, `devops-manager`, `ux-designer`

**Rules**:
- No uppercase letters
- No underscores (use hyphens)
- No spaces
- Must be unique across all agents

### description
**Format**: String or multi-line block (using `|`)
**Example**:
```yaml
description: Infrastructure orchestration - Docker, Traefik, network topology, port allocation
```

Or multi-line:
```yaml
description: |
  Creates React components with TypeScript

  Use when: Building frontend features, creating UI components
```

**Rules**:
- Write in third person
- Include what the agent does
- Include when to use it
- Be concise but descriptive (1-3 sentences recommended)
- Enables agent discovery in Claude Code

---

## Optional Fields

### type
**Format**: One of: `orchestrator`, `builder`, `planner`, `specialist`, `rule`
**Purpose**: Categorizes agents by their primary function

| Type | Purpose | Typical Complexity |
|------|---------|-------------------|
| `orchestrator` | High-level coordination, session management, routing | High (opus) |
| `builder` | Code generation, implementation, scaffolding | Medium (sonnet/haiku) |
| `planner` | Analysis, planning, design, debugging | Medium (sonnet) |
| `specialist` | Domain expertise, complex diagnosis, workshops | High (opus) |
| `rule` | Framework rules, not directly invoked by users | N/A (no model) |

### model
**Format**: One of: `opus`, `sonnet`, `haiku`
**Purpose**: Specifies which Claude model to use for this agent
**Default**: Inherits from parent if not specified

**Guidelines**:
- **opus**: Complex reasoning, multi-step planning, critical decisions
  - Examples: ATLAS, genesis, system-architect, devops-manager
- **sonnet**: Balanced performance, most code generation
  - Examples: backend-builder, frontend-builder, debugger, planner
- **haiku**: Fast, simple tasks, quick scaffolding
  - Examples: doc-writer, devops-builder (config generation)

**Cost vs Performance**:
- opus: Highest cost, best reasoning
- sonnet: Balanced cost/performance
- haiku: Lowest cost, fastest response

### color
**Format**: String (color name)
**Purpose**: Visual distinction in Claude Code UI
**Optional**: Only needed for user-facing agents (not rules)

**Atlas Framework Color Scheme**:

| Color | Agent Category | Agents |
|-------|---------------|--------|
| `gold` | Core orchestration | ATLAS, WORKSHOP-FACILITATOR |
| `purple` | Meta/system evolution | genesis, system-architect |
| `orange` | Infrastructure | devops-manager, devops-builder |
| `green` | Backend/planning | backend-builder, planner |
| `blue` | Frontend/UI | frontend-builder |
| `cyan` | Design/documentation | ux-designer |
| `pink` | Creative/brainstorming | brainstorm |
| `red` | Debugging/fixing | debugger |
| `gray` | Documentation | doc-writer |

### tools
**Format**: Comma-separated list
**Purpose**: Restricts agent to specific tools
**Default**: Inherits all tools if omitted

**Example**:
```yaml
tools: Read, Write, Edit, Bash
```

**Best Practice**: Omit this field unless you need to restrict tools for security/safety.

---

## Type Taxonomy

### Orchestrator
**Purpose**: High-level coordination, session management, task routing
**Model**: `opus` (requires complex reasoning)
**Color**: `gold` or `purple`

**Characteristics**:
- Makes architectural decisions
- Routes tasks to specialized agents
- Manages session state
- Handles multi-step workflows

**Examples**:
- ATLAS - Main orchestrator
- brainstorm - Creative exploration
- genesis - Meta-agent evolution
- system-architect - System design

### Builder
**Purpose**: Code generation, implementation, scaffolding
**Model**: `sonnet` or `haiku`
**Color**: Varies by domain (green/blue/orange/gray)

**Characteristics**:
- Generates code files
- Implements features
- Creates scaffolding/boilerplate
- Follows existing patterns

**Examples**:
- backend-builder - FastAPI/Python backend
- frontend-builder - React/TypeScript frontend
- devops-builder - Docker/infrastructure configs
- doc-writer - Documentation generation

### Planner
**Purpose**: Analysis, planning, design, debugging
**Model**: `sonnet` (balanced reasoning)
**Color**: Varies by domain (green/cyan/red)

**Characteristics**:
- Analyzes problems
- Creates implementation plans
- Designs solutions
- Debugs issues

**Examples**:
- planner - General planning
- debugger - Bug investigation
- ux-designer - UI/UX design

### Specialist
**Purpose**: Domain expertise, complex diagnosis, facilitation
**Model**: `opus` (requires deep expertise)
**Color**: `gold` or `orange`

**Characteristics**:
- Deep domain knowledge
- Handles complex scenarios
- Requires high reasoning
- Facilitates processes

**Examples**:
- devops-manager - Infrastructure diagnosis
- WORKSHOP-FACILITATOR - Design Thinking workshops

### Rule
**Purpose**: Framework rules and protocols
**Model**: None (not invoked as agents)
**Color**: None

**Characteristics**:
- Defines standards
- Not directly invoked by users
- Referenced by other agents
- Framework documentation

**Examples**:
- auto-documentation - Documentation triggers
- response-protocol - Response format rules
- session-management - Session lifecycle rules

---

## Complete Example

### High-Complexity Agent (Orchestrator)
```yaml
---
name: ATLAS
description: Main orchestrator - Session management, task routing, auto-documentation
type: orchestrator
model: opus
color: gold
---
```

### Medium-Complexity Agent (Builder)
```yaml
---
name: backend-builder
description: |
  Creates backend code - FastAPI endpoints, database models, business logic

  Use when: Implementing backend features, APIs, services
model: sonnet
type: builder
color: green
---
```

### Low-Complexity Agent (Builder)
```yaml
---
name: doc-writer
description: |
  Generates documentation - README files, API docs, guides

  Use when: Creating or updating documentation
model: haiku
type: builder
color: gray
---
```

### Rule Definition
```yaml
---
name: response-protocol-rules
description: Unified response protocol for all human-facing agents - Recap + numbered choices format
type: rule
---
```

---

## Validation Checklist

Before committing a new or modified agent file:

- [ ] Has `---` delimiters at start and end of frontmatter
- [ ] Has `name` field (lowercase, hyphens only)
- [ ] Has `description` field (third person, describes purpose and usage)
- [ ] Has `type` field (one of 5 valid types)
- [ ] Has `model` field (opus/sonnet/haiku) - unless type is `rule`
- [ ] Has `color` field (matches color scheme) - unless type is `rule`
- [ ] YAML syntax is valid (test with Claude Code reload)
- [ ] Description is concise (1-3 sentences)
- [ ] Model choice aligns with complexity (opus for complex, haiku for simple)
- [ ] Color choice aligns with domain/function

---

## Best Practices

### Naming Conventions
- Use descriptive names: `backend-builder` not `bb`
- Include domain: `devops-manager`, `ux-designer`
- Use action verbs for builders: `builder`, `writer`, `generator`
- Use role names for specialists: `manager`, `facilitator`, `architect`

### Description Writing
- Start with what it does: "Creates React components..."
- Include when to use: "Use when: Building frontend features"
- Be specific: "FastAPI endpoints" not "backend code"
- Use active voice: "Creates" not "Can create"
- Third person: "Creates" not "I create"

### Model Selection
Ask these questions:
1. Does it require complex multi-step reasoning? → `opus`
2. Does it need to analyze complex systems? → `opus`
3. Is it primarily code generation from patterns? → `sonnet`
4. Is it simple scaffolding or templating? → `haiku`
5. Is it documentation that doesn't need reasoning? → `haiku`

### Color Selection
- Match existing agents in same domain
- Use warm colors (orange/red) for infrastructure/debugging
- Use cool colors (blue/cyan) for frontend/design
- Use purple for meta/system agents
- Use gold for core orchestration
- Keep it consistent across the framework

---

## Migration Guide

### Adding `type` to Existing Agents

1. Identify agent's primary purpose
2. Match to taxonomy (orchestrator/builder/planner/specialist/rule)
3. Add `type:` field to frontmatter
4. Verify model choice aligns with type defaults

### Adding `color` to Existing Agents

1. Check agent's domain (frontend/backend/infra/etc.)
2. Look at color scheme table
3. Pick color that matches domain
4. Ensure no conflicts with similar agents
5. Add `color:` field to frontmatter

### Adding `model` to Existing Agents

1. Evaluate agent complexity
2. Match to guidelines (opus/sonnet/haiku)
3. Add `model:` field to frontmatter
4. Test agent behavior (may need to adjust if wrong model)

---

## Testing Agent Definitions

After modifying frontmatter:

1. **Reload Claude Code**: Restart CLI to pick up changes
2. **Check for Parse Errors**: Look for error messages on load
3. **Test Invocation**: Try invoking agent via Task tool
4. **Verify Metadata**: Ensure type/color display correctly (if UI supports it)
5. **Test Behavior**: Verify agent uses correct model (opus vs sonnet response quality)

---

## Maintenance

### When to Update This Document
- New agent type added to framework
- Color scheme changes
- Claude Code introduces new frontmatter fields
- Model naming changes (e.g., new Claude versions)

### Version History
- 2025-01-29: Initial version for Claude Code 2.0.55
- Defines 5 agent types (orchestrator, builder, planner, specialist, rule)
- Establishes color scheme for Atlas framework
- Documents all required and optional frontmatter fields

---

## Resources

### Official Documentation
- [Agent Skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [Skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Claude Code Custom Agent Framework](https://dev.to/therealmrmumba/claude-codes-custom-agent-framework-changes-everything-4o4m)

### Atlas Framework Documentation
- `.claude/agents/` - All agent definitions
- `.claude/agents/rules/` - Framework rules
- `.claude/CLAUDE.md` - Main framework guide

---

**Last Updated**: 2025-01-29
**Framework Version**: Atlas 1.0
**Claude Code Version**: 2.0.55+
