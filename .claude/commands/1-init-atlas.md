# /1-init-atlas

Initialize ATLAS layering structure in a project.

## Usage

```
/1-init-atlas              # Auto-detect project type
/1-init-atlas standalone   # Force standalone type
/1-init-atlas child        # Force child type (in monorepo)
/1-init-atlas parent       # Force parent type (monorepo root)
```

## What This Command Does

1. **Detect project type** (if not specified):
   - Check for parent `.atlas/` → child
   - Check for `apps/` or multiple sub-projects → parent
   - Otherwise → standalone

2. **Create .atlas/ structure**:
   ```
   .atlas/
   ├── atlas.config.json     # From template
   ├── agents/               # Project-specific agents
   ├── overrides/            # Override framework components
   ├── commands/             # Project-specific commands
   ├── skills/               # Project-specific skills
   └── runtime/
       ├── sessions/         # Session tracking
       └── checkpoints/      # Manual checkpoints
   ```

3. **Generate atlas.config.json** with:
   - Project ID from directory name
   - Detected or specified type
   - Framework path

4. **Create .gitignore** for runtime data

## Execution Steps

### Step 1: Detect/Confirm Type
```bash
# Check for parent
if [ -f "../.atlas/atlas.config.json" ]; then
  TYPE="child"
elif [ -d "apps" ] || [ $(find . -maxdepth 2 -name ".dev" -type d | wc -l) -gt 1 ]; then
  TYPE="parent"
else
  TYPE="standalone"
fi
```

### Step 2: Create Structure
```bash
mkdir -p .atlas/{agents,overrides,commands,skills}
mkdir -p .atlas/runtime/{sessions,checkpoints}
```

### Step 3: Generate Config
Copy appropriate template from `.claude/templates/atlas/config-{type}.json`
and replace placeholders:
- `{{PROJECT_ID}}` → directory name (lowercase, no spaces)
- `{{PROJECT_NAME}}` → directory name (human readable)
- `{{PARENT_PATH}}` → relative path to parent (for child type)

### Step 4: Create .gitignore
```
# .atlas/.gitignore
runtime/sessions/*
runtime/checkpoints/*
!runtime/sessions/.gitkeep
!runtime/checkpoints/.gitkeep
```

### Step 5: Create .gitkeep files
```bash
touch .atlas/runtime/sessions/.gitkeep
touch .atlas/runtime/checkpoints/.gitkeep
```

## Output

After successful initialization:
```
✓ Created .atlas/ structure
✓ Generated atlas.config.json (type: {type})
✓ Project ready for ATLAS layering

Next steps:
- Add project-specific agents to .atlas/agents/
- Override framework components in .atlas/overrides/
- Add project commands to .atlas/commands/
```

## Notes

- Does NOT affect existing .dev/ structure
- Does NOT modify .claude symlink
- Safe to run multiple times (won't overwrite existing config)
