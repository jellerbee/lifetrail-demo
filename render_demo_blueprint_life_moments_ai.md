# Render Demo Blueprint — *Life Moments AI* (FastAPI + Next.js + Postgres)

A small, production-shaped demo to accompany your Render application. It shows a multi-service architecture (FastAPI backend, Next.js frontend, managed Postgres) with an AI summarization step and a timeline UI — exactly the kind of content a DevRel Engineer would publish.

---

## 1) Repo layout
```
life-moments-ai/
├─ render.yaml                 # Render Infra-as-code (2 services + 1 database)
├─ README.md                   # Project overview + quickstart
├─ .env.example                # Shared env hints (no secrets)
├─ backend/
│  ├─ Dockerfile
│  ├─ requirements.txt
│  ├─ app/
│  │  ├─ main.py              # FastAPI app (health, /api/process)
│  │  ├─ db.py                # SQLAlchemy engine/session
│  │  ├─ models.py            # SQLAlchemy models (Event)
│  │  ├─ schemas.py           # Pydantic models
│  │  ├─ ai.py                # GPT call + simple keyword extraction
│  │  └─ settings.py          # Pydantic Settings (env vars)
│  └─ alembic/ (optional)     # If you later add migrations
└─ frontend/
   ├─ Dockerfile
   ├─ package.json
   ├─ next.config.js
   ├─ tsconfig.json
   ├─ app/
   │  ├─ page.tsx            # Upload + timeline list
   │  ├─ layout.tsx          # Basic shell
   │  └─ lib/api.ts          # Client helper to call backend
   └─ public/
```

---

## 2) Environment variables
Create per-service envs in Render dashboard. Keep secrets out of git. Example:

```
# .env.example (do not commit real secrets)
# Backend
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DB
OPENAI_API_KEY=sk-... (or other LLM provider key)
ALLOWED_ORIGINS=https://your-frontend.onrender.com,http://localhost:3000

# Frontend
NEXT_PUBLIC_BACKEND_URL=https://your-backend.onrender.com
```

---

## 3) FastAPI backend (minimal scaffolding)

**backend/requirements.txt**
```
fastapi==0.112.2
uvicorn[standard]==0.30.6
pydantic==2.8.2
pydantic-settings==2.4.0
SQLAlchemy==2.0.34
psycopg2-binary==2.9.9
httpx==0.27.2
python-multipart==0.0.9
```

**backend/app/settings.py**
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str | None = None
    allowed_origins: List[str] = ["http://localhost:3000"]

    class Config:
        env_prefix = ""
        env_file = ".env"

settings = Settings()
```

**backend/app/db.py**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .settings import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass
```

**backend/app/models.py**
```python
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .db import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    kind = Column(String(32), nullable=False)           # "image" | "text"
    source = Column(Text, nullable=True)                # raw text or object key
    summary = Column(Text, nullable=False)              # AI summary
    labels = Column(Text, nullable=True)                # comma-separated labels
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**backend/app/schemas.py**
```python
from pydantic import BaseModel

class ProcessTextRequest(BaseModel):
    text: str

class EventOut(BaseModel):
    id: int
    kind: str
    source: str | None
    summary: str
    labels: str | None

    class Config:
        from_attributes = True
```

**backend/app/ai.py** (placeholder logic; swap with your preferred LLM)
```python
import re
from typing import List

# very simple keyword extractor placeholder
def extract_keywords(text: str, k: int = 5) -> List[str]:
    words = re.findall(r"[A-Za-z0-9_]+", text.lower())
    freq = {}
    for w in words:
        if len(w) < 3: continue
        freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:k]]

# simple "AI" summarizer stub (replace with real LLM call)
async def summarize(text: str) -> str:
    return f"Life Moment: {text[:160]}..." if len(text) > 160 else f"Life Moment: {text}"
```

**backend/app/main.py**
```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .settings import settings
from .db import Base, engine, SessionLocal
from . import models, schemas
from .ai import extract_keywords, summarize

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Life Moments AI Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/process", response_model=schemas.EventOut)
async def process_text(payload: schemas.ProcessTextRequest, db: Session = Depends(get_db)):
    labels = ",".join(extract_keywords(payload.text))
    summary = await summarize(payload.text)
    ev = models.Event(kind="text", source=payload.text[:2000], summary=summary, labels=labels)
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev

@app.get("/api/events", response_model=list[schemas.EventOut])
async def list_events(db: Session = Depends(get_db)):
    return db.query(models.Event).order_by(models.Event.id.desc()).limit(50).all()
