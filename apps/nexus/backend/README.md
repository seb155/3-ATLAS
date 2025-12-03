# Nexus Backend API

FastAPI backend for Nexus Knowledge Graph Portal - Phase 2

## Quick Start

### 1. Start Docker Services

```bash
# From project root
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 2. Setup Python Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Edit .env and paste the generated key into SECRET_KEY
```

### 4. Initialize Database

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Edit alembic/env.py:
# - Import: from app.database import Base
# - Import: from app.models import user, note
# - Set: target_metadata = Base.metadata

# Create initial migration
alembic revision --autogenerate -m "Initial schema: users and notes"

# Run migrations
alembic upgrade head

# Verify tables created
docker exec nexus-postgres psql -U nexus -d nexus_dev -c "\dt"
```

### 5. Start Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

### Authentication

- **POST** `/api/v1/auth/register` - Register new user
- **POST** `/api/v1/auth/login` - Login (returns JWT token)
- **GET** `/api/v1/auth/me` - Get current user info (protected)

### Notes

- **POST** `/api/v1/notes` - Create note (protected)
- **GET** `/api/v1/notes` - Get all user's notes (protected)
- **GET** `/api/v1/notes/{id}` - Get single note (protected)
- **PUT** `/api/v1/notes/{id}` - Update note (protected)
- **DELETE** `/api/v1/notes/{id}` - Delete note (protected)

## Testing

### Manual Testing (FastAPI Docs)

1. Open http://localhost:8000/docs
2. Register a user: POST `/api/v1/auth/register`
3. Login: POST `/api/v1/auth/login` (copy access_token)
4. Click "Authorize" button, paste token
5. Test protected endpoints

### Automated Tests

```bash
pytest tests/ -v
```

## Project Structure

```
backend/
├── app/
│   ├── models/          # SQLAlchemy models
│   │   ├── user.py
│   │   └── note.py
│   ├── schemas/         # Pydantic schemas
│   │   ├── user.py
│   │   └── note.py
│   ├── routers/         # API routes
│   │   ├── auth.py
│   │   └── notes.py
│   ├── services/        # Business logic
│   │   ├── auth.py
│   │   └── notes.py
│   ├── utils/           # Utilities
│   │   ├── security.py
│   │   └── dependencies.py
│   ├── config.py        # Settings
│   ├── database.py      # Database connection
│   └── main.py          # FastAPI app
├── alembic/             # Database migrations
├── tests/               # Tests
├── requirements.txt     # Dependencies
└── .env                 # Environment variables
```

## Database Commands

```bash
# Connect to PostgreSQL
docker exec -it nexus-postgres psql -U nexus -d nexus_dev

# View tables
\dt

# View users table
SELECT * FROM users;

# View notes table
SELECT * FROM notes;

# Exit
\q
```

## Development Workflow

1. **Make model changes** in `app/models/`
2. **Generate migration**:
   ```bash
   alembic revision --autogenerate -m "Description"
   ```
3. **Review migration** in `alembic/versions/`
4. **Apply migration**:
   ```bash
   alembic upgrade head
   ```
5. **Test changes** via `/docs`

## Troubleshooting

### Port 5432 already in use
Change PostgreSQL port in `docker-compose.yml` and update `DATABASE_URL` in `.env`

### Alembic can't detect models
Ensure all models are imported in `alembic/env.py`

### JWT token errors
- Check `SECRET_KEY` is set in `.env`
- Verify token format: `Bearer {token}`
- Check token expiration time

### CORS errors
Add your frontend URL to `allow_origins` in `app/main.py`

## Next Steps

- Week 2: Frontend TipTap editor integration
- Week 3: Wiki links and full-text search
- Week 4: Polish and testing

---

**Phase 2 Week 1:** Backend Foundation ✅
**Next:** Frontend Editor Integration
