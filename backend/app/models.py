from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from .db import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), nullable=False, index=True)  # UUID for session isolation
    kind = Column(String(32), nullable=False)           # "image" | "text"
    source = Column(Text, nullable=True)                # raw text or S3 key
    summary = Column(Text, nullable=False)              # AI-generated summary 
    user_caption = Column(Text, nullable=True)          # original user-provided caption
    labels = Column(Text, nullable=True)                # comma-separated labels
    processing_status = Column(String(32), default="completed")  # "pending" | "completed" | "failed"
    ai_results = Column(JSON, nullable=True)            # faces, labels, ocr_text, location, event_type
    heic_metadata = Column(JSON, nullable=True)         # original HEIC metadata (EXIF, device info, etc)
    original_filename = Column(String(255), nullable=True)  # original filename with extension
    photo_taken_at = Column(DateTime(timezone=True), nullable=True)  # when photo was actually taken (from EXIF)
    created_at = Column(DateTime(timezone=True), server_default=func.now())