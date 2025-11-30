# Environment Variables Management

Comprehensive guide for managing environment variables across AXIOM applications using the `.env.template` pattern and auto-generation scripts.

---

## Overview

AXIOM uses a **template-based system** for environment configuration:
1. `.env.template` - Template with placeholders (committed to git)
2. `generate-env.ps1` - PowerShell script that auto-generates `.env` (committed to git)
3. `.env` - Generated file with actual values (gitignored)

**Benefits:**
- ✅ Auto-detects Docker vs local environment
- ✅ No hardcoded IPs or hostnames
- ✅ Consistent across all applications
- ✅ Developers don't need to manually edit `.env`

---

## Quick Start

### For Developers

```powershell
# Navigate to backend directory
cd D:\Projects\AXIOM\apps\synapse\backend

# Generate .env from template (auto-detects environment)
.\generate-env.ps1

# Output:
# 🐳 Detected Docker environment
# ✓ Successfully generated .env
#   Mode: docker
#   Database: forge-postgres:5432
```

That's it! The script automatically:
- Detects if you're in Docker or local mode
- Replaces all `{{PLACEHOLDERS}}` with correct values
- Creates `.env` with appropriate configuration

---

## How It Works

### Environment Detection

The `generate-env.ps1` script detects your environment using these checks (in order):

1. **Check for `/.dockerenv` file** (standard Docker marker)
2. **Check `DOCKER_CONTAINER` environment variable**
3. **Check if `forge-network` exists** (`docker network ls`)

If ANY check is true → **Docker mode**
If ALL checks are false → **Local mode**

### Variable Replacement

The script replaces these placeholders automatically:

| Placeholder | Docker Value | Local Value |
|------------|--------------|-------------|
| `{{DATABASE_HOST}}` | `forge-postgres` | `localhost` |
| `{{DATABASE_PORT}}` | `5432` | `5433` |
| `{{REDIS_HOST}}` | `forge-redis` | `localhost` |
| `{{REDIS_PORT}}` | `6379` | `6379` |
| `{{LOKI_HOST}}` | `forge-loki` | `localhost` |
| `{{LOKI_PORT}}` | `3100` | `3100` |
| `{{MEILISEARCH_HOST}}` | `forge-meilisearch` | `localhost` |
| `{{MEILISEARCH_PORT}}` | `7700` | `7700` |
| `{{ENV_MODE}}` | `docker` | `local` |

---

## File Structure

### Standard Application Structure

```
app/
├── backend/
│   ├── .env.template      # Template with {{PLACEHOLDERS}} (git tracked)
│   ├── .env.example       # Documentation of all variables (git tracked)
│   ├── generate-env.ps1   # Auto-generation script (git tracked)
│   ├── .env               # Generated file (gitignored)
│   ├── .env.backup-*      # Auto-backups (gitignored)
│   └── app/
│       └── core/
│           └── config.py  # Reads .env file
```

### Template File (.env.template)

Example for SYNAPSE:

```env
# SYNAPSE Backend Environment Configuration
# This file is a template - DO NOT edit directly
# Run: .\generate-env.ps1 to create .env with correct values

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@{{DATABASE_HOST}}:{{DATABASE_PORT}}/synapse

# Cache
REDIS_URL=redis://{{REDIS_HOST}}:{{REDIS_PORT}}

# Environment
ENVIRONMENT={{ENV_MODE}}

# Security (MANUAL: Change in production!)
SECRET_KEY=CHANGE_THIS_IN_PRODUCTION_SECRET_KEY
```

### Example File (.env.example)

Documents all available variables:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@forge-postgres:5432/synapse

# Cache
REDIS_URL=redis://forge-redis:6379

# Security
SECRET_KEY=your-secret-key-here

# CORS (comma-separated origins)
ALLOWED_ORIGINS=http://localhost:4000,https://synapse.axoiq.com
```

---

## Usage Guide

### Initial Setup (First Time)

1. **Clone repository:**
   ```powershell
   git clone <repo-url>
   cd AXIOM/apps/synapse/backend
   ```

2. **Generate .env:**
   ```powershell
   .\generate-env.ps1
   ```

3. **Review generated file:**
   ```powershell
   cat .env
   ```

4. **Edit manual placeholders** (if any):
   ```powershell
   notepad .env
   # Replace things like {{SECRET_KEY}}, {{API_KEY}}, etc.
   ```

### Regenerating .env

If you switch environments or need to regenerate:

```powershell
# With prompt (asks to overwrite)
.\generate-env.ps1

