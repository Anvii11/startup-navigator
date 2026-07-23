# Startup Navigator

AI-powered guide for building a startup — structured articles, curated resources, RAG search, and an admin dashboard.

**Phase 2 complete:** content CMS (categories, articles, resources), public Explore/Resources UI, admin dashboard CRUD, and seeded knowledge base.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React (Vite), Tailwind CSS, React Router, Axios, Framer Motion, React Query |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic, JWT |
| Database | SQLite (upgradeable to PostgreSQL) |

## Project structure

```
├── frontend/          # React SPA
├── backend/           # FastAPI API
├── docs/              # Architecture notes
├── docker-compose.yml # Optional backend container
├── README.md
└── .gitignore
```

## Prerequisites

- Node.js 20+
- Python 3.11+ (3.12 recommended)
- npm

## Backend setup

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # or: cp .env.example .env

# Seed CMS content (10 categories, 40 articles, 30 resources)
python -m app.scripts.seed_content

# Prefer --reload-dir app on Windows to avoid watching .venv
uvicorn app.main:app --reload --reload-dir app --host 127.0.0.1 --port 8000
```

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

On startup the app creates tables and seeds an admin user from `.env`:

- `ADMIN_EMAIL` (default: `admin@example.com`)
- `ADMIN_PASSWORD` (default: `ChangeMeAdmin123!`)

### Public content APIs

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/categories` | List categories |
| GET | `/api/v1/categories/{slug}` | Category detail |
| GET | `/api/v1/categories/{slug}/articles` | Articles in category |
| GET | `/api/v1/articles` | List/search/filter articles |
| GET | `/api/v1/articles/{slug}` | Article detail (+ view increment) |
| GET | `/api/v1/articles/{slug}/related` | Related articles |
| GET | `/api/v1/resources` | List/search/filter resources |

Query params (typical): `page`, `page_size`, `search`, `sort`, `category`, `difficulty`, `type`, `featured`.

### Admin content APIs (Bearer admin JWT)

| Method | Path |
|--------|------|
| CRUD | `/api/v1/admin/categories` |
| CRUD | `/api/v1/admin/articles` |
| CRUD | `/api/v1/admin/resources` |

### Auth API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/login` | Login → JWT |
| POST | `/api/v1/auth/refresh` | Refresh tokens |
| GET | `/api/v1/auth/me` | Current user (Bearer) |

### Alembic

```bash
cd backend
alembic revision --autogenerate -m "message"
alembic upgrade head
```

## Frontend setup

```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

App: http://127.0.0.1:5173

### Key routes

| Path | Description |
|------|-------------|
| `/explore` | Categories sidebar, featured/latest/trending, search |
| `/articles/:slug` | Markdown article reader |
| `/resources` | Filterable resource grid |
| `/admin` | CMS dashboard (admin only) |
| `/admin/articles` | Article CRUD |
| `/admin/categories` | Category CRUD |
| `/admin/resources` | Resource CRUD |
| `/login` / `/register` | Auth forms |

Admin login: `admin@example.com` / `ChangeMeAdmin123!`

## Environment variables

### Backend (`backend/.env`)

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | JWT signing key |
| `DATABASE_URL` | SQLAlchemy URL |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Seeded admin |

### Frontend (`frontend/.env`)

| Variable | Purpose |
|----------|---------|
| `VITE_API_BASE_URL` | API base, e.g. `http://127.0.0.1:8000/api/v1` |

## What is intentionally out of scope (Phase 2)

- AI Search / RAG
- Chat history persistence UI
- Saved articles
- Analytics / search logs UI

## Next phase

AI Search Assistant + RAG pipeline — wait for approval before starting Phase 3.
