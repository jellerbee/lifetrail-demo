from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import threading
from .settings import settings
from .db import Base, engine, SessionLocal
from . import models, schemas
from .ai import extract_keywords, summarize
from .s3 import upload_image_to_s3
from .image_processor import process_image_async

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

@app.post("/api/upload", response_model=schemas.EventOut)
async def upload_image(
    file: UploadFile = File(...),
    caption: str = Form(...),
    db: Session = Depends(get_db)
):
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file content
    image_bytes = await file.read()
    
    # Upload to S3
    s3_key = upload_image_to_s3(image_bytes, file.filename)
    
    # Create event with pending status
    event = models.Event(
        kind="image",
        source=s3_key,
        summary=caption,
        processing_status="pending"
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # Start background processing
    threading.Thread(
        target=process_image_async,
        args=(event.id, s3_key, caption),
        daemon=True
    ).start()
    
    return event

@app.get("/api/events", response_model=list[schemas.EventOut])
async def list_events(db: Session = Depends(get_db)):
    return db.query(models.Event).order_by(models.Event.id.desc()).limit(50).all()