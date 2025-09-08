from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class ProcessTextRequest(BaseModel):
    text: str

class UploadImageRequest(BaseModel):
    caption: str

class EventOut(BaseModel):
    id: int
    kind: str
    source: str | None
    summary: str
    user_caption: str | None
    labels: str | None
    processing_status: str
    ai_results: Dict[str, Any] | None
    heic_metadata: Dict[str, Any] | None
    original_filename: str | None
    photo_taken_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True