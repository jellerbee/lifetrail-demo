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