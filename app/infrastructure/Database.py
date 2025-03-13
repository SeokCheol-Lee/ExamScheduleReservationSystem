from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# 실제 PostgreSQL 연결 정보로 변경
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/Reservation"
# 개발 또는 테스트 환경에서는 아래와 같이 SQLite 사용 가능
# DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()
