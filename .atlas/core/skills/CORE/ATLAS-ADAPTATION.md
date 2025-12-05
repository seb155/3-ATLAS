# ATLAS 3.0 Adaptation Notes

This directory contains PAI (Personal AI Infrastructure) core skills vendored from:
- Source: `danielmiessler/Personal_AI_Infrastructure`
- Fork: `seb155/Personal_AI_Infrastructure`
- Sync Date: 2025-12-04

## Adaptations for ATLAS

### Environment Variables
- `PAI_DIR` → `ATLAS_DIR` (optional, PAI_DIR still supported)
- `DA` → Digital Assistant name (unchanged)

### Response Format
ATLAS v3 uses PAI's mandatory response format with STORY EXPLANATION.

### Security
- Private repo: `.pai` or `.atlas` (local)
- Public repo: Sanitized, generic code only

### Stack Preferences
- TypeScript > Python (same as PAI)
- Bun for JS/TS (same as PAI)
- uv for Python (same as PAI)

## Files

| File | Purpose | Adapted |
|------|---------|---------|
| CONSTITUTION.md | Core philosophy | No changes |
| SKILL.md | Skill system reference | No changes |
| SkillSystem.md | Skill architecture | Minor (paths) |
| HookSystem.md | Hook documentation | No changes |
| HistorySystem.md | UOCS documentation | No changes |

## Sync Policy

**DO NOT MODIFY VENDORED FILES DIRECTLY.**

To update from upstream:
```bash
cd ~/.atlas-upstream/pai
git pull upstream main
# Review changes, then copy to .atlas/core/skills/CORE/
```
