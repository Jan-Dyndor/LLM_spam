from sqlalchemy.orm import DeclarativeBase
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

db_file_location = Path(__file__).resolve().parents[3]

sql_url = f"sqlite+aiosqlite:///{db_file_location}/data/data.db"

engine = create_async_engine(url=sql_url, connect_args={"check_same_thread": False})

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
