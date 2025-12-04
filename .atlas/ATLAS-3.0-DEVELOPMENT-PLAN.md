# ATLAS 3.0 - Development Plan

**Created:** 2024-12-04
**Author:** Claude + Seb
**Status:** PLANNING
**Target:** Q1 2025

---

## Table of Contents

1. [Vision & Context](#vision--context)
2. [Repository Strategy](#repository-strategy)
3. [WSL Environment](#wsl-environment)
4. [Architecture](#architecture)
5. [Miessler Suite Integration](#miessler-suite-integration)
6. [Development Phases](#development-phases)
7. [Sync Policy](#sync-policy)
8. [Ideas & Notes](#ideas--notes)

---

## Vision & Context

### What is ATLAS 3.0?

ATLAS 3.0 is the next evolution of the ATLAS AI orchestration framework, combining:

1. **PAI (Personal AI Infrastructure)** - Daniel Miessler's proven foundation
2. **Miessler Suite** - Fabric, Telos, Substrate, Daemon, SecLists
3. **AXIOM-specific features** - Monorepo support, multi-app orchestration

### Why ATLAS 3.0?

| Problem with ATLAS 2.x | Solution in ATLAS 3.0 |
|------------------------|----------------------|
| Custom architecture | Proven PAI foundation |
| No pattern library | Fabric 242+ patterns |
| No knowledge base | Substrate integration |
| No purpose docs | Telos Context Files |
| No public API | Daemon MCP server |
| No security testing | SecLists integration |

### Core Principles

1. **Don't reinvent** - Use PAI as-is, don't denature it
2. **Explicit sync** - No automatic upstream pulls
3. **Portable** - Works on WSL1, WSL2, Linux bare metal
4. **Isolated** - Develop in separate WSL instance
5. **Documented** - Everything written down

---

## Repository Strategy

### Current State

```
GitHub: seb155/atlas-framework
└── Current ATLAS implementation (symlink-based)
```

### Target State

```
GitHub Repositories:
│
├── seb155/2-ATLAS                    # PRODUCTION
│   ├── Renamed from atlas-framework
│   ├── ATLAS 2.x stable
│   └── Used by AXIOM currently
│
├── seb155/3-ATLAS                    # DEVELOPMENT
│   ├── Fork of 2-ATLAS
│   ├── ATLAS 3.0 development
│   ├── PAI + Miessler Suite
│   └── Complete rewrite
│
├── seb155/Personal_AI_Infrastructure # UPSTREAM FORK
│   ├── Fork of danielmiessler/PAI
│   ├── For tracking upstream changes
│   └── Manual sync only
│
└── seb155/fabric                     # UPSTREAM FORK
    ├── Fork of danielmiessler/fabric
    ├── For tracking upstream changes
    └── Manual sync only
```

### Steps to Create

```bash
# Step 1: Rename atlas-framework → 2-ATLAS
# (Do this in GitHub Settings → Repository name)

# Step 2: Fork 2-ATLAS → 3-ATLAS
# (Do this in GitHub: Fork button)

# Step 3: Fork Miessler repos
# - Fork danielmiessler/Personal_AI_Infrastructure → seb155/Personal_AI_Infrastructure
# - Fork danielmiessler/fabric → seb155/fabric

# Step 4: Clone 3-ATLAS for development
git clone https://github.com/seb155/3-ATLAS.git ~/ATLAS-3
cd ~/ATLAS-3

# Step 5: Add upstream remotes to forks
cd ~/seb155-pai-fork
git remote add upstream https://github.com/danielmiessler/Personal_AI_Infrastructure.git

cd ~/seb155-fabric-fork
git remote add upstream https://github.com/danielmiessler/fabric.git
```

---

## WSL Environment

### WSL1 vs WSL2 Comparison

| Aspect | WSL1 | WSL2 | Winner |
|--------|------|------|--------|
| **Architecture** | Translation layer | Real Linux kernel (VM) | WSL2 |
| **Linux FS Performance** | Good | ~87% of bare metal | WSL2 |
| **Windows FS Performance** | Fast | 5x slower! | WSL1 |
| **Docker** | Not supported | Native | WSL2 |
| **Syscall compatibility** | ~80% | 100% | WSL2 |
| **RAM usage** | Low | Higher | WSL1 |
| **GPU support** | No | Yes | WSL2 |
| **systemd** | No | Yes (recent) | WSL2 |

### Recommendation: WSL2

**WSL2 is recommended for ATLAS 3.0 because:**

- Docker support (for future sandboxes)
- Better syscall compatibility (100%)
- ~24% better performance than WSL1
- GPU support for AI/ML if needed
- systemd support for services

**IMPORTANT:** Keep files in Linux filesystem (`/home/...`), NOT on `/mnt/c/...`

### WSL2 Setup for ATLAS 3.0 Development

#### Option A: New Distribution (Recommended)

```powershell
# PowerShell (Run as Administrator)

# 1. List available distributions
wsl --list --online

# 2. Install fresh Ubuntu 24.04 with custom name
wsl --install Ubuntu-24.04

# 3. Or import a custom instance
wsl --import ATLAS3-Dev C:\WSL\ATLAS3-Dev .\ubuntu-24.04.tar.gz

# 4. Set WSL2 as default version
wsl --set-default-version 2

# 5. Verify
wsl -l -v
```

#### Option B: Automated Script

```powershell
# setup-atlas3-wsl.ps1

$WSL_NAME = "ATLAS3-Dev"
$WSL_PATH = "C:\WSL\$WSL_NAME"

Write-Host "Setting up ATLAS 3.0 WSL Environment..." -ForegroundColor Cyan

# Check WSL version
wsl --status

# Create directory
New-Item -ItemType Directory -Path $WSL_PATH -Force | Out-Null

# Install Ubuntu
wsl --install -d Ubuntu-24.04

Write-Host ""
Write-Host "WSL instance ready!" -ForegroundColor Green
Write-Host "Next: wsl -d Ubuntu-24.04" -ForegroundColor Yellow
```

### Inside WSL2: Initial Setup

```bash
#!/bin/bash
# Run this inside the new WSL2 instance

# Update system
sudo apt update && sudo apt upgrade -y

# Install essentials
sudo apt install -y \
    git \
    curl \
    wget \
    build-essential \
    python3 \
    python3-pip \
    nodejs \
    npm

# Install Bun (PAI requirement)
curl -fsSL https://bun.sh/install | bash
source ~/.bashrc

# Install Claude Code
npm install -g @anthropic-ai/claude-code

# Verify installations
echo "Git: $(git --version)"
echo "Bun: $(bun --version)"
echo "Claude: $(claude --version 2>/dev/null || echo 'Run claude to setup')"

# Clone ATLAS 3.0
git clone https://github.com/seb155/3-ATLAS.git ~/ATLAS-3
cd ~/ATLAS-3

echo ""
echo "Setup complete! Run: cd ~/ATLAS-3 && claude"
```

---

## Architecture

### Directory Structure

```
3-ATLAS/                              # Repository root
│
├── README.md                         # Project overview
├── LICENSE                           # MIT
├── install.sh                        # One-liner installer
│
├── docs/                             # Documentation
│   ├── PLAN.md                       # This file (symlink)
│   ├── CONTEXT.md                    # Project context & history
│   ├── IDEAS.md                      # Ideas backlog
│   ├── DECISIONS.md                  # Architecture Decision Records
│   └── WSL-SETUP.md                  # WSL setup guide
│
├── .atlas/                           # ATLAS 3.0 Core
│   │
│   ├── VERSION                       # "3.0.0-dev"
│   ├── CONSTITUTION.md               # PAI philosophy
│   │
│   ├── config/
│   │   ├── settings.json             # PAI settings
│   │   ├── identity.yml              # AI identity (DA name)
│   │   └── platform.yml              # Platform detection config
│   │
│   ├── core/                         # PAI CORE SYSTEMS
│   │   ├── skills/                   # Skills System (3-tier)
│   │   │   ├── CORE/
│   │   │   │   ├── SKILL.md
│   │   │   │   └── SkillSystem.md
│   │   │   ├── observability/
│   │   │   ├── research/
│   │   │   └── create-skill/
│   │   │
│   │   ├── hooks/                    # Hooks System
│   │   │   ├── PreToolUse/
│   │   │   ├── PostToolUse/
│   │   │   └── UserFeedback/
│   │   │
│   │   ├── history/                  # UOCS History System
│   │   │   ├── sessions/             # Markdown summaries
│   │   │   └── logs/                 # JSONL logs
│   │   │
│   │   ├── agents/                   # Agent Personalities
│   │   │   └── personalities/
│   │   │
│   │   └── voice/                    # Voice Server (ElevenLabs)
│   │
│   ├── integrations/                 # MIESSLER SUITE
│   │   ├── fabric/
│   │   │   ├── README.md
│   │   │   ├── config.yml
│   │   │   ├── patterns/             # Vendored from upstream
│   │   │   └── custom/               # Custom patterns
│   │   │
│   │   ├── telos/
│   │   │   ├── README.md
│   │   │   ├── templates/
│   │   │   └── projects/             # Project TCFs
│   │   │
│   │   ├── substrate/
│   │   │   ├── README.md
│   │   │   ├── templates/
│   │   │   └── knowledge/            # Knowledge base
│   │   │
│   │   ├── daemon/
│   │   │   ├── README.md
│   │   │   └── daemon.md             # Public data file
│   │   │
│   │   └── seclists/
│   │       ├── README.md
│   │       └── config.yml
│   │
│   ├── upstream/                     # VENDORED SOURCES
│   │   ├── README.md                 # "SYNC REQUIRES EXPLICIT APPROVAL"
│   │   ├── SYNC_LOG.md               # Sync history
│   │   ├── check-updates.sh          # Check for upstream changes
│   │   ├── request-sync.sh           # Create sync request
│   │   └── approve-sync.sh           # Apply approved sync
│   │
│   └── tools/
│       ├── setup/
│       │   └── bootstrap.sh
│       └── platform/
│           ├── detect.sh
│           └── wsl-setup.sh
│
├── .claude/                          # Claude Code config
│   ├── commands/
│   ├── settings.json
│   └── hooks/
│
└── tests/                            # Test suite
    ├── test-skills.sh
    ├── test-hooks.sh
    └── test-fabric.sh
```

### Component Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ATLAS 3.0 COMPONENT DIAGRAM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                           ┌─────────────────┐                               │
│                           │   Claude Code    │                               │
│                           │   (Interface)    │                               │
│                           └────────┬────────┘                               │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         ATLAS 3.0 CORE                               │    │
│  │  ┌─────────────────────────────────────────────────────────────┐    │    │
│  │  │                    PAI FOUNDATION                            │    │    │
│  │  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │    │    │
│  │  │  │ Skills  │  │  Hooks  │  │ History │  │ Agents  │        │    │    │
│  │  │  │ System  │  │ System  │  │  UOCS   │  │Personae │        │    │    │
│  │  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │    │    │
│  │  │       │            │            │            │              │    │    │
│  │  │       └────────────┴────────────┴────────────┘              │    │    │
│  │  │                         │                                    │    │    │
│  │  └─────────────────────────┼────────────────────────────────────┘    │    │
│  │                            │                                          │    │
│  │  ┌─────────────────────────┼────────────────────────────────────┐    │    │
│  │  │              MIESSLER SUITE INTEGRATIONS                      │    │    │
│  │  │                         │                                     │    │    │
│  │  │  ┌──────────┐  ┌───────┴───────┐  ┌───────────┐              │    │    │
│  │  │  │  Fabric  │  │   Substrate   │  │   Telos   │              │    │    │
│  │  │  │ Patterns │  │  Knowledge    │  │  Purpose  │              │    │    │
│  │  │  └──────────┘  └───────────────┘  └───────────┘              │    │    │
│  │  │                                                               │    │    │
│  │  │  ┌──────────┐  ┌───────────────┐                             │    │    │
│  │  │  │  Daemon  │  │   SecLists    │                             │    │    │
│  │  │  │   API    │  │   Security    │                             │    │    │
│  │  │  └──────────┘  └───────────────┘                             │    │    │
│  │  │                                                               │    │    │
│  │  └───────────────────────────────────────────────────────────────┘    │    │
│  │                                                                        │    │
│  └────────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Miessler Suite Integration

### Overview

| Project | Purpose | Integration Level |
|---------|---------|-------------------|
| **PAI** | Core AI infrastructure | Full (foundation) |
| **Fabric** | 242+ AI patterns | Full (skills) |
| **Telos** | Purpose documentation | Templates + custom |
| **Substrate** | Knowledge base | Templates + custom |
| **Daemon** | Public API | Optional |
| **SecLists** | Security testing | Config only (external) |

### Integration Details

#### 1. PAI (Personal AI Infrastructure)

**Source:** `danielmiessler/Personal_AI_Infrastructure`
**Integration:** Vendor copy (manual sync)

```
What to copy:
├── .claude/skills/CORE/          → .atlas/core/skills/CORE/
├── .claude/skills/observability/ → .atlas/core/skills/observability/
├── .claude/skills/research/      → .atlas/core/skills/research/
├── .claude/hooks/                → .atlas/core/hooks/
├── CONSTITUTION.md               → .atlas/CONSTITUTION.md
└── tools/setup/                  → .atlas/tools/setup/
```

#### 2. Fabric

**Source:** `danielmiessler/fabric`
**Integration:** Patterns only (vendor copy)

```
What to copy:
└── patterns/                     → .atlas/integrations/fabric/patterns/

Custom patterns:
└── .atlas/integrations/fabric/custom/
    ├── axiom_code_review/
    ├── axiom_api_docs/
    └── axiom_security_audit/
```

#### 3. Telos

**Source:** `danielmiessler/Telos`
**Integration:** Templates only

```
What to copy:
├── corporate_telos.md            → .atlas/integrations/telos/templates/
└── personal_telos.md             → .atlas/integrations/telos/templates/

Custom TCFs:
└── .atlas/integrations/telos/projects/
    ├── atlas.telos.md            # ATLAS 3.0 purpose
    └── (future project TCFs)
```

#### 4. Substrate

**Source:** `danielmiessler/Substrate`
**Integration:** Structure only

```
What to copy:
├── GETTING_STARTED.md            → .atlas/integrations/substrate/
└── Component templates (17 types)

Custom knowledge:
└── .atlas/integrations/substrate/knowledge/
    ├── Problems/
    ├── Solutions/
    └── Data/
```

#### 5. Daemon

**Source:** `danielmiessler/Daemon`
**Integration:** Optional (structure only)

```
What to copy:
└── daemon.md template            → .atlas/integrations/daemon/

Custom daemon:
└── .atlas/integrations/daemon/atlas.daemon.md
```

#### 6. SecLists

**Source:** `danielmiessler/SecLists`
**Integration:** External reference only (too large to vendor)

```
Config only:
└── .atlas/integrations/seclists/config.yml
    seclists:
      path: "~/.cache/seclists"
      repo: "https://github.com/danielmiessler/SecLists"
```

---

## Development Phases

### Phase 0: Repository Setup
**Duration:** 1 day
**Status:** TODO

Tasks:
- [ ] Rename `atlas-framework` → `2-ATLAS` on GitHub
- [ ] Fork `2-ATLAS` → `3-ATLAS`
- [ ] Fork `danielmiessler/Personal_AI_Infrastructure`
- [ ] Fork `danielmiessler/fabric`
- [ ] Create WSL2 instance "ATLAS3-Dev"
- [ ] Clone `3-ATLAS` in WSL2

### Phase 1: PAI Core
**Duration:** 1 week
**Status:** TODO

Tasks:
- [ ] Vendor copy PAI core systems
- [ ] Setup Skills System (3-tier)
- [ ] Setup Hooks System
- [ ] Setup History/UOCS System
- [ ] Setup bootstrap wizard
- [ ] Test basic functionality

### Phase 2: Miessler Suite
**Duration:** 1 week
**Status:** TODO

Tasks:
- [ ] Vendor Fabric patterns
- [ ] Create Telos templates
- [ ] Create Substrate structure
- [ ] Setup Daemon template
- [ ] Configure SecLists reference
- [ ] Test integrations

### Phase 3: Platform Support
**Duration:** 3 days
**Status:** TODO

Tasks:
- [ ] Platform detection script
- [ ] WSL1 compatibility
- [ ] WSL2 optimization
- [ ] Linux bare metal support
- [ ] One-liner installer
- [ ] Test on multiple platforms

### Phase 4: Documentation & Testing
**Duration:** 3 days
**Status:** TODO

Tasks:
- [ ] Complete all README files
- [ ] Write user guide
- [ ] Create test suite
- [ ] Test in fresh WSL2
- [ ] Document known issues

### Phase 5: Future (Post-Launch)
**Status:** PLANNING

Ideas for later:
- [ ] Server deployment (pve1, pve2)
- [ ] Inter-agent JSON schemas (from ATLAS 2.x)
- [ ] Bidirectional sync tools
- [ ] Web dashboard
- [ ] Voice integration

---

## Sync Policy

### Rules

1. **NO automatic sync** - All upstream changes require explicit approval
2. **Check before sync** - Review what changed upstream
3. **Request sync** - Create a sync request file
4. **Approve sync** - Manual approval required
5. **Log all syncs** - Keep history in SYNC_LOG.md

### Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                   UPSTREAM SYNC WORKFLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: CHECK                                                   │
│  ──────────────                                                  │
│  $ ./upstream/check-updates.sh                                   │
│  Output: "PAI: 5 new commits, Fabric: 2 new commits"            │
│                                                                  │
│  Step 2: REVIEW                                                  │
│  ─────────────                                                   │
│  $ ./upstream/check-updates.sh --diff pai                       │
│  Output: Shows actual changes                                    │
│                                                                  │
│  Step 3: REQUEST (Optional - creates formal request)            │
│  ────────────────                                                │
│  $ ./upstream/request-sync.sh pai                                │
│  Creates: SYNC_REQUEST_2024-12-04_pai.md                        │
│                                                                  │
│  Step 4: APPROVE                                                 │
│  ────────────────                                                │
│  $ ./upstream/approve-sync.sh pai                                │
│  - Downloads changes                                             │
│  - Applies to local                                              │
│  - Logs to SYNC_LOG.md                                          │
│                                                                  │
│  ⚠️  YOU MUST EXPLICITLY RUN APPROVE                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Sync Scripts

```bash
# check-updates.sh
#!/bin/bash
echo "Checking upstream repositories..."

cd ~/.atlas-upstream/pai
git fetch upstream --dry-run
BEHIND=$(git rev-list HEAD..upstream/main --count)
echo "PAI: $BEHIND commits behind upstream"

cd ~/.atlas-upstream/fabric
git fetch upstream --dry-run
BEHIND=$(git rev-list HEAD..upstream/main --count)
echo "Fabric: $BEHIND commits behind upstream"
```

```bash
# approve-sync.sh
#!/bin/bash
REPO=$1
DATE=$(date +%Y-%m-%d)

read -p "⚠️  SYNC REQUIRES YOUR EXPLICIT APPROVAL. Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Sync cancelled."
    exit 0
fi

echo "Syncing $REPO..."
cd ~/.atlas-upstream/$REPO
git fetch upstream
git merge upstream/main

# Log the sync
echo "| $DATE | $REPO | $(git rev-parse --short HEAD) | Manual approval |" >> ~/ATLAS-3/.atlas/upstream/SYNC_LOG.md

echo "✅ Sync complete. Logged to SYNC_LOG.md"
```

---

## Ideas & Notes

### Ideas Backlog

#### High Priority
- [ ] Fabric skill runner (`/fabric <pattern>`)
- [ ] Telos viewer (`/telos show`)
- [ ] Knowledge query (`/knowledge search <query>`)

#### Medium Priority
- [ ] Custom pattern creator
- [ ] Substrate auto-linking
- [ ] Session templates

#### Low Priority / Future
- [ ] Web dashboard for observability
- [ ] Voice commands (ElevenLabs)
- [ ] Daemon MCP server
- [ ] Multi-instance coordination

### Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2024-12-04 | Use WSL2 over WSL1 | Docker support, better performance |
| 2024-12-04 | No ATLAS 2.x JSON schemas | Keep PAI pure, add later if needed |
| 2024-12-04 | Explicit sync only | Maintain control over upstream changes |
| 2024-12-04 | Fork strategy | Allow upstream tracking without auto-merge |

### Open Questions

1. Should we support WSL1 at all, or WSL2 only?
2. How to handle Fabric pattern updates (frequent changes)?
3. Should Daemon be included in MVP or deferred?

### Notes

```
2024-12-04 - Initial planning session
- Analyzed PAI, Fabric, Telos, Substrate, Daemon, SecLists
- Compared WSL1 vs WSL2 (WSL2 wins)
- Decided on fork strategy for upstream tracking
- Explicit sync approval is critical
- ATLAS 2.x JSON schemas deferred (maybe never needed)
```

---

## Quick Reference

### Commands

```bash
# Setup new WSL2 environment
wsl --install Ubuntu-24.04

# Clone ATLAS 3.0
git clone https://github.com/seb155/3-ATLAS.git ~/ATLAS-3

# Check upstream updates
./upstream/check-updates.sh

# Request sync (creates approval request)
./upstream/request-sync.sh pai

# Approve sync (requires explicit confirmation)
./upstream/approve-sync.sh pai

# Run ATLAS 3.0
cd ~/ATLAS-3 && claude
```

### Key Files

| File | Purpose |
|------|---------|
| `docs/PLAN.md` | This document |
| `.atlas/VERSION` | Current version |
| `.atlas/CONSTITUTION.md` | PAI philosophy |
| `.atlas/upstream/SYNC_LOG.md` | Sync history |
| `.atlas/config/settings.json` | Main config |

### Links

- [PAI Repository](https://github.com/danielmiessler/Personal_AI_Infrastructure)
- [Fabric Repository](https://github.com/danielmiessler/fabric)
- [Telos Repository](https://github.com/danielmiessler/Telos)
- [Substrate Repository](https://github.com/danielmiessler/Substrate)
- [Daemon Repository](https://github.com/danielmiessler/Daemon)
- [SecLists Repository](https://github.com/danielmiessler/SecLists)
- [WSL Documentation](https://learn.microsoft.com/en-us/windows/wsl/)

---

**End of Document**

*Last updated: 2024-12-04*
