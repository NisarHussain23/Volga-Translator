from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.db_models import TranscriptionJob

class TranscriptionRepository:

    @staticmethod
    async def create_job(session: AsyncSession, file_path: str) -> TranscriptionJob:
        job = TranscriptionJob(file_path=file_path, status="pending")
        session.add(job)
        await session.commit()
        await session.refresh(job)
        return job

    @staticmethod
    async def get_job(session: AsyncSession, job_id: int):
        result = await session.execute(
            select(TranscriptionJob).where(TranscriptionJob.id == job_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_job(session: AsyncSession, job: TranscriptionJob, status: str, transcript: str = None):
        job.status = status
        if transcript is not None:
            job.transcript = transcript
        session.add(job)
        await session.commit()