from pydantic import BaseModel
from typing import Dict, Any

class ProcessTextRequest(BaseModel):
    text: str

class UploadImageRequest(BaseModel):
    caption: str

class EventOut(BaseModel):
    id: int
    kind: str
    source: str | None
    summary: str
    labels: str | None
    processing_status: str
    ai_results: Dict[str, Any] | None

    class Config:
        from_attributes = True