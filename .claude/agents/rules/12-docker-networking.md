<!-- 🔒 PROTECTED: Infrastructure rule - DO NOT MODIFY WITHOUT OWNER VALIDATION -->

# Règle 12: Docker Networking & Environment Configuration

**Status:** OBLIGATOIRE
**Dernière mise à jour:** 2025-11-30
**Scope:** Tous les agents AI

---

## RÈGLE ABSOLUE

**TOUTES les applications AXIOM DOIVENT utiliser Docker DNS pour la communication inter-services.**

**INTERDIT:**
- ❌ Hardcoder des adresses IP (`192.168.x.x`, `172.x.x.x`)
- ❌ Utiliser `localhost` dans les fichiers de configuration Docker
- ❌ Créer des fichiers `.env` manuellement sans template

**OBLIGATOIRE:**
- ✅ Utiliser Docker DNS names (`forge-postgres`, `forge-redis`)
- ✅ Fournir `.env.template` avec placeholders `{{VAR}}`
- ✅ Fournir script `generate-env.ps1` pour auto-génération

---

## Pattern Standard: .env Management

### 1. Fichiers Requis

Pour chaque application backend:

```
app/backend/
├── .env.template      # Template avec {{PLACEHOLDERS}} (git tracked)
├── .env.example       # Documentation (git tracked)
├── generate-env.ps1   # Script auto-génération (git tracked)
└── .env               # Généré, gitignored
```

### 2. Template Pattern

**Fichier `.env.template`:**
```env
# Application Backend Environment
# Run: .\generate-env.ps1 to auto-generate .env

# Database (auto-replaced)
DATABASE_URL=postgresql://postgres:postgres@{{DATABASE_HOST}}:{{DATABASE_PORT}}/{{DB_NAME}}

# Cache (auto-replaced)
REDIS_URL=redis://{{REDIS_HOST}}:{{REDIS_PORT}}

# Environment mode (auto-replaced)
ENVIRONMENT={{ENV_MODE}}

# Manual configuration (not auto-replaced)
SECRET_KEY={{SECRET_KEY}}  # MANUAL: Change in production
API_KEY={{API_KEY}}        # MANUAL: Add your key
```

### 3. Script de Génération

**Copier depuis:** `D:\Projects\AXIOM\scripts\generate-env-template.ps1`

**Variables auto-remplacées:**

| Placeholder | Docker | Local |
|------------|--------|-------|
| `{{DATABASE_HOST}}` | `forge-postgres` | `localhost` |
| `{{DATABASE_PORT}}` | `5432` | `5433` |
| `{{REDIS_HOST}}` | `forge-redis` | `localhost` |
| `{{REDIS_PORT}}` | `6379` | `6379` |
| `{{ENV_MODE}}` | `docker` | `local` |

---

## Docker DNS Patterns

### ✅ Pattern Correct: Service-to-Service

```yaml
# docker-compose.dev.yml
services:
  backend:
    environment:
      DATABASE_URL: postgresql://postgres:postgres@forge-postgres:5432/myapp
      REDIS_URL: redis://forge-redis:6379
      CORTEX_URL: http://cortex-backend:8000  # Autre service AXIOM
    networks:
      - forge-network

networks:
  forge-network:
    external: true
```

### ❌ Anti-Pattern: Hardcoded Values

```yaml
# NE JAMAIS FAIRE ÇA
services:
  backend:
    environment:
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/myapp      # ❌
      REDIS_URL: redis://192.168.1.10:6379                                   # ❌
      CORTEX_URL: http://172.18.0.5:8000                                     # ❌
```

---

## Checklist Création Nouveau Service

Avant de créer un nouveau service/application, l'agent DOIT:

- [ ] **1. Lire url-registry.yml**
  ```
  Read: D:\Projects\AXIOM\.dev\infra\url-registry.yml
  ```

- [ ] **2. Vérifier ports disponibles** dans le range approprié
  - FORGE: 3000-3999
  - SYNAPSE: 4000-4999
  - NEXUS: 5000-5999
  - APEX: 6000-6999
  - CORTEX: 7000-7999

- [ ] **3. Créer .env.template** avec placeholders `{{VAR}}`

- [ ] **4. Copier generate-env.ps1** depuis `AXIOM/scripts/`

- [ ] **5. Créer .env.example** (documentation)

- [ ] **6. Configurer docker-compose.yml**
  ```yaml
  networks:
    - forge-network
  ```

- [ ] **7. Utiliser Docker DNS names** (jamais IPs, jamais localhost)

- [ ] **8. Tester génération:**
  ```powershell
  .\generate-env.ps1
  cat .env  # Vérifier output
  ```

---

## Communication Patterns par Type

### Backend → Database

```env
DATABASE_URL=postgresql://postgres:postgres@forge-postgres:5432/synapse
```

### Backend → Cache

```env
REDIS_URL=redis://forge-redis:6379
# Utiliser database différent par app: /0, /1, /2, etc.
```

### Backend → Autre Backend

```env
# Docker DNS name du service
CORTEX_API_URL=http://cortex-backend:8000
NEXUS_API_URL=http://nexus-backend:8000
```

### Frontend → Backend

