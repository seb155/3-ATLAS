# Environment Variables Standards

Standards et templates réutilisables pour la gestion des variables d'environnement dans AXIOM.

**Pour:** Agents AI Claude
**Usage:** Référence rapide lors de création de nouveaux services

---

## Template Standard .env.template

### Backend Python (FastAPI/Django)

```env
# {{APP_NAME}} Backend Environment Configuration
# This file is a template - DO NOT edit directly
# Run: .\generate-env.ps1 to create .env with correct values
#
# Auto-replaced placeholders:
# - {{DATABASE_HOST}} -> forge-postgres (Docker) or localhost (Local)
# - {{DATABASE_PORT}} -> 5432 (Docker) or 5433 (Local)
# - {{REDIS_HOST}} -> forge-redis (Docker) or localhost (Local)
# - {{REDIS_PORT}} -> 6379 (both)
# - {{ENV_MODE}} -> docker or local

# ============================================================================
# Database Configuration
# ============================================================================

DATABASE_URL=postgresql://postgres:postgres@{{DATABASE_HOST}}:{{DATABASE_PORT}}/{{DB_NAME}}

# ============================================================================
# Cache Configuration
# ============================================================================

# Redis database number (0=SYNAPSE, 1=NEXUS, 2=CORTEX, 3=PRISM, etc.)
REDIS_URL=redis://{{REDIS_HOST}}:{{REDIS_PORT}}/{{REDIS_DB}}

# ============================================================================
# Application Settings
# ============================================================================

ENVIRONMENT={{ENV_MODE}}
DEBUG=true
LOG_LEVEL=INFO
APP_NAME={{APP_NAME}}

# ============================================================================
# Security
# ============================================================================

# MANUAL: Change this in production!
SECRET_KEY={{SECRET_KEY}}

# CORS origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:5173,https://{{APP_NAME}}.axoiq.com

# ============================================================================
# Observability (Optional)
# ============================================================================

# Loki logging
LOKI_URL=http://{{LOKI_HOST}}:{{LOKI_PORT}}

# ============================================================================
# External Services (Optional)
# ============================================================================

# Add application-specific external services here
# Example:
# STRIPE_API_KEY={{STRIPE_API_KEY}}  # MANUAL
# SENDGRID_API_KEY={{SENDGRID_API_KEY}}  # MANUAL
```

### Frontend (React/Vue/Next.js)

```env
# {{APP_NAME}} Frontend Environment
# Run: .\generate-env.ps1 to create .env

# API URL (browser-accessible)
# Production: Use Traefik domain
# Development: Use localhost
VITE_API_URL=http://localhost:8001
# VITE_API_URL=https://api-{{APP_NAME}}.axoiq.com

# Environment
VITE_ENVIRONMENT={{ENV_MODE}}
```

---

## Variables Standard par Catégorie

### Database

```env
# PostgreSQL (preferred)
DATABASE_URL=postgresql://postgres:postgres@{{DATABASE_HOST}}:{{DATABASE_PORT}}/{{DB_NAME}}

# Alternative format (components)
DB_HOST={{DATABASE_HOST}}
DB_PORT={{DATABASE_PORT}}
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME={{DB_NAME}}

# For multi-tenant: Auth database
AUTH_DATABASE_URL=postgresql://postgres:postgres@{{DATABASE_HOST}}:{{DATABASE_PORT}}/postgres
```

### Cache

```env
# Redis
REDIS_URL=redis://{{REDIS_HOST}}:{{REDIS_PORT}}

# With database number (0-15)
REDIS_URL=redis://{{REDIS_HOST}}:{{REDIS_PORT}}/{{REDIS_DB}}

# With key prefix
REDIS_URL=redis://{{REDIS_HOST}}:{{REDIS_PORT}}
REDIS_KEY_PREFIX={{APP_NAME}}:
```

### Observability

