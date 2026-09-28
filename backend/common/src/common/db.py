from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from common.config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with session_factory() as session:
        yield session
