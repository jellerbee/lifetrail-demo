from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from .db import Base

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    kind = Column(String(32), nullable=False)           # "image" | "text"
    source = Column(Text, nullable=True)                # raw text or S3 key
    summary = Column(Text, nullable=False)              # AI summary or user caption
    labels = Column(Text, nullable=True)                # comma-separated labels
    processing_status = Column(String(32), default="completed")  # "pending" | "completed" | "failed"
    ai_results = Column(JSON, nullable=True)            # faces, labels, ocr_text, location, event_type
    created_at = Column(DateTime(timezone=True), server_default=func.now())