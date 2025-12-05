# Telos Integration

Based on [Telos](https://github.com/danielmiessler/Telos) by Daniel Miessler.

## What is Telos?

Telos provides "deep context about things that matter" through Telos Context Files (TCFs).

## Templates

- `corporate_telos.md` - Enterprise/team context template
- `personal_telos.md` - Individual context template
- `project_telos.md` - Project-specific context template

## Usage

1. Copy appropriate template to `contexts/`
2. Customize with your project/organization details
3. Reference in AI conversations for context

## ATLAS Integration

TCF files in `contexts/` are automatically loaded at session start to provide purpose and goal context.

See: `contexts/atlas.telos.md` for example
