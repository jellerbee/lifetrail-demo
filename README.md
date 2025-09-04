# Life Moments AI

A small demo showing a multi-service architecture (FastAPI backend, Next.js frontend, managed Postgres) with an AI summarization step and a timeline UI.

## Quick Start

1. Click **Deploy to Render** (badge) or connect repo and auto-detect `render.yaml`.
2. Set `ALLOWED_ORIGINS` on backend; confirm database is provisioned.
3. Wait for both services to be healthy; visit frontend URL and add a Life Moment.
4. (Optional) Swap `ai.py` stub with a real LLM call; note cost/keys.

## Local Development

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./local.db
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
export NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev
```

## Architecture

- **Backend**: FastAPI with SQLAlchemy and Postgres
- **Frontend**: Next.js with App Router
- **Database**: Managed Postgres on Render
- **AI**: Simple keyword extraction and text summarization (placeholder for real LLM integration)


## Environment Setup

Each service has its own `.env.example` file.  
To run locally, copy them to `.env` and update values as needed:

```bash
# Backend
cp backend/.env.example backend/.env
```

```bash
# Frontend
cp frontend/.env.example frontend/.env
```


---