**IMPORTANT:** Frontend s'exécute dans le navigateur!

```javascript
// Production: Via Traefik
const API_URL = "https://api.axoiq.com";

// Development local
const API_URL = "http://localhost:8001";

// ❌ NE JAMAIS UTILISER Docker DNS dans frontend
const API_URL = "http://synapse-backend:8000";  // ❌ Navigateur ne peut pas résoudre
```

---

## Validation Agent

Avant de proposer une configuration, l'agent DOIT vérifier:

### 1. Pas d'IPs Hardcodées

```bash
# Vérifier fichiers de config
grep -r "192\.168\." .
grep -r "172\.\|10\." .
grep -r "127\.0\.0\.1" .
```

### 2. Utilisation Docker DNS

```bash
# Vérifier présence de noms Docker
grep -r "forge-postgres\|forge-redis" .
```

### 3. Fichiers .env.template Présents

```bash
# Vérifier structure
ls .env.template
ls generate-env.ps1
```

---

## Erreurs Courantes à Éviter

### ❌ Erreur 1: Mélanger Docker et localhost

```env
# INCORRECT
DATABASE_URL=postgresql://...@forge-postgres:5432/synapse  # Docker
REDIS_URL=redis://localhost:6379                          # Localhost
```

**Solution:** Utiliser `{{PLACEHOLDERS}}` et `generate-env.ps1`.

### ❌ Erreur 2: Fichier .env committé

```bash
# .gitignore DOIT contenir:
.env
.env.local
.env.*.local
.env.backup-*

# Mais PAS:
!.env.template
!.env.example
```

### ❌ Erreur 3: Ports hardcodés dans code

```python
# INCORRECT
DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/synapse"

# CORRECT
DATABASE_URL = os.getenv("DATABASE_URL")
```

---

## Intégration avec Autres Règles

### Règle 10 (Traefik Routing)

- Utiliser Traefik pour accès externe (navigateur → backend)
- Utiliser Docker DNS pour accès interne (backend → backend)

### Règle 11 (URL Registry)

- Consulter registry AVANT d'allouer ports
- Variables d'environnement doivent être alignées avec registry

---

## Actions Automatiques Requises

### Lors Création Nouveau Service

```markdown
1. AskUserQuestion: Valider nom, port, domaine
2. Read: url-registry.yml
3. Create: .env.template avec placeholders
4. Copy: generate-env.ps1 depuis AXIOM/scripts/
5. Create: .env.example (documentation)
6. Update: docker-compose.yml avec forge-network
7. Test: .\generate-env.ps1
8. Update: url-registry.yml
```

### Lors Diagnostic Problème Réseau

```markdown
1. Read: .env file
2. Check: Présence IPs hardcodées
3. Check: forge-network dans docker-compose
4. Check: Services FORGE running (docker ps)
5. Suggest: Régénérer .env si incorrect
```

---

## Documentation Référence

### Pour Utilisateurs

- `AXIOM/docs/infrastructure/docker-networking.md` - Guide complet
- `AXIOM/docs/infrastructure/environment-variables.md` - .env management

### Pour Agents

- Cette règle (12-docker-networking.md) - Patterns obligatoires
- `Règle 10` - Traefik routing
- `Règle 11` - URL registry

### Templates

- `AXIOM/scripts/generate-env-template.ps1` - Script réutilisable
- `AXIOM/scripts/.env.template.example` - Pattern exemple

---

## Exemples Complets

### Exemple 1: Nouveau Backend

```env
# .env.template
DATABASE_URL=postgresql://postgres:postgres@{{DATABASE_HOST}}:{{DATABASE_PORT}}/newapp
REDIS_URL=redis://{{REDIS_HOST}}:{{REDIS_PORT}}/3
ENVIRONMENT={{ENV_MODE}}
SECRET_KEY={{SECRET_KEY}}
```

```powershell
# generate-env.ps1 (copier depuis AXIOM/scripts/)
```

```yaml
# docker-compose.dev.yml
services:
  backend:
    env_file: .env
    networks:
      - forge-network
networks:
  forge-network:
    external: true
```

### Exemple 2: Service Externe (Standalone)

Si déploiement indépendant requis (comme NEXUS standalone):

```yaml
# docker-compose.yml (standalone)
services:
  postgres-standalone:
    image: postgres:15
    container_name: newapp-postgres-standalone
    ports:
      - "6500:5432"  # Port dans range APEX (6000-6999)

  backend-standalone:
    environment:
      DATABASE_URL: postgresql://...@postgres-standalone:5432/newapp
    ports:
      - "6000:8000"
```

**Important:** Documenter les deux modes (FORGE vs standalone) dans README.

---

## Support

**Questions sur cette règle:**
- Consulter docs/infrastructure/docker-networking.md
- Invoquer DevOps Manager agent

**Mise à jour de la règle:**
- Proposer changements via GENESIS agent
- Valider avec utilisateur avant modification

---

**RAPPEL:**

```
AVANT toute création de service:
→ Read: url-registry.yml
→ Create: .env.template avec {{PLACEHOLDERS}}
→ Copy: generate-env.ps1
→ Use: Docker DNS names (JAMAIS IPs)
```

**Pas d'exception à ces règles.**
