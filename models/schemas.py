from pydantic import BaseModel
from typing import Optional

class TranscriptionResponse(BaseModel):
    job_id: int
    status: str
    transcript: Optional[str] = None
