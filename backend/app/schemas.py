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