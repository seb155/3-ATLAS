# ATLAS 2.0 - Plan Complet

**Créé:** 2025-12-02
**Objectif:** Système multi-agent parallèle avec sandboxing pour monorepo
**Status:** EN COURS

---

## Comment Continuer Ce Travail

### Si tu reprends dans une nouvelle session Claude Code:

```bash
# 1. Lire ce fichier en premier
cat .atlas/ATLAS-2.0-PLAN.md

# 2. Voir où on en est
cat .atlas/ATLAS-2.0-PROGRESS.md

# 3. Commande pour continuer
/0-resume
# OU dire: "Continue ATLAS 2.0 implementation from .atlas/ATLAS-2.0-PLAN.md"
```

### Fichiers clés à lire pour contexte:
1. `.atlas/ATLAS-2.0-PLAN.md` (CE FICHIER) - Plan complet
2. `.atlas/ATLAS-2.0-PROGRESS.md` - Progression détaillée
3. `.atlas/CURRENT-STATE.md` - État ATLAS v1.0
4. `CLAUDE.md` - Instructions projet

---

## Vue d'Ensemble ATLAS 2.0

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ATLAS 2.0 ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    ORCHESTRATOR LAYER (Opus)                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │   ATLAS     │  │  GENESIS    │  │ BRAINSTORM  │              │   │
│  │  │ Orchestrator│  │ Meta-Agent  │  │  Whiteboard │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼ Parallel Dispatch                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    SANDBOX POOL (FORGE)                          │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐          │   │
│  │  │  Sandbox A    │ │  Sandbox B    │ │  Sandbox C    │          │   │
│  │  │ ┌───────────┐ │ │ ┌───────────┐ │ │ ┌───────────┐ │          │   │
│  │  │ │ Backend-  │ │ │ │ Frontend- │ │ │ │ QA-Tester │ │          │   │
│  │  │ │ Builder   │ │ │ │ Builder   │ │ │ │           │ │          │   │
│  │  │ └───────────┘ │ │ └───────────┘ │ │ └───────────┘ │          │   │
│  │  │ [Worktree A]  │ │ [Worktree B]  │ │ [Worktree C]  │          │   │
│  │  └───────────────┘ └───────────────┘ └───────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              │                                          │
│                              ▼ Results                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    SHARED STATE (Redis + Files)                  │   │
│  │  • Task Queue        • Results Store       • Agent Status        │   │
│  │  • Hot Files         • Session State       • Metrics             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phases d'Implémentation

| Phase | Nom | Priorité | Durée | Dépendances |
|-------|-----|----------|-------|-------------|
| 0 | Migration Symlinks | CRITIQUE | 30 min | - |
| 1 | Parallel Agent Framework | HAUTE | 2-3h | Phase 0 |
| 2 | Git Worktrees Integration | HAUTE | 1-2h | Phase 1 |
| 3 | Sandbox Pool (FORGE) | MOYENNE | 3-4h | Phase 1, 2 |
| 4 | Monorepo Layer System | MOYENNE | 2h | Phase 0 |
| 5 | Inter-Agent Communication | BASSE | 2-3h | Phase 3 |

---

## Phase 0: Migration Symlinks → Local

### 0.1 Objectif
Supprimer le symlink `.claude/` et copier le contenu localement.

### 0.2 État Actuel
```
.claude/ → /home/seb/atlas-framework/.claude (SYMLINK)
```

### 0.3 État Cible
```
.claude/  (LOCAL DIRECTORY, tracked by git)
├── agents/
├── commands/
├── skills/
├── hooks/
└── settings.json
```

### 0.4 Commandes de Migration

```bash
# 1. Backup du contenu actuel
mkdir -p /tmp/atlas-backup
cp -rL /home/user/AXIOM/.claude /tmp/atlas-backup/

# 2. Supprimer le symlink
rm /home/user/AXIOM/.claude

# 3. Copier le contenu
cp -r /tmp/atlas-backup/.claude /home/user/AXIOM/.claude

# 4. Vérifier
ls -la /home/user/AXIOM/.claude/agents/

# 5. Commit
cd /home/user/AXIOM
git add .claude/
git commit -m "refactor: migrate ATLAS from symlink to local"
```

