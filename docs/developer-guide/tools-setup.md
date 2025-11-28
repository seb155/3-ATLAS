# Development Tools Setup

Free and open-source tools for SYNAPSE development.

---

## Core (Already in SYNAPSE)

### Alembic (Migrations)
```bash
pip install alembic
```
- **License:** BSD (100% Free)
- **Function:** Versioned schema migrations
- **Docs:** https://alembic.sqlalchemy.org

### SQLAlchemy (ORM)
```bash
pip install sqlalchemy
```
- **License:** MIT (100% Free)
- **Function:** Python ORM
- **Repo:** https://github.com/sqlalchemy/sqlalchemy

---

## Database GUI Tools

### Prisma Studio (Recommended)
```bash
npm install -g prisma
prisma studio
```
- **License:** Free
- **Function:** Visual GUI for data exploration
- **Features:** Inline editing, visualized relations
- **URL:** http://localhost:5555

### DBeaver
```bash
# Download: https://dbeaver.io/download/
```
- **License:** Apache 2.0 (Free)
- **Function:** Full-featured graphical DB client
- **Features:** ER diagrams, schema compare, SQL editor

### pgAdmin 4
```bash
docker run -p 5050:80 \
  -e 'PGADMIN_DEFAULT_EMAIL=admin@admin.com' \
  -e 'PGADMIN_DEFAULT_PASSWORD=admin' \
  dpage/pgadmin4
```
- **License:** PostgreSQL (Free)
- **Function:** Complete PostgreSQL GUI

### TablePlus (Community)
- **License:** Free (Community: 2 tabs, 2 connections)
- **Download:** https://tableplus.com/

---

## Cloud Services (Free Tier)

### PostgreSQL Hosting

| Provider | Free Tier | URL |
|----------|-----------|-----|
| **Neon.tech** | 3 GB storage, 1 project | https://neon.tech |
| **Supabase** | 500 MB DB, 1 GB storage | https://supabase.com |
| **Railway** | $5 credit/month | https://railway.app |

### Schema Documentation

**dbdocs.io**
```bash
npm install -g dbdocs
dbdocs build docs/schema.dbml
```
- Free for public projects
- URL: https://dbdocs.io

**dbdiagram.io**
- Free: 10 diagrams
- URL: https://dbdiagram.io

---

## Code Quality & Validation

### SQLFluff (SQL Linter)
```bash
pip install sqlfluff
sqlfluff lint backend/alembic/versions/*.sql
sqlfluff fix backend/alembic/versions/*.sql
```
- **License:** MIT (Free)
- **Function:** Lint + format SQL

### Pre-commit (Git Hooks)
```bash
pip install pre-commit
pre-commit install
```
- **License:** MIT (Free)
- **Function:** Automatic validation before commit

**Config example** (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: https://github.com/sqlfluff/sqlfluff
    rev: 2.3.0
    hooks:
      - id: sqlfluff-lint
        args: [--dialect, postgres]
```

---

## Schema Visualization

### ERAlchemy (ER Diagrams)
```bash
pip install eralchemy2
eralchemy2 -i 'postgresql://user:pass@localhost/synapse' -o docs/schema.png
```
- **License:** Apache 2.0 (Free)
- **Output:** PNG, PDF, DOT

### SchemaCrawler
```bash
docker run -v "$PWD:/output" \
  schemacrawler/schemacrawler \
  /opt/schemacrawler/bin/schemacrawler.sh \
  --server=postgresql \
  --host=db \
  --database=synapse \
  --info-level=maximum \
  --command=schema \
  --output-format=png \
  --output-file=/output/schema.png
```
- **License:** EPL/GPL (Free)

---

## Testing & Data Generation

### pytest
```bash
pip install pytest pytest-postgresql
```
- **License:** MIT (Free)
- **Function:** Automated testing

### Faker (Test Data)
```bash
pip install faker
```
- **License:** MIT (Free)
- **Function:** Generate realistic test data

```python
from faker import Faker
fake = Faker()

# Generate test assets
for _ in range(100):
    asset = Asset(
        tag=fake.bothify('???-####'),
        type=fake.random_element(['PUMP', 'MOTOR', 'VALVE'])
    )
```

---

## Documentation Tools

### MkDocs + Material
```bash
pip install mkdocs mkdocs-material
mkdocs new docs
mkdocs serve
```
- **License:** MIT (Free)
- **Demo:** https://squidfunk.github.io/mkdocs-material/

### Sphinx + autodoc
```bash
pip install sphinx sphinx-autodoc-typehints
sphinx-quickstart docs
```
- **License:** BSD (Free)
- **Function:** Auto-documentation from code

---

## Debugging & Analysis

### pg_stat_statements (Query Analysis)
```sql
-- Enable in PostgreSQL
CREATE EXTENSION pg_stat_statements;
SELECT query, calls, total_time FROM pg_stat_statements;
```
- Built-in PostgreSQL extension

### FastAPI Debug Toolbar
```bash
pip install fastapi-debug-toolbar
```
- **License:** BSD (Free)

---

## Recommended Dev Setup

### requirements-dev.txt
```txt
# Core
sqlalchemy>=2.0.0
alembic>=1.12.0

# Validation
sqlfluff>=2.3.0
pre-commit>=3.0.0

# Visualization
eralchemy2>=1.3.0

# Testing
pytest>=7.4.0
pytest-postgresql>=5.0.0
faker>=20.0.0

# Documentation
mkdocs>=1.5.0
mkdocs-material>=9.0.0

# Utils
sqlalchemy-utils>=0.41.0
```

### Quick Start
```bash
# 1. Install tools
pip install -r requirements-dev.txt

# 2. Setup pre-commit
pre-commit install

# 3. Validate schema
python -m app.scripts.validate_schema

# 4. Generate diagram
python -m app.scripts.generate_er_diagram

# 5. Build docs
cd docs && mkdocs serve
```

---

## Cost Summary

**$0 / GRATUIT** - All tools listed are:
- Open source or free tier
- Production-ready
- Actively maintained
