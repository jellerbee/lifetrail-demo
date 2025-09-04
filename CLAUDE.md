# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (FastAPI)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./local.db
uvicorn app.main:app --reload
```

### Frontend (Next.js)
```bash
cd frontend
npm install
export NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev        # Development server
npm run build      # Production build
npm run start      # Production server
```

## Architecture

This is a full-stack Life Moments AI application with a clear separation between frontend and backend services.

**Backend Structure** (`backend/app/`):
- `main.py` - FastAPI application with CORS middleware and two main endpoints:
  - `POST /api/process` - Processes text input, extracts keywords, generates summary, stores in DB
  - `GET /api/events` - Returns recent events from database
- `models.py` - SQLAlchemy Event model with fields: id, kind, source, summary, labels, created_at
- `schemas.py` - Pydantic models for request/response validation
- `db.py` - Database session management and SQLAlchemy setup
- `ai.py` - Placeholder AI functions (extract_keywords, summarize) for keyword extraction and text summarization
- `settings.py` - Application configuration using pydantic-settings

**Frontend Structure** (`frontend/app/`):
- `page.tsx` - Main React component with form for text input and timeline of events
- `lib/api.ts` - API client for backend communication with fetch-based methods
- `layout.tsx` - Next.js App Router layout component

**Database**: Single Event table storing life moments with AI-generated summaries and keyword labels.

**Key Data Flow**:
1. User submits text → POST /api/process
2. Backend extracts keywords and generates summary using ai.py functions
3. Event stored in database with original text, summary, and labels
4. Frontend refreshes timeline via GET /api/events

## Environment Variables

Copy `.env.example` files to `.env` in both frontend and backend directories:

**Backend** (`backend/.env`):
- `DATABASE_URL` - Postgres connection string (uses sqlite for local dev)
- `OPENAI_API_KEY` - Optional API key for real LLM integration (currently uses stub)
- `ALLOWED_ORIGINS` - CORS origins (comma-separated)

**Frontend** (`frontend/.env`):
- `NEXT_PUBLIC_BACKEND_URL` - Backend API URL

## Deployment

Configured for Render.com deployment via `render.yaml`:
- Dockerized services for both frontend and backend
- Managed Postgres database
- Automatic service discovery between frontend/backend

## AI Integration

Current implementation uses placeholder functions in `backend/app/ai.py`. To integrate real LLM:
1. Replace `summarize()` function with actual OpenAI/Anthropic API calls
2. Update `extract_keywords()` for better keyword extraction
3. Set `OPENAI_API_KEY` environment variable