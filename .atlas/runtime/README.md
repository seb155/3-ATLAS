# ATLAS 2.0 - Runtime Directory

This directory contains runtime state for inter-agent communication.

## Structure

```
.atlas/runtime/
├── README.md           # This file
├── status.json         # Global orchestration status
├── tasks/              # Pending and active tasks
│   └── task-{id}.json
├── results/            # Completed task results
│   └── task-{id}-result.json
└── agents/             # Agent status tracking
    └── {agent-name}.json
```

## Usage

### For ATLAS Orchestrator

```python
# Check global status
with open('.atlas/runtime/status.json') as f:
    status = json.load(f)

# Create task for agent
task = {
    "id": "task-001",
    "agent": "backend-builder",
    "action": "create_endpoint",
    "input": {...},
    "status": "pending"
}
with open(f'.atlas/runtime/tasks/task-001.json', 'w') as f:
    json.dump(task, f)
```

### For Agents

```python
# Read assigned task
with open('.atlas/runtime/tasks/task-001.json') as f:
    task = json.load(f)

# Write result when done
result = {
    "task_id": "task-001",
    "status": "success",
    "output": {...}
}
with open('.atlas/runtime/results/task-001-result.json', 'w') as f:
    json.dump(result, f)
```

## Cleanup

Runtime files are temporary and can be cleaned:

```bash
# Clean all runtime state
rm -rf .atlas/runtime/tasks/*
rm -rf .atlas/runtime/results/*
rm -rf .atlas/runtime/agents/*

# Reset status
echo '{"status": "idle", "agents": {}}' > .atlas/runtime/status.json
```

## See Also

- Task schema: `schemas/task.schema.json`
- Result schema: `schemas/result.schema.json`
- Agent status schema: `schemas/agent-status.schema.json`
