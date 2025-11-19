# Backend Python (FastAPI)

This backend replaces the Node `server/` endpoints with Python FastAPI.

Endpoints:

- POST `/parse` with JSON `{ text, type }` or form-data. Type: `contacts` (default) or `companies`.
- POST `/parse/contacts` with `{ text }`.
- POST `/parse/companies` with `{ text }`.
- GET `/email/health` health check.
- POST `/email/send` with form-data: `asunto`, `para` (comma-separated), `plantilla` (optional), `body`, `files[]` attachments.

## Setup

1. Create and activate venv (already present as `env/` in repo):

```bash
source env/Scripts/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy env file and fill secrets:

```bash
cp .env.example .env
```

Required vars: `GEMINI_KEY_API`, `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` (or anon for read-only), and Gmail `GMAIL_USER` + `GMAIL_PASSWORD_APP`.

4. Run locally with uvicorn (port 3000):

```bash
uvicorn app.main:app --reload --port 3000
```

The Vite dev server proxies `/email` and `/parse` to `http://localhost:3000`.
