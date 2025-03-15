# Database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from fastapi import FastAPI

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/Reservation")
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
Base = declarative_base()

# ★ ORM 모델들을 import하여 Base.metadata에 등록합니다.
from app.infrastructure.ReservationRepository import ReservationORM, ExamScheduleORM

app = FastAPI()

async def reset_database():
    async with engine.begin() as conn:
        print("🔄 Dropping existing tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("✅ Creating new tables...")
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    await reset_database()