### 0.5 Checklist Phase 0
- [ ] Backup créé
- [ ] Symlink supprimé
- [ ] Contenu copié localement
- [ ] Vérification structure
- [ ] Git commit
- [ ] Test /0-new-session

---

## Phase 1: Parallel Agent Framework

### 1.1 Objectif
Permettre à ATLAS de lancer plusieurs agents en parallèle via le Task tool.

### 1.2 Principe Clé

Pour exécuter en parallèle avec Claude Code, tu DOIS envoyer **UN SEUL message**
avec **PLUSIEURS appels Task tool**. Si tu envoies les Task tools séquentiellement
(un par message), ils s'exécutent un après l'autre.

**Pattern Parallèle (CORRECT):**
```
Message 1:
  - Task(backend-builder, "Create API...")
  - Task(frontend-builder, "Create UI...")
  - Task(qa-tester, "Write tests...")
→ Les 3 s'exécutent EN MÊME TEMPS
```

**Pattern Séquentiel (À ÉVITER pour parallélisme):**
```
Message 1: Task(backend-builder, "Create API...")
Message 2: Task(frontend-builder, "Create UI...")
Message 3: Task(qa-tester, "Write tests...")
→ Exécution un par un
```

### 1.3 Nouveaux Agents Spécialisés

Créer dans `.claude/agents/builders/`:

#### backend-builder.md
```markdown
# Backend Builder Agent

## Role
Spécialiste développement backend Python/FastAPI.

## Model
Sonnet (balanced cost/capability)

## Capabilities
- Créer endpoints API
- Écrire services business logic
- Créer modèles SQLAlchemy
- Écrire migrations Alembic

## Context Loading
Charge automatiquement:
- apps/synapse/backend/app/main.py
- apps/synapse/backend/app/api/endpoints/
- apps/synapse/backend/app/models/

## Output Format
Retourne:
- Fichiers créés/modifiés (paths absolus)
- Résumé des changements
- Commandes à exécuter (migrations, etc.)
```

#### frontend-builder.md
```markdown
# Frontend Builder Agent

## Role
Spécialiste développement frontend React/TypeScript.

## Model
Sonnet (balanced cost/capability)

## Capabilities
- Créer composants React
- Écrire hooks personnalisés
- Intégrer avec API backend
- Styling avec Tailwind

## Context Loading
Charge automatiquement:
- apps/synapse/frontend/src/components/
- apps/synapse/frontend/src/hooks/
- apps/synapse/frontend/src/api/

## Output Format
Retourne:
- Fichiers créés/modifiés (paths absolus)
- Résumé des changements
- Dépendances à installer (si nouvelles)
```

#### qa-tester.md
```markdown
# QA Tester Agent

## Role
Spécialiste tests et validation.

## Model
Haiku (fast, cost-effective)

## Capabilities
- Écrire tests pytest (backend)
- Écrire tests vitest (frontend)
- Exécuter suites de tests
- Générer rapports coverage

## Context Loading
Charge automatiquement:
- apps/synapse/backend/tests/
- apps/synapse/frontend/src/**/*.test.ts

## Output Format
Retourne:
- Tests créés (paths)
- Résultats d'exécution
- Coverage summary
- Issues trouvées
```

### 1.4 Update atlas.md

Ajouter au fichier `.claude/agents/atlas.md`:

```markdown
## Parallel Execution Protocol

### Règles de Parallélisation

1. **Indépendance**: Ne parallélise que les tâches sans dépendances mutuelles
2. **Single Message**: Envoie tous les Task tools dans UN message
3. **Max Concurrent**: Limite à 3-5 agents parallèles
4. **Synthesis**: Attends tous les résultats avant de continuer

### Scénarios de Parallélisation

| Scénario | Agents Parallèles |
|----------|-------------------|
| Nouvelle feature full-stack | backend-builder + frontend-builder |
| Code review complet | backend-builder + frontend-builder + qa-tester |
| Exploration codebase | 3x Explore agents (different areas) |
| Bug fix + tests | backend-builder + qa-tester |

### Template de Dispatch Parallèle

Quand tu identifies une tâche parallélisable, utilise ce pattern mental:

"Je vais lancer [N] agents en parallèle:
- Agent 1: [nom] pour [tâche spécifique]
- Agent 2: [nom] pour [tâche spécifique]
- Agent 3: [nom] pour [tâche spécifique]

Ces tâches sont indépendantes car [raison].
Je les lance TOUS dans ce même message."
```