# Force overwrite (no prompt)
.\generate-env.ps1 -Force
```

**Safety:** The script automatically backs up your existing `.env` with a timestamp:
```
.env.backup-20251129-153045
```

### Switching Environments

**From Local to Docker:**
```powershell
# Start FORGE infrastructure
cd D:\Projects\AXIOM\forge
docker compose up -d

# Regenerate .env (will auto-detect Docker)
cd D:\Projects\AXIOM\apps\synapse\backend
.\generate-env.ps1 -Force
```

**From Docker to Local:**
```powershell
# Stop Docker containers
docker compose down

# Regenerate .env (will auto-detect Local)
.\generate-env.ps1 -Force
```

---

## Variable Categories

### Auto-Replaced Variables

These are automatically set by `generate-env.ps1`:

```env
DATABASE_URL=postgresql://postgres:postgres@{{DATABASE_HOST}}:{{DATABASE_PORT}}/synapse
REDIS_URL=redis://{{REDIS_HOST}}:{{REDIS_PORT}}
ENVIRONMENT={{ENV_MODE}}
```

### Manual Variables

These require manual configuration (not auto-replaced):

```env
# API Keys
ANTHROPIC_API_KEY=sk-ant-xxx          # MANUAL: Add your key
OPENAI_API_KEY=sk-xxx                 # MANUAL: Add your key

# Security
SECRET_KEY={{SECRET_KEY}}             # MANUAL: Generate secure key

# External Services
TRILIUM_ETAPI_TOKEN=xxx               # MANUAL: Add token
```

### Environment-Specific Overrides

Some variables change based on environment but aren't auto-replaced:

```env
# CORS origins (different for Docker vs Local)
# Docker mode: Use domain names
ALLOWED_ORIGINS=http://synapse-frontend:4000,https://synapse.axoiq.com

# Local mode: Use localhost
ALLOWED_ORIGINS=http://localhost:4000,http://localhost:5173
```

**Tip:** Use conditional logic in application code or create separate templates.

---

## Best Practices

### DO:

✅ **Use `.env.template` for all configurations**
```env
DATABASE_URL=postgresql://postgres:postgres@{{DATABASE_HOST}}:{{DATABASE_PORT}}/myapp
```

✅ **Commit `.env.template` and `generate-env.ps1` to git**
```gitignore
# .gitignore
.env
.env.backup-*
```

✅ **Document all variables in `.env.example`**
```env
# .env.example - Full documentation
DATABASE_URL=postgresql://...  # PostgreSQL connection string
REDIS_URL=redis://...          # Redis cache connection
```

✅ **Run `generate-env.ps1` when environment changes**
```powershell
.\generate-env.ps1 -Force
```

### DON'T:

❌ **Don't hardcode values in application code**
```python
# BAD
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/synapse"

# GOOD
DATABASE_URL = os.getenv("DATABASE_URL")
```

❌ **Don't commit `.env` to git**
```gitignore
# Always in .gitignore
.env
.env.local
.env.backup-*
```

❌ **Don't mix Docker and localhost in same `.env`**
```env
# BAD - Inconsistent
DATABASE_URL=postgresql://...@forge-postgres:5432/synapse  # Docker DNS
REDIS_URL=redis://localhost:6379                          # Localhost
```

---

## Application-Specific Guides

### SYNAPSE Backend

**Location:** `D:\Projects\AXIOM\apps\synapse\backend`

**Variables:**
```env
DATABASE_URL=postgresql://postgres:postgres@{{DATABASE_HOST}}:{{DATABASE_PORT}}/synapse
REDIS_URL=redis://{{REDIS_HOST}}:{{REDIS_PORT}}
SECRET_KEY=CHANGE_THIS_IN_PRODUCTION_SECRET_KEY
ALLOWED_ORIGINS=http://localhost:4000,http://localhost:5173
```

**Generate:**
```powershell
cd D:\Projects\AXIOM\apps\synapse\backend
.\generate-env.ps1
```

### NEXUS Backend

**Location:** `D:\Projects\AXIOM\apps\nexus\backend`

**Variables:**
```env
DATABASE_URL=postgresql://postgres:postgres@{{DATABASE_HOST}}:{{DATABASE_PORT}}/nexus
AUTH_DATABASE_URL=postgresql://postgres:postgres@{{DATABASE_HOST}}:{{DATABASE_PORT}}/postgres
REDIS_URL=redis://{{REDIS_HOST}}:{{REDIS_PORT}}
REDIS_KEY_PREFIX=nexus:
TRILIUM_ETAPI_URL=https://notes.s-gagnon.com      # MANUAL
TRILIUM_ETAPI_TOKEN=xxx                            # MANUAL
```

**Generate:**
```powershell
cd D:\Projects\AXIOM\apps\nexus\backend
.\generate-env.ps1
```

### CORTEX Backend

**Location:** `D:\Projects\AXIOM\apps\cortex`

**Variables:**
```env
DATABASE_URL=postgresql://postgres:postgres@{{DATABASE_HOST}}:{{DATABASE_PORT}}/cortex
REDIS_URL=redis://{{REDIS_HOST}}:{{REDIS_PORT}}/2
ANTHROPIC_API_KEY=sk-ant-xxx                       # MANUAL
LITELLM_URL=http://litellm:4000
OLLAMA_URL=http://ollama:11434
```

**Generate:**
```powershell
cd D:\Projects\AXIOM\apps\cortex
.\generate-env.ps1
```

---

## Troubleshooting

### Error: "Template file not found"

**Cause:** No `.env.template` in directory

**Solution:**
```powershell
# Copy from example
cp .env.example .env.template

