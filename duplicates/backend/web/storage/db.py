from uuid import uuid4

from asyncpg import Connection
from sqlalchemy import AsyncAdaptedQueuePool, Boolean
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from typing_extensions import AsyncGenerator

from web.config.settings import settings


Base = declarative_base()


class Jobs(Base):
    __tablename__ = 'jobs'

    uid = Column(String, primary_key=True)

    is_processed = Column(Boolean)

    is_duplicate = Column(Boolean)
    duplicate_link = Column(String)


class CConnection(Connection):
    def _get_unique_id(self, prefix: str) -> str:
        return f'__asyncpg_{prefix}_{uuid4()}__'


def create_engine() -> AsyncEngine:
    return create_async_engine(
        settings.db_url,
        poolclass=AsyncAdaptedQueuePool,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
        connect_args={
            'connection_class': CConnection,
        },
    )


def create_session(_engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,
    )


engine = create_engine()
async_session = create_session(engine)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as db:
        yield db