```env
# Loki (logging)
LOKI_URL=http://{{LOKI_HOST}}:{{LOKI_PORT}}

# MeiliSearch (search)
MEILISEARCH_URL=http://{{MEILISEARCH_HOST}}:{{MEILISEARCH_PORT}}
MEILISEARCH_API_KEY=masterKey
```

### Security

```env
# JWT
SECRET_KEY={{SECRET_KEY}}          # MANUAL
JWT_SECRET={{JWT_SECRET}}          # MANUAL (can be same as SECRET_KEY)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# CORS (backend)
ALLOWED_ORIGINS=http://localhost:5173,https://{{APP_NAME}}.axoiq.com
```

### AI Services (CORTEX-specific)

```env
# AI Provider Keys
ANTHROPIC_API_KEY={{ANTHROPIC_API_KEY}}  # MANUAL
OPENAI_API_KEY={{OPENAI_API_KEY}}        # MANUAL
GEMINI_API_KEY={{GEMINI_API_KEY}}        # MANUAL

# AI Infrastructure (Docker DNS)
LITELLM_URL=http://litellm:4000
OLLAMA_URL=http://ollama:11434
CHROMADB_URL=http://chromadb:8000
```

---

## Allocation Redis Database

**Convention:** Each AXIOM app uses a different Redis database number.

| App | Redis DB | URL |
|-----|----------|-----|
| SYNAPSE | 0 | `redis://forge-redis:6379/0` |
| NEXUS | 1 | `redis://forge-redis:6379/1` |
| CORTEX | 2 | `redis://forge-redis:6379/2` |
| PRISM | 3 | `redis://forge-redis:6379/3` |
| ATLAS | 4 | `redis://forge-redis:6379/4` |

---

## Script generate-env.ps1

**Location source:** `D:\Projects\AXIOM\scripts\generate-env-template.ps1`

**Usage pour nouvel app:**
```powershell
# Copier le script template
Copy-Item D:\Projects\AXIOM\scripts\generate-env-template.ps1 .\generate-env.ps1

# Tester
.\generate-env.ps1
```

**Le script détecte automatiquement:**
- Docker environment (forge-network exists)
- Local environment (no Docker)

**Variables remplacées:**
- `{{DATABASE_HOST}}` / `{{DATABASE_PORT}}`
- `{{REDIS_HOST}}` / `{{REDIS_PORT}}`
- `{{LOKI_HOST}}` / `{{LOKI_PORT}}`
- `{{MEILISEARCH_HOST}}` / `{{MEILISEARCH_PORT}}`
- `{{ENV_MODE}}`

---

## Fichier .env.example

**Purpose:** Documentation for developers (what each variable does)

```env
# {{APP_NAME}} Backend - Environment Variables Documentation
# Copy to .env.template and use generate-env.ps1

# ==============================================================================
# DATABASE CONFIGURATION
# ==============================================================================

# PostgreSQL connection string
# Format: postgresql://user:password@host:port/database
# Docker: Uses forge-postgres:5432
# Local: Uses localhost:5433
DATABASE_URL=postgresql://postgres:postgres@forge-postgres:5432/{{DB_NAME}}

# ==============================================================================
# CACHE CONFIGURATION
# ==============================================================================

# Redis connection
# Each app uses different database number (see docs)
# - SYNAPSE: /0
# - NEXUS: /1
# - CORTEX: /2
REDIS_URL=redis://forge-redis:6379/{{REDIS_DB}}

# ==============================================================================
# SECURITY
# ==============================================================================

# Secret key for JWT signing
# IMPORTANT: Generate secure random key for production
# Example: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=CHANGE_THIS_IN_PRODUCTION

# CORS allowed origins (comma-separated)
# Add all frontend URLs that need API access
ALLOWED_ORIGINS=http://localhost:5173,https://{{APP_NAME}}.axoiq.com

# ==============================================================================
# EXTERNAL SERVICES (if applicable)
# ==============================================================================

# Example: Email service
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER={{SMTP_USER}}
# SMTP_PASSWORD={{SMTP_PASSWORD}}

# Example: Payment service
# STRIPE_API_KEY={{STRIPE_API_KEY}}
# STRIPE_WEBHOOK_SECRET={{STRIPE_WEBHOOK_SECRET}}
```

