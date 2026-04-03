from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import os
import shutil

from models.schemas import TranscriptionResponse
from db.repository import TranscriptionRepository
from db.database import get_db
from services.Tservice import TranscriptionService

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=TranscriptionResponse)
async def upload_audio(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
):
    if not file.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    job = await TranscriptionRepository.create_job(db, file_path)

    background_tasks.add_task(
        TranscriptionService.process_job,
        job.id,
        file_path
    )

    return TranscriptionResponse(job_id=job.id, status=job.status)

@router.get("/transcribe/{job_id}", response_model=TranscriptionResponse)
async def get_transcription(job_id: int, db: AsyncSession = Depends(get_db)):
    job = await TranscriptionRepository.get_job(db, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return TranscriptionResponse(
        job_id=job.id,
        status=job.status,
        transcript=job.transcript,
    )
