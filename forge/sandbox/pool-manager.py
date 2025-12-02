#!/usr/bin/env python3
"""
ATLAS 2.0 - Sandbox Pool Manager

Manages pre-warmed Docker containers for parallel agent execution.

Usage:
    python pool-manager.py status              # Show pool status
    python pool-manager.py acquire <agent>     # Get sandbox for agent
    python pool-manager.py release <agent>     # Release sandbox
    python pool-manager.py exec <agent> <cmd>  # Execute command in sandbox
    python pool-manager.py warm                # Pre-warm pool
    python pool-manager.py cleanup             # Cleanup idle sandboxes
"""

import subprocess
import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Configuration
SCRIPT_DIR = Path(__file__).parent
AXIOM_ROOT = SCRIPT_DIR.parent.parent
RUNTIME_DIR = AXIOM_ROOT / ".atlas" / "runtime"
CONFIG_FILE = SCRIPT_DIR / "sandbox-config.yml"

# Sandbox labels
SANDBOX_LABEL = "atlas.sandbox=true"


class SandboxPool:
    """Manages pool of Docker sandbox containers."""

    def __init__(self):
        self.config = self._load_config()
        self._ensure_runtime_dir()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            import yaml
            with open(CONFIG_FILE) as f:
                return yaml.safe_load(f)
        except ImportError:
            # Fallback if PyYAML not installed
            return {
                "pool": {"min_warm": 2, "max_size": 5, "idle_timeout": 300},
                "sandbox": {"image": "axiom-agent-sandbox:latest"}
            }
        except FileNotFoundError:
            return {
                "pool": {"min_warm": 2, "max_size": 5, "idle_timeout": 300},
                "sandbox": {"image": "axiom-agent-sandbox:latest"}
            }

    def _ensure_runtime_dir(self):
        """Ensure runtime directory exists."""
        (RUNTIME_DIR / "sandboxes").mkdir(parents=True, exist_ok=True)

    def _run_docker(self, *args) -> subprocess.CompletedProcess:
        """Run docker command and return result."""
        cmd = ["docker"] + list(args)
        return subprocess.run(cmd, capture_output=True, text=True)

    def _get_containers(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Get list of sandbox containers."""
        filter_args = [f"--filter=label={SANDBOX_LABEL}"]
        if filters:
            for key, value in filters.items():
                filter_args.append(f"--filter={key}={value}")

        result = self._run_docker(
            "ps", "-a", "--format", "{{json .}}", *filter_args
        )

        containers = []
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line:
                    try:
                        containers.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return containers

    def status(self) -> Dict[str, Any]:
        """Get current pool status."""
        containers = self._get_containers()

        running = [c for c in containers if c.get("State") == "running"]
        stopped = [c for c in containers if c.get("State") != "running"]

        # Get assigned agents from runtime files
        assigned = {}
        sandbox_dir = RUNTIME_DIR / "sandboxes"
        if sandbox_dir.exists():
            for f in sandbox_dir.glob("*.json"):
                try:
                    with open(f) as fp:
                        data = json.load(fp)
                        if data.get("status") == "active":
                            assigned[data.get("agent")] = data
                except:
                    pass

        return {
            "timestamp": datetime.now().isoformat(),
            "pool": {
                "total": len(containers),
                "running": len(running),
                "stopped": len(stopped),
                "available": len(running) - len(assigned),
                "assigned": len(assigned),
                "max_size": self.config.get("pool", {}).get("max_size", 5)
            },
            "containers": [
                {
                    "id": c.get("ID", "")[:12],
                    "name": c.get("Names"),
                    "state": c.get("State"),
                    "status": c.get("Status"),
                    "image": c.get("Image")
                }
                for c in containers
            ],
            "assigned_agents": list(assigned.keys())
        }

    def acquire(self, agent_name: str) -> Optional[str]:
        """Acquire a sandbox for an agent."""
        # Check if agent already has a sandbox
        sandbox_file = RUNTIME_DIR / "sandboxes" / f"{agent_name}.json"
        if sandbox_file.exists():
            with open(sandbox_file) as f:
                data = json.load(f)
                if data.get("status") == "active":
                    print(f"Agent {agent_name} already has sandbox: {data.get('container_id')}")
                    return data.get("container_id")

        # Find available container or create new one
        containers = self._get_containers({"status": "running"})

        # Get already assigned container IDs
        assigned_ids = set()
        sandbox_dir = RUNTIME_DIR / "sandboxes"
        if sandbox_dir.exists():
            for f in sandbox_dir.glob("*.json"):
                try:
                    with open(f) as fp:
                        data = json.load(fp)
                        if data.get("status") == "active":
                            assigned_ids.add(data.get("container_id"))
                except:
                    pass

        # Find first available container
        container_id = None
        for c in containers:
            cid = c.get("ID", "")[:12]
            if cid not in assigned_ids:
                container_id = cid
                break

        # If no available container, try to create one
        if not container_id:
            if len(containers) >= self.config.get("pool", {}).get("max_size", 5):
                print(f"ERROR: Pool exhausted (max {self.config.get('pool', {}).get('max_size', 5)})")
                return None

            # Create new container
            container_id = self._create_sandbox(agent_name)

        if container_id:
            # Record assignment
            with open(sandbox_file, "w") as f:
                json.dump({
                    "agent": agent_name,
                    "container_id": container_id,
                    "status": "active",
                    "acquired_at": datetime.now().isoformat()
                }, f, indent=2)

            print(f"Sandbox acquired for {agent_name}: {container_id}")
            return container_id

        return None

    def release(self, agent_name: str) -> bool:
        """Release a sandbox back to pool."""
        sandbox_file = RUNTIME_DIR / "sandboxes" / f"{agent_name}.json"

        if not sandbox_file.exists():
            print(f"No sandbox found for agent: {agent_name}")
            return False

        with open(sandbox_file) as f:
            data = json.load(f)

        container_id = data.get("container_id")

        # Reset container state (git clean)
        self._run_docker(
            "exec", container_id,
            "git", "-C", "/workspace", "checkout", "--", "."
        )
        self._run_docker(
            "exec", container_id,
            "git", "-C", "/workspace", "clean", "-fd"
        )

        # Update status
        data["status"] = "released"
        data["released_at"] = datetime.now().isoformat()
        with open(sandbox_file, "w") as f:
            json.dump(data, f, indent=2)

        # Remove assignment file
        sandbox_file.unlink()

        print(f"Sandbox released for {agent_name}: {container_id}")
        return True

    def exec_command(self, agent_name: str, command: List[str]) -> int:
        """Execute command in agent's sandbox."""
        sandbox_file = RUNTIME_DIR / "sandboxes" / f"{agent_name}.json"

        if not sandbox_file.exists():
            print(f"No sandbox found for agent: {agent_name}")
            return 1

        with open(sandbox_file) as f:
            data = json.load(f)

        container_id = data.get("container_id")

        # Execute command
        result = self._run_docker("exec", container_id, *command)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        return result.returncode

    def warm(self) -> int:
        """Pre-warm pool with minimum containers."""
        min_warm = self.config.get("pool", {}).get("min_warm", 2)
        current = len(self._get_containers({"status": "running"}))

        needed = max(0, min_warm - current)
        created = 0

        for i in range(needed):
            container_id = self._create_sandbox(f"warm-{i}")
            if container_id:
                created += 1
                print(f"Created warm sandbox: {container_id}")

        print(f"Pool warmed: {created} new sandboxes (total running: {current + created})")
        return created

    def cleanup(self) -> int:
        """Cleanup idle and stopped sandboxes."""
        containers = self._get_containers()
        cleaned = 0

        # Get assigned containers
        assigned_ids = set()
        sandbox_dir = RUNTIME_DIR / "sandboxes"
        if sandbox_dir.exists():
            for f in sandbox_dir.glob("*.json"):
                try:
                    with open(f) as fp:
                        data = json.load(fp)
                        if data.get("status") == "active":
                            assigned_ids.add(data.get("container_id"))
                except:
                    pass

        # Remove stopped containers
        for c in containers:
            cid = c.get("ID", "")[:12]
            if c.get("State") != "running" and cid not in assigned_ids:
                self._run_docker("rm", "-f", cid)
                cleaned += 1
                print(f"Removed stopped sandbox: {cid}")

        print(f"Cleanup complete: {cleaned} sandboxes removed")
        return cleaned

    def _create_sandbox(self, name: str) -> Optional[str]:
        """Create a new sandbox container."""
        image = self.config.get("sandbox", {}).get("image", "axiom-agent-sandbox:latest")

        result = self._run_docker(
            "run", "-d",
            "--name", f"atlas-sandbox-{name}-{int(time.time())}",
            "--label", SANDBOX_LABEL,
            "--label", f"atlas.agent={name}",
            "-v", f"{AXIOM_ROOT}:/workspace",
            "--memory", "1g",
            "--cpus", "1.0",
            "--network", "forge_default",
            image
        )

        if result.returncode == 0:
            container_id = result.stdout.strip()[:12]
            return container_id
        else:
            print(f"Failed to create sandbox: {result.stderr}")
            return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    pool = SandboxPool()
    command = sys.argv[1]

    if command == "status":
        status = pool.status()
        print(json.dumps(status, indent=2))

    elif command == "acquire":
        if len(sys.argv) < 3:
            print("Usage: pool-manager.py acquire <agent-name>")
            sys.exit(1)
        result = pool.acquire(sys.argv[2])
        sys.exit(0 if result else 1)

    elif command == "release":
        if len(sys.argv) < 3:
            print("Usage: pool-manager.py release <agent-name>")
            sys.exit(1)
        result = pool.release(sys.argv[2])
        sys.exit(0 if result else 1)

    elif command == "exec":
        if len(sys.argv) < 4:
            print("Usage: pool-manager.py exec <agent-name> <command...>")
            sys.exit(1)
        exit_code = pool.exec_command(sys.argv[2], sys.argv[3:])
        sys.exit(exit_code)

    elif command == "warm":
        pool.warm()

    elif command == "cleanup":
        pool.cleanup()

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