### 1.5 Checklist Phase 1
- [ ] Créer `.claude/agents/builders/` directory
- [ ] Créer backend-builder.md
- [ ] Créer frontend-builder.md
- [ ] Créer qa-tester.md
- [ ] Update atlas.md avec Parallel Execution Protocol
- [ ] Tester dispatch parallèle simple
- [ ] Documenter dans CLAUDE.md

---

## Phase 2: Git Worktrees Integration

### 2.1 Objectif
Isoler chaque agent parallèle dans son propre worktree Git pour éviter les conflits.

### 2.2 Structure Worktrees

```
/home/user/AXIOM/                    # Main worktree (orchestrator)
/home/user/AXIOM-worktrees/
├── agent-backend/                   # Backend-Builder worktree
├── agent-frontend/                  # Frontend-Builder worktree
└── agent-qa/                        # QA-Tester worktree
```

### 2.3 Script de Gestion Worktrees

Créer `.atlas/scripts/worktree-manager.sh`:

```bash
#!/bin/bash
# Worktree Manager for ATLAS 2.0 Parallel Agents

AXIOM_ROOT="/home/user/AXIOM"
WORKTREE_BASE="/home/user/AXIOM-worktrees"

create_worktree() {
    local agent_name=$1
    local branch_name="atlas-agent-$agent_name-$(date +%s)"
    local worktree_path="$WORKTREE_BASE/agent-$agent_name"

    # Create branch from current HEAD
    git -C "$AXIOM_ROOT" branch "$branch_name"

    # Create worktree
    git -C "$AXIOM_ROOT" worktree add "$worktree_path" "$branch_name"

    echo "$worktree_path"
}

cleanup_worktree() {
    local agent_name=$1
    local worktree_path="$WORKTREE_BASE/agent-$agent_name"

    if [ -d "$worktree_path" ]; then
        local branch_name=$(git -C "$worktree_path" branch --show-current)
        git -C "$AXIOM_ROOT" worktree remove "$worktree_path" --force
        git -C "$AXIOM_ROOT" branch -D "$branch_name" 2>/dev/null
    fi
}

merge_worktree() {
    local agent_name=$1
    local worktree_path="$WORKTREE_BASE/agent-$agent_name"

    if [ -d "$worktree_path" ]; then
        local branch_name=$(git -C "$worktree_path" branch --show-current)

        # Commit any changes in worktree
        git -C "$worktree_path" add -A
        git -C "$worktree_path" commit -m "Agent $agent_name: completed task" 2>/dev/null

        # Merge into main
        git -C "$AXIOM_ROOT" merge "$branch_name" --no-edit

        # Cleanup
        cleanup_worktree "$agent_name"
    fi
}

list_worktrees() {
    git -C "$AXIOM_ROOT" worktree list
}

case "$1" in
    create)  create_worktree "$2" ;;
    cleanup) cleanup_worktree "$2" ;;
    merge)   merge_worktree "$2" ;;
    list)    list_worktrees ;;
    *)       echo "Usage: $0 {create|cleanup|merge|list} [agent-name]" ;;
esac
```

### 2.4 Intégration avec Agents

Modifier le prompt des builders pour utiliser worktrees:

```markdown
## Worktree Protocol

Avant de modifier des fichiers:
1. Vérifie si tu es dans un worktree isolé
2. Si oui, travaille normalement
3. Si non, signale à l'orchestrateur

Après avoir terminé:
1. Liste tous les fichiers modifiés
2. Signale "READY_FOR_MERGE" dans ta réponse
```

### 2.5 Checklist Phase 2
- [ ] Créer `.atlas/scripts/worktree-manager.sh`
- [ ] Tester create/merge/cleanup
- [ ] Intégrer avec agent prompts
- [ ] Documenter workflow merge conflicts
- [ ] Ajouter au PATH ou alias

---

## Phase 3: Sandbox Pool (FORGE)

### 3.1 Objectif
Créer un pool de containers Docker pré-chauffés pour isolation agent.

### 3.2 Architecture Sandbox

