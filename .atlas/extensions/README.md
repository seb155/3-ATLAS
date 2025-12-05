# ATLAS 3.0 Extensions

Extensions preserve ATLAS v2.x capabilities while building on PAI foundation.

## Components

### sessions/
Session management ported from ATLAS v2.x:
- Lifecycle tracking
- Checkpoint system
- Recovery after /compact

### routing/
Model routing engine:
- Haiku (60%) - Simple tasks
- Sonnet (30%) - Code, planning
- Opus (10%) - Architecture

### layering/
Project override system:
- Framework defaults
- Project customization
- User preferences

### multiproject/
Cross-project support:
- AXIOM monorepo compatibility
- Project switching
- Shared context

## Migration from v2.x

Extensions ensure backward compatibility with ATLAS v2.x commands:
- `/0-session-*` → `/session`
- `/0-view-*` → `/view`
- `/9-git-ship` → `/ship`

See: `.atlas/ATLAS-3.0-DETAILED-PLAN.md` Section 6 (Mapping Commandes)
