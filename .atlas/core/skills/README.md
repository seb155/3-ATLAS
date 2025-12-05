# ATLAS 3.0 Skills System

Based on PAI (Personal AI Infrastructure) by Daniel Miessler.

## 3-Tier Resolution

```
User Request → TIER 1 (CORE) → TIER 2 (Domain) → TIER 3 (Custom)
```

### Tier 1: CORE (PAI Foundation)
- Location: `core/skills/CORE/`
- Status: **IMMUTABLE** (vendored from PAI)
- Contains: CONSTITUTION, SkillSystem, HookSystem, etc.

### Tier 2: Domain (Fabric Patterns)
- Location: `integrations/fabric/patterns/`
- Status: **VENDORED** (periodic sync from upstream)
- Contains: 248+ AI patterns (summarize, extract_wisdom, etc.)

### Tier 3: Custom (User Skills)
- Location: `extensions/skills/` or `integrations/fabric/custom/`
- Status: **EDITABLE**
- Contains: Project-specific and user-created skills

## Skill Invocation

```
# Core skills (auto-loaded)
skill: CORE

# Fabric patterns
skill: fabric:summarize
skill: fabric:extract_wisdom

# Custom skills
skill: custom:my-skill
```

## Creating New Skills

Use the `Createskill` meta-skill:
```
skill: Createskill
```

See: `Createskill/Createskill.md`
