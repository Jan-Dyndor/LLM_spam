from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


def create_db_engine(settings):
    db_url = settings.postgres.db_url
    return create_async_engine(url=db_url)


def create_db_async_session(engine):
    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )
    return AsyncSessionLocal


class Base(DeclarativeBase):
    pass
