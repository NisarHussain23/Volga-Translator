import httpx
import os
from core.config import settings
from core.logging import logger
from db.database import AsyncSessionLocal
from db.repository import TranscriptionRepository

class TranscriptionService:

    @staticmethod
    async def process_job(job_id: int, file_path: str):
        async with AsyncSessionLocal() as session:
            job = await TranscriptionRepository.get_job(session, job_id)

            if not job:
                logger.error(f"JOB {job_id} Not found")
                return

            await TranscriptionRepository.update_job(session, job, "processing")

            retries = 3

            for attempt in range(retries):
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        with open(file_path, "rb") as f:
                            response = await client.post(
                                "https://api.deepgram.com/v1/listen",
                                headers={
                                    "Authorization": f"Token {settings.DEEPGRAM_API_KEY}",
                                    "Content-Type": "application/octet-stream",
                                },
                                content=f.read(),
                            )

                        response.raise_for_status()
                        result = response.json()

                    transcript = (
                        result.get("results", {})
                              .get("channels", [{}])[0]
                              .get("alternatives", [{}])[0]
                              .get("transcript", "")
                    )

                    await TranscriptionRepository.update_job(
                        session, job, "completed", transcript
                    )

                    logger.info(f"[JOB {job.id}] Completed")

                    if os.path.exists(file_path):
                        os.remove(file_path)

                    return

                except httpx.TimeoutException:
                    logger.warning(f"[JOB {job.id}] Timeout {attempt+1}")

                except httpx.HTTPStatusError as e:
                    logger.error(f"[JOB {job.id}] HTTP {e.response.status_code}")
                    break

                except Exception as e:
                    logger.error(f"[JOB {job.id}] Error {str(e)}")

            await TranscriptionRepository.update_job(session, job, "failed")
            logger.error(f"[JOB {job.id}] Failed")