```
FORGE Infrastructure
└── forge/sandbox/
    ├── docker-compose.sandbox.yml
    ├── Dockerfile.agent
    ├── pool-manager.py
    └── config/
        └── sandbox-config.yml
```

### 3.3 Configuration Sandbox

Créer `forge/sandbox/sandbox-config.yml`:

```yaml
# ATLAS 2.0 Sandbox Pool Configuration
version: "1.0"

pool:
  min_warm: 2           # Minimum sandboxes toujours prêts
  max_size: 5           # Maximum sandboxes simultanés
  idle_timeout: 300     # Secondes avant cleanup sandbox idle

sandbox:
  image: "axiom-agent-sandbox:latest"
  resources:
    cpu: "1"
    memory: "1Gi"
    timeout: 600        # 10 minutes max par exécution

  mounts:
    - type: "bind"
      source: "/home/user/AXIOM"
      target: "/workspace"
      readonly: false

  network:
    mode: "bridge"
    allow_internet: true

  security:
    privileged: false
    capabilities:
      drop: ["ALL"]
      add: ["CHOWN", "SETUID", "SETGID"]
```

### 3.4 Dockerfile Agent

Créer `forge/sandbox/Dockerfile.agent`:

```dockerfile
FROM python:3.11-slim

# Install base tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Python tools
RUN pip install --no-cache-dir \
    pytest \
    ruff \
    black \
    uvicorn \
    fastapi

# Install Node tools
RUN npm install -g \
    typescript \
    vitest \
    eslint

# Create workspace
WORKDIR /workspace

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command (idle wait)
CMD ["tail", "-f", "/dev/null"]
```

### 3.5 Docker Compose Sandbox

Créer `forge/sandbox/docker-compose.sandbox.yml`:

```yaml
version: "3.8"

services:
  sandbox-pool:
    build:
      context: .
      dockerfile: Dockerfile.agent
    image: axiom-agent-sandbox:latest
    deploy:
      mode: replicated
      replicas: 2
      resources:
        limits:
          cpus: "1"
          memory: 1G
    volumes:
      - ../../:/workspace:rw
      - sandbox-cache:/root/.cache
    networks:
      - forge-network
    labels:
      - "atlas.sandbox=true"
      - "atlas.pool=default"

volumes:
  sandbox-cache:

networks:
  forge-network:
    external: true
```

### 3.6 Pool Manager Script

Créer `forge/sandbox/pool-manager.py`:

```python
#!/usr/bin/env python3
"""
ATLAS 2.0 Sandbox Pool Manager
Manages pre-warmed container pool for parallel agents.
"""

import docker
import yaml
import time
import threading
from pathlib import Path

class SandboxPool:
    def __init__(self, config_path: str):
        self.client = docker.from_env()
        self.config = self._load_config(config_path)
        self.active_sandboxes = {}
        self.lock = threading.Lock()

    def _load_config(self, path: str) -> dict:
        with open(path) as f:
            return yaml.safe_load(f)

    def acquire(self, agent_name: str) -> str:
        """Get a sandbox for an agent, creating if needed."""
        with self.lock:
            # Find idle sandbox or create new
            container = self._get_or_create_sandbox()
            self.active_sandboxes[agent_name] = container.id
            return container.id

    def release(self, agent_name: str):
        """Release a sandbox back to pool."""
        with self.lock:
            if agent_name in self.active_sandboxes:
                container_id = self.active_sandboxes.pop(agent_name)
                # Reset container state
                self._reset_sandbox(container_id)

    def _get_or_create_sandbox(self):
        """Get existing idle sandbox or create new one."""
        # Find idle container
        for container in self.client.containers.list(
            filters={"label": "atlas.sandbox=true"}
        ):
            if container.id not in self.active_sandboxes.values():
                return container

        # Create new if under limit
        if len(self.active_sandboxes) < self.config["pool"]["max_size"]:
            return self._create_sandbox()

        raise RuntimeError("Sandbox pool exhausted")

    def _create_sandbox(self):
        """Create a new sandbox container."""
        return self.client.containers.run(
            "axiom-agent-sandbox:latest",
            detach=True,
            labels={"atlas.sandbox": "true"},
            volumes={
                "/home/user/AXIOM": {"bind": "/workspace", "mode": "rw"}
            },
            mem_limit="1g",
            cpu_quota=100000,
        )

    def _reset_sandbox(self, container_id: str):
        """Reset sandbox to clean state."""
        container = self.client.containers.get(container_id)
        container.exec_run("git -C /workspace checkout -- .")
        container.exec_run("git -C /workspace clean -fd")

    def status(self) -> dict:
        """Get pool status."""
        total = len(list(self.client.containers.list(
            filters={"label": "atlas.sandbox=true"}
        )))
        active = len(self.active_sandboxes)
        return {
            "total": total,
            "active": active,
            "available": total - active,
            "max": self.config["pool"]["max_size"]
        }


if __name__ == "__main__":
    import sys
    pool = SandboxPool("sandbox-config.yml")

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            print(pool.status())
        elif cmd == "acquire" and len(sys.argv) > 2:
            print(pool.acquire(sys.argv[2]))
        elif cmd == "release" and len(sys.argv) > 2:
            pool.release(sys.argv[2])
```

