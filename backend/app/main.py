from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import threading
from .settings import settings
from .db import Base, engine, SessionLocal
from . import models, schemas
from .ai import extract_keywords, summarize
from .s3 import upload_image_to_s3, get_s3_url
from .image_processor import process_image_async
from .heic_processor import is_heic_file, process_heic_upload

# Run database migration first
try:
    from .migrate import migrate_database
    migrate_database()
except Exception as e:
    print(f"Migration failed: {e}")

# Run database initialization if configured
try:
    from .db_init import run_database_initialization
    run_database_initialization(settings.db_init_mode)
except Exception as e:
    print(f"Database initialization failed: {e}")
    # Don't raise here to allow app to continue if initialization fails

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Life Moments AI Backend")

# Debug CORS settings
print(f"CORS allowed origins: {settings.allowed_origins_list}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
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
async def process_text(payload: schemas.ProcessTextRequest, session_id: str, db: Session = Depends(get_db)):
    labels = ",".join(extract_keywords(payload.text))
    summary = await summarize(payload.text)
    ev = models.Event(session_id=session_id, kind="text", source=payload.text[:2000], summary=summary, labels=labels)
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev

@app.post("/api/upload", response_model=schemas.EventOut)
async def upload_image(
    file: UploadFile = File(...),
    caption: str = Form(""),
    session_id: str = Form(...),
    db: Session = Depends(get_db)
):
    # Validate file type (accept both regular images and HEIC)
    is_heic = is_heic_file(file.filename or "")
    if not (file.content_type and file.content_type.startswith('image/')) and not is_heic:
        raise HTTPException(status_code=400, detail="File must be an image (including HEIC/HEIF)")
    
    # Read file content
    image_bytes = await file.read()
    heic_metadata = None
    final_filename = file.filename
    
    # Process HEIC files
    if is_heic:
        try:
            # Extract metadata and convert to JPEG
            image_bytes, heic_metadata = process_heic_upload(image_bytes, file.filename or "")
            # Change filename extension to .jpg for S3 storage
            base_name = (file.filename or "image").rsplit('.', 1)[0]
            final_filename = f"{base_name}.jpg"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to process HEIC image: {str(e)}")
    
    # Upload to S3 (now JPEG if converted from HEIC)
    s3_key = upload_image_to_s3(image_bytes, final_filename)
    
    # Create event with pending status
    event = models.Event(
        session_id=session_id,
        kind="image",
        source=s3_key,
        summary="Processing...",  # Will be replaced with AI summary
        user_caption=caption,     # Store original user caption
        processing_status="pending",
        heic_metadata=heic_metadata,
        original_filename=file.filename
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

@app.get("/api/s3-config")
async def get_s3_config():
    return {
        "bucket_name": settings.aws_bucket_name,
        "region": settings.aws_region
    }

@app.get("/api/events", response_model=list[schemas.EventOut])
async def list_events(session_id: str, db: Session = Depends(get_db)):
    return db.query(models.Event).filter(models.Event.session_id == session_id).order_by(models.Event.id.desc()).limit(50).all()

@app.post("/api/truncate-events")
async def truncate_events(db: Session = Depends(get_db)):
    """
    DEBUG ENDPOINT: Truncate all events from the database.
    TODO: Add proper authentication/authorization for this endpoint in production.
    TODO: Consider adding S3 cleanup to also delete associated image files.
    """
    try:
        # Delete all events
        count = db.query(models.Event).count()
        db.query(models.Event).delete()
        db.commit()
        
        return {"message": f"Successfully deleted {count} events", "deleted_count": count}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to truncate events: {str(e)}")

from fastapi.responses import Response

@app.get("/api/image-url/{s3_key:path}")
async def get_image_url(s3_key: str):
    """Get presigned URL for S3 image"""
    try:
        url = get_s3_url(s3_key)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate image URL: {str(e)}")

@app.get("/api/image/{s3_key:path}")
async def get_image_proxy(s3_key: str):
    """Proxy S3 images through backend"""
    try:
        from .s3 import get_s3_client
        s3_client = get_s3_client()
        
        # Get image from S3
        response = s3_client.get_object(Bucket=settings.aws_bucket_name, Key=s3_key)
        image_data = response['Body'].read()
        
        # Return image with appropriate headers
        return Response(
            content=image_data,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "public, max-age=3600"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Image not found: {str(e)}")