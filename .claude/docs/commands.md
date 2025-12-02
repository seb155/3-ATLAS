# Development Commands

## Backend (SYNAPSE - `apps/synapse/backend/`)

```bash
# Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database
alembic upgrade head
alembic revision --autogenerate -m "description"

# Tests
pytest                              # All tests
pytest -k "test_name"               # Single test
pytest tests/test_rules.py          # Single file
pytest --cov=app                    # With coverage
pytest --cov=app --cov-report=html  # HTML report

# Linting
ruff check . --fix
```

## Frontend (SYNAPSE - `apps/synapse/frontend/`)

```bash
npm run dev           # Dev server (port 4000)
npm run build         # Production build
npm run test          # Run tests
npm run test:watch    # Watch mode
npm run test:coverage # Coverage report
npm run lint:fix      # Fix linting
npm run type-check    # TypeScript check
```

## Docker

```bash
docker logs synapse-backend -f --tail 100
docker restart synapse-backend
docker exec -it forge-postgres psql -U postgres -d synapse
```

## Demo Data

When database is empty:
```bash
cd apps/synapse/backend
python -m app.scripts.seed_demo
```

Creates:
- Admin: `admin@aurumax.com` / `admin123!`
- 2 Clients, 2 Projects, 5 Rules, 12 Assets
- WBS Packages: PKG-IN-001, PKG-EL-001

## Architecture (SYNAPSE Backend)

```
app/
├── main.py              # FastAPI app
├── api/endpoints/       # Route handlers
├── services/            # Business logic
│   ├── rule_engine.py
│   ├── cable_sizing.py
│   ├── ingestion_service.py
│   └── validation_service.py
├── models/              # SQLAlchemy ORM
├── schemas/             # Pydantic schemas
├── core/
│   ├── database.py
│   ├── config.py
│   ├── auth.py
│   └── exceptions.py
└── scripts/             # Seed data
```

## Key API Endpoints

- `/api/v1/auth/*` - Authentication (JWT)
- `/api/v1/projects/*` - Project management
- `/api/v1/assets/*` - Asset CRUD
- `/api/v1/rules/*` - Rule definitions
- `/api/v1/ingest/*` - CSV/Excel import