### 3.7 Checklist Phase 3
- [ ] Créer `forge/sandbox/` directory
- [ ] Créer Dockerfile.agent
- [ ] Créer docker-compose.sandbox.yml
- [ ] Créer sandbox-config.yml
- [ ] Créer pool-manager.py
- [ ] Build image: `docker compose build`
- [ ] Test pool: `python pool-manager.py status`
- [ ] Intégrer avec agent dispatch
- [ ] Ajouter à FORGE docker-compose principal

---

## Phase 4: Monorepo Layer System

### 4.1 Objectif
Permettre des configurations ATLAS par app avec héritage.

### 4.2 Système de Layers

```
Priority (low → high):
1. Root:     /.claude/           # Shared base
2. App:      /apps/X/.claude/    # App-specific overrides
```

### 4.3 Configuration Monorepo

Créer `.atlas/config.yml`:

```yaml
# ATLAS 2.0 Monorepo Configuration
version: "2.0"

monorepo:
  root: "."

  apps:
    synapse:
      path: "apps/synapse"
      display_name: "SYNAPSE"
      has_overrides: false
      default_builders:
        - backend-builder
        - frontend-builder
      test_command: "cd apps/synapse && npm test && pytest"

    nexus:
      path: "apps/nexus"
      display_name: "NEXUS"
      has_overrides: false
      default_builders:
        - frontend-builder
      test_command: "cd apps/nexus && npm test"

    cortex:
      path: "apps/cortex"
      display_name: "CORTEX"
      has_overrides: false
      default_builders:
        - backend-builder
      test_command: "cd apps/cortex && pytest"

layers:
  root:
    path: ".claude"
    priority: 1
    provides:
      - agents
      - commands
      - skills
      - hooks

  app:
    path: "apps/{app}/.claude"
    priority: 2
    can_override:
      - commands
      - agents/rules

parallel_agents:
  enabled: true
  max_concurrent: 3
  use_worktrees: true
  sandbox_pool: true

context:
  hot_files:
    global:
      - "CLAUDE.md"
      - ".dev/context/project-state.md"
      - ".atlas/config.yml"
    per_app:
      synapse:
        - "apps/synapse/backend/app/main.py"
        - "apps/synapse/frontend/src/App.tsx"
      nexus:
        - "apps/nexus/src/main.tsx"
```

### 4.4 Layer Resolution Logic

Ajouter à `.claude/agents/atlas.md`:

```markdown
## Layer Resolution

Quand tu cherches un fichier de configuration:

1. Vérifie d'abord `apps/{current_app}/.claude/{path}`
2. Si non trouvé, utilise `.claude/{path}`
3. Les fichiers app override complètement (pas de merge)

Exemple:
- User dans SYNAPSE demande `/test`
- Cherche: `apps/synapse/.claude/commands/test.md`
- Si non trouvé: `.claude/commands/test.md`
```

### 4.5 Checklist Phase 4
- [ ] Créer `.atlas/config.yml`
- [ ] Update atlas.md avec layer resolution
- [ ] Créer exemple override: `apps/synapse/.claude/commands/`
- [ ] Tester résolution layers
- [ ] Documenter dans CLAUDE.md

---

## Phase 5: Inter-Agent Communication

### 5.1 Objectif
Permettre aux agents de communiquer via shared state.

### 5.2 Architecture Communication

