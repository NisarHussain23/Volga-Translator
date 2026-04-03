from fastapi import FastAPI
from api.routes import router
from db.database import Base, engine

app = FastAPI(title="Complete Mid-Level Transcription API")

app.include_router(router)

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
