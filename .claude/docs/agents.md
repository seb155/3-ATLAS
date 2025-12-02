# AI Agents System

## Implemented Agents

| Agent | File | Purpose |
|-------|------|---------|
| **ATLAS** | `.claude/agents/atlas.md` | Main orchestrator |
| **DevOps Manager** | `.claude/agents/devops-manager.md` | Infrastructure |
| **Brainstorm** | `.claude/agents/brainstorm.md` | Creative sessions |
| **Backend Builder** | `.claude/agents/builders/backend-builder.md` | Python/FastAPI |
| **Frontend Builder** | `.claude/agents/builders/frontend-builder.md` | React/TypeScript |
| **QA Tester** | `.claude/agents/builders/qa-tester.md` | Tests/validation |

## Slash Commands

| Command | Mode | Purpose |
|---------|------|---------|
| `/0-new-session` | FULL | Start new day with app review |
| `/0-next` | QUICK | Continue quickly |
| `/0-resume` | RECOVERY | Resume after /compact |
| `/0-ship` | - | Git workflow (test + commit + push) |
| `/0-progress` | - | Roadmap overview |
| `/0-dashboard` | - | Session status |

## Skills

| Skill | File | Purpose |
|-------|------|---------|
| `infra` | `.claude/skills/infra.md` | Infrastructure status |
| `brainstorm` | `.claude/skills/brainstorm.md` | Whiteboard mode |

## Hooks

| Hook | Type | Purpose |
|------|------|---------|
| Session Start | PreToolUse | Load context |
| Pre-Commit | PreToolUse | Validate before commit |
| Context Update | PostToolUse | Update hot-files |

## Agent Rules

| Rule | File | Purpose |
|------|------|---------|
| 10 | `10-traefik-routing.md` | Traefik routing |
| 11 | `11-url-registry.md` | URL management |
| 12 | `12-docker-networking.md` | Docker network |
| 20 | `20-protected-docs.md` | Protected documents |

## ATLAS Development

| File | Purpose |
|------|---------|
| `.atlas/CURRENT-STATE.md` | Implementation state |
| `.atlas/ROADMAP.md` | Development plan |
| `.atlas/sessions/` | Session logs |
| `.atlas/config.yml` | ATLAS 2.0 configuration |

## Status Line

```
<< OPUS >> --- [ AXIOM/backend ] --- < master*3 > --- { A:1/2 } --- $0.42 --- 5m32s
```

| Section | Description |
|---------|-------------|
| `<< OPUS >>` | Active model |
| `[ AXIOM/backend ]` | App + directory |
| `< master*3 >` | Branch + modified files |
| `{ A:1/2 }` | Agents: running/total |
| `$0.42` | Session cost |
| `5m32s` | Session duration |

**Status file:** `.claude/context/agent-status.json`