```
┌─────────────────────────────────────────────────────────────┐
│                    SHARED STATE                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  .atlas/runtime/                                     │   │
│  │  ├── tasks/                                          │   │
│  │  │   ├── task-001.json    # Task definition          │   │
│  │  │   └── task-002.json                               │   │
│  │  ├── results/                                        │   │
│  │  │   ├── task-001-result.json                        │   │
│  │  │   └── task-002-result.json                        │   │
│  │  └── status.json          # Global status            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Task Schema

```json
{
  "id": "task-001",
  "created_at": "2025-12-02T10:30:00Z",
  "agent": "backend-builder",
  "status": "running",
  "input": {
    "action": "create_endpoint",
    "endpoint": "/api/v1/metrics",
    "spec": "..."
  },
  "dependencies": [],
  "priority": 1
}
```

### 5.4 Result Schema

```json
{
  "task_id": "task-001",
  "completed_at": "2025-12-02T10:35:00Z",
  "status": "success",
  "output": {
    "files_created": [
      "apps/synapse/backend/app/api/endpoints/metrics.py"
    ],
    "files_modified": [
      "apps/synapse/backend/app/api/__init__.py"
    ],
    "summary": "Created metrics endpoint with GET/POST methods"
  },
  "next_steps": [
    "Run migrations",
    "Update frontend to consume endpoint"
  ]
}
```

### 5.5 Redis Option (Production)

Pour une implémentation plus robuste, utiliser Redis:

```yaml
# forge/docker-compose.yml (ajout)
services:
  atlas-redis:
    image: redis:7-alpine
    container_name: atlas-redis
    ports:
      - "6380:6379"
    volumes:
      - atlas-redis-data:/data
    networks:
      - forge-network

volumes:
  atlas-redis-data:
```

### 5.6 Checklist Phase 5
- [ ] Créer `.atlas/runtime/` structure
- [ ] Définir task/result schemas
- [ ] Implémenter file-based communication
- [ ] (Optional) Ajouter Redis à FORGE
- [ ] Tester communication multi-agent
- [ ] Cleanup automatique runtime/

---

## Fichiers à Créer (Résumé)

```
.claude/agents/builders/
├── backend-builder.md          # Phase 1
├── frontend-builder.md         # Phase 1
└── qa-tester.md               # Phase 1

.atlas/
├── ATLAS-2.0-PLAN.md          # CE FICHIER
├── ATLAS-2.0-PROGRESS.md      # Tracking progression
├── config.yml                 # Phase 4
├── scripts/
│   └── worktree-manager.sh    # Phase 2
└── runtime/                   # Phase 5
    ├── tasks/
    ├── results/
    └── status.json

forge/sandbox/
├── Dockerfile.agent           # Phase 3
├── docker-compose.sandbox.yml # Phase 3
├── sandbox-config.yml         # Phase 3
└── pool-manager.py           # Phase 3
```

---

## Commandes Utiles

```bash
# Phase 0: Migration
rm .claude && cp -r /tmp/atlas-backup/.claude .

# Phase 2: Worktrees
.atlas/scripts/worktree-manager.sh create backend
.atlas/scripts/worktree-manager.sh list
.atlas/scripts/worktree-manager.sh merge backend

# Phase 3: Sandbox
cd forge/sandbox
docker compose build
docker compose up -d
python pool-manager.py status

# Debug
cat .atlas/runtime/status.json
git worktree list
docker ps --filter "label=atlas.sandbox=true"
```

---

## Success Criteria

| Phase | Critère de Succès |
|-------|-------------------|
| 0 | `.claude/` est local, git tracked, /0-new-session fonctionne |
| 1 | 3 agents peuvent être lancés en parallèle dans un message |
| 2 | Chaque agent travaille dans son worktree isolé |
| 3 | Pool de 2+ containers pré-chauffés disponibles |
| 4 | Override per-app fonctionne (layer resolution) |
| 5 | Agents peuvent lire les résultats des autres |

---

## Notes de Session

### 2025-12-02 - Création du Plan
- Analyse architecture actuelle ATLAS v1.0
- Comparaison avec best practices 2025
- Identification gaps: parallélisme, sandbox, worktrees
- Création plan complet 5 phases
- Décision: supprimer symlinks pour monorepo-native