---

## docker-compose Pattern

### Standard Backend Service

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: {{APP_NAME}}-backend
    env_file:
      - backend/.env  # Generated by generate-env.ps1
    ports:
      - "{{PORT}}:8000"
    networks:
      - forge-network
    depends_on:
      forge-postgres:
        condition: service_healthy
      forge-redis:
        condition: service_healthy

networks:
  forge-network:
    external: true
    name: forge-network
```

### Standalone Mode (Optional)

```yaml
services:
  postgres-standalone:
    image: postgres:15
    container_name: {{APP_NAME}}-postgres-standalone
    environment:
      POSTGRES_DB: {{DB_NAME}}
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "{{PORT_RANGE_START}}:5432"
    volumes:
      - postgres_standalone_data:/var/lib/postgresql/data

  backend-standalone:
    build:
      context: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres-standalone:5432/{{DB_NAME}}
      REDIS_URL: redis://redis-standalone:6379
    ports:
      - "{{PORT_RANGE_START + 100}}:8000"

volumes:
  postgres_standalone_data:
```

---

## Application Code Pattern

### Python (FastAPI with Pydantic BaseSettings)

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # Cache
    REDIS_URL: str

    # Security
    SECRET_KEY: str
    ALLOWED_ORIGINS: list[str] = []

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

### Python (Django)

```python
# settings.py
import os
from pathlib import Path

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL'),
    }
}

# Security
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

### JavaScript/TypeScript (Node.js)

```javascript
// config.ts
import dotenv from 'dotenv';
dotenv.config();

export const config = {
  database: {
    url: process.env.DATABASE_URL!,
  },
  redis: {
    url: process.env.REDIS_URL!,
  },
  app: {
    environment: process.env.ENVIRONMENT || 'development',
    debug: process.env.DEBUG === 'true',
  },
  security: {
    secretKey: process.env.SECRET_KEY!,
  },
};
```

---

## Validation

### Pre-Start Validation

```python
# Validate required environment variables
import os

REQUIRED_VARS = [
    'DATABASE_URL',
    'REDIS_URL',
    'SECRET_KEY',
]

def validate_env():
    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")

# Call on startup
validate_env()
```

---

## .gitignore Standard

```gitignore
# Environment files (never commit actual values)
.env
.env.local
.env.docker
.env.*.local
.env.backup-*

# Templates and examples (DO commit)
!.env.template
!.env.example

# Scripts (DO commit)
!generate-env.ps1
```

---

## Quick Reference: Creating New Service

1. **Copy template:**
   ```powershell
   cp AXIOM/scripts/.env.template.example app/backend/.env.template
   ```

2. **Customize placeholders:**
   ```env
   {{APP_NAME}} → myapp
   {{DB_NAME}} → myapp
   {{REDIS_DB}} → 3
   ```

3. **Copy script:**
   ```powershell
   cp AXIOM/scripts/generate-env-template.ps1 app/backend/generate-env.ps1
   ```

4. **Create .env.example** (documentation)

5. **Generate .env:**
   ```powershell
   cd app/backend
   .\generate-env.ps1
   ```

6. **Test:**
   ```powershell
   cat .env  # Verify output
   docker compose up backend  # Test service
   ```

---

## Related Documentation

- **User Docs:** `AXIOM/docs/infrastructure/environment-variables.md`
- **Rule:** `.claude/agents/rules/12-docker-networking.md`
- **Script:** `AXIOM/scripts/generate-env-template.ps1`
- **Example:** `AXIOM/scripts/.env.template.example`

---

**Last Updated:** 2025-11-29
**Version:** 1.0