```

**backend/Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
ENV PORT=8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 4) Next.js frontend (App Router, minimal UI)

**frontend/package.json**
```json
{
  "name": "life-moments-frontend",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start -p 3000"
  },
  "dependencies": {
    "next": "14.2.5",
    "react": "18.3.1",
    "react-dom": "18.3.1"
  }
}
```

**frontend/next.config.js**
```js
/** @type {import('next').NextConfig} */
const nextConfig = { reactStrictMode: true };
module.exports = nextConfig;
```

**frontend/app/lib/api.ts**
```ts
export const api = {
  base: process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000",
  async process(text: string) {
    const res = await fetch(`${this.base}/api/process`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });
    if (!res.ok) throw new Error("Request failed");
    return res.json();
  },
  async events() {
    const res = await fetch(`${this.base}/api/events`, { cache: "no-store" });
    if (!res.ok) throw new Error("Request failed");
    return res.json();
  }
};
```

**frontend/app/layout.tsx**
```tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ maxWidth: 900, margin: "2rem auto", padding: "0 1rem", fontFamily: "ui-sans-serif, system-ui" }}>
        <h1>Life Moments AI</h1>
        <p>FastAPI + Next.js on Render • AI summarized timeline</p>
        {children}
      </body>
    </html>
  );
}
```

**frontend/app/page.tsx**
```tsx
"use client";
import { useEffect, useState } from "react";
import { api } from "./lib/api";

type Event = { id: number; kind: string; source?: string; summary: string; labels?: string };

export default function Page() {
  const [text, setText] = useState("");
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);

  async function refresh() {
    try { setEvents(await api.events()); } catch (e) { console.error(e); }
  }
  useEffect(() => { refresh(); }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await api.process(text);
      setText("");
      await refresh();
    } finally { setLoading(false); }
  }

  return (
    <div>
      <form onSubmit={onSubmit} style={{ display: "flex", gap: 8, marginTop: 16 }}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste a sentence about a life moment..."
          style={{ flex: 1, padding: 8 }}
        />
        <button disabled={loading || !text} type="submit">Add</button>
      </form>
      <h2 style={{ marginTop: 24 }}>Recent Moments</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {events.map(ev => (
          <li key={ev.id} style={{ padding: 12, border: "1px solid #eee", borderRadius: 8, marginTop: 8 }}>
            <div style={{ fontSize: 12, opacity: 0.7 }}>{ev.labels}</div>
            <div style={{ fontWeight: 600 }}>{ev.summary}</div>
            <div style={{ fontSize: 12, marginTop: 4, whiteSpace: "pre-wrap" }}>{ev.source}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

**frontend/Dockerfile**
```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci --ignore-scripts || npm i --ignore-scripts

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["npm", "start"]
```

---

## 5) Render IaC (render.yaml)

```yaml
services:
  - type: web
    name: life-moments-backend
    env: docker
    plan: starter
    rootDir: backend
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase: life-moments-db
        property: connectionString
      - key: ALLOWED_ORIGINS
        value: https://life-moments-frontend.onrender.com, http://localhost:3000
    healthCheckPath: /health

  - type: web
    name: life-moments-frontend
    env: docker
    plan: starter
    rootDir: frontend
    dockerfilePath: ./Dockerfile
    envVars:
      - key: NEXT_PUBLIC_BACKEND_URL
        fromService:
          name: life-moments-backend
          type: web
          envVarKey: RENDER_EXTERNAL_URL

databases:
  - name: life-moments-db
    plan: starter
```

> After first deploy, Render will provide `RENDER_EXTERNAL_URL` for the backend; the frontend consumes it via `NEXT_PUBLIC_BACKEND_URL`.

---

## 6) Local dev

**Backend:**
```
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./local.db
uvicorn app.main:app --reload
```
**Frontend:**
```
cd frontend
npm install
export NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
npm run dev
```

---

## 7) README quickstart (suggested content)
1. Click **Deploy to Render** (badge) or connect repo and auto-detect `render.yaml`.
2. Set `ALLOWED_ORIGINS` on backend; confirm database is provisioned.
3. Wait for both services to be healthy; visit frontend URL and add a Life Moment.
4. (Optional) Swap `ai.py` stub with a real LLM call; note cost/keys.

---

## 8) Content plan (what you’ll publish)
- **Blog:** *Building a Multi-Service AI App on Render (FastAPI + Next.js + Postgres)*
- **Quickstart:** *Five-minute deploy — clone, connect, push*
- **Video (3–4 min):** *From zero to deployed: Render walkthrough*
- **Repo Issues:** Good-first-issues (docs fixes, adding image-OCR route, etc.)

---

This blueprint is intentionally minimal yet production-shaped so you can extend it quickly (auth, S3, R2, image OCR route, background jobs).

