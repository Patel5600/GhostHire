# GhostHire Backend

Production-ready backend for the GhostHire SaaS platform. Built with FastAPI, PostgreSQL (Supabase), and Docker.

## Tech Stack

- **Framework:** FastAPI (Python 3.11)
- **Database:** PostgreSQL (SQLModel + AsyncPG)
- **Authentication:** JWT (OAuth2 Password Bearer)
- **Deployment:** Docker-ready (Render/Railway compatible)

## Project Structure

```
ghosthire/
├── app/
│   ├── api/            # API Endpoints (v1)
│   ├── core/           # Config & Security
│   ├── db/             # Database Session
│   ├── models/         # SQLModel Entity Definitions
│   ├── schemas/        # Pydantic Schemas for Requests
│   └── services/       # Business Logic (Resume Parsing, AI)
├── alembic/            # Migrations (Optional, using Auto-Create for now)
├── Dockerfile
└── requirements.txt
```

## Local Setup

### 1. Requirements
- Docker & Docker Compose
- Python 3.11+ (if running locally without Docker)
- PostgreSQL (or use Docker service)

### 2. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Update `DATABASE_URL`. For local Docker Postgres:
`postgresql+asyncpg://postgres:postgres@localhost:5432/ghosthire`

### 3. Run with Docker
```bash
docker build -t ghosthire .
docker run -p 8000:8000 --env-file .env ghosthire
```

### 4. Run Locally (Dev)
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API Docs will be available at: http://localhost:8000/docs

## Deployment Guide (Free Tier)

### Database (Supabase)
1. Create a free project on [Supabase](https://supabase.com).
2. Get the connection string (Transaction Pooler is recommended for serverless).
3. Replace `DATABASE_URL` in your `.env` (or prompt during deployment).
   - Format: `postgresql+asyncpg://[user]:[password]@[host]:5432/[db_name]`

### Web Service (Render)
1. Fork this repo to GitHub.
2. Create a "New Web Service" on Render.
3. Connect your repository.
4. Select **Docker** as the environment.
5. Add Environment Variables:
   - `DATABASE_URL`: (Your Supabase URL)
   - `SECRET_KEY`: (Generate a secure key)
   - `PYTHON_VERSION`: 3.11.0
   - `AI_API_KEY`: (Optional) Groq or Together.xyz API Key for AI features. (Starts with gsk_ for Groq auto-detect).
6. Deploy.

## API Usage

- **Auth:** POST `/api/v1/auth/top/login` to get a JWT. Use header `Authorization: Bearer <token>` for protected endpoints.
- **Resumes:** POST `/api/v1/resumes/` to upload PDF.
- **Jobs:** POST `/api/v1/jobs/` to track a job.
- **AI:** POST `/api/v1/ai/optimize` to get resume feedback.
- **Scraper:**
  - Trigger: POST `/api/v1/ingest/trigger` with `{ "url": "...", "type": "greenhouse" }`
  - Automated: Scheduler runs daily at midnight (configurable in `app/worker/scheduler.py`).

## Workers & Orchestration (Celery)
This system uses Celery for background workflows.
1. Run Redis (locally or via Docker Service).
2. Start Worker:
   ```bash
   celery -A app.core.celery_app worker --loglevel=info
   ```


## Scraper Setup
1. Ensure Playwright browsers are installed:
   ```bash
   playwright install chromium
   ```
2. The scraper runs headless by default. To debug, set `headless=False` in `app/services/scraper/browser.py`.


## Infrastructure & Deployment
The platform is fully containerized and orchestration-ready.

### Local Orchestration (Docker Compose)
Spin up the entire stack (API, Worker, DB, Redis, Nginx):
```bash
docker-compose up --build
```

### CI/CD Pipeline
- **GitHub Actions** (`.github/workflows/ci_cd.yml`) performs automated testing and linting on push.
- To enable auto-deploy, uncomment the Docker Push and Deploy Hook sections in the YAML file and set your secrets in GitHub.

### Deploy to Render (Free Tier)
1. Link your repo to Render.
2. Use properties from `render.yaml` ("Blueprints").
3. Render will automatically provision:
   - Web Service (API)
   - Background Worker (Celery)
   - Postgres Database
   - Redis Instance

## License
MIT