# Or create from scratch using pattern
```

### Error: "Unresolved placeholders: {{SECRET_KEY}}"

**Cause:** Manual placeholders not replaced

**Solution:**
```powershell
# Edit .env and replace manual placeholders
notepad .env

# Replace {{SECRET_KEY}} with actual value
```

### Wrong Environment Detected

**Problem:** Script detects Docker but you're local (or vice versa)

**Debug:**
```powershell
# Check if forge-network exists
docker network ls | findstr forge

# Check Docker environment
docker ps
```

**Solution:**
```powershell
# Stop Docker if needed
docker compose down

# Force regeneration
.\generate-env.ps1 -Force
```

### Variables Not Loading in Application

**Possible causes:**
1. `.env` file not in correct location
2. Application not reading `.env` file
3. Variable name mismatch

**Solution:**
```powershell
# Verify .env exists
ls .env

# Check file contents
cat .env

# Verify application config
# Python: load_dotenv() or pydantic BaseSettings
# Node: require('dotenv').config()
```

---

## Advanced Usage

### Custom Templates

Create environment-specific templates:

```powershell
# Production template
.env.template.prod

# Staging template
.env.template.staging

# Use specific template
.\generate-env.ps1 -Template .env.template.prod
```

### Multiple Environments

Use different `.env` files:

```env
# .env.docker (for Docker mode)
DATABASE_URL=postgresql://...@forge-postgres:5432/synapse

# .env.local (for local mode)
DATABASE_URL=postgresql://...@localhost:5433/synapse
```

```powershell
# Switch between them
copy .env.docker .env
# or
copy .env.local .env
```

### Validation

Validate `.env` file before starting application:

```powershell
# Check for required variables
$env = Get-Content .env | ConvertFrom-StringData
if (-not $env.DATABASE_URL) {
    Write-Error "DATABASE_URL not set"
}
```

---

## Security Considerations

### Secrets Management

**Development:**
```env
# OK for local development
SECRET_KEY=dev-secret-key-not-for-production
API_KEY=test-api-key
```

**Production:**
```env
# Use strong, randomly generated secrets
SECRET_KEY=$(openssl rand -hex 32)
API_KEY=<from secure vault>
```

**Best Practice:**
- Never commit secrets to git
- Use secret management tools (HashiCorp Vault, AWS Secrets Manager, etc.)
- Rotate secrets regularly
- Use different secrets per environment

### .gitignore Configuration

```gitignore
# Environment files (never commit)
.env
.env.local
.env.docker
.env.*.local
.env.backup-*

# Templates and examples (DO commit)
!.env.template
!.env.example
```

---

## Related Documentation

- [Docker Networking Guide](docker-networking.md)
- [Infrastructure Overview](README.md)
- [URL Registry](../../.dev/infra/url-registry.yml)
- [Generate-Env Script](../../scripts/generate-env-template.ps1)

---

**Last Updated:** 2025-11-29
**Version:** 1.0
