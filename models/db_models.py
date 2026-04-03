from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from db.database import Base

class TranscriptionJob(Base):
    __tablename__ = "transcription_jobs"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    status = Column(String, default="pending")
    transcript = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#