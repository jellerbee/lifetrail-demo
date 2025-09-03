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