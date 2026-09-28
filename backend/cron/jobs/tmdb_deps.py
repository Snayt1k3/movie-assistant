from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from adapters.tmdb import TMDBClient
from adapters.tmdb_state import TMDBSyncState
from config import settings
from redis.asyncio import Redis
from services.tmdb_catalog import TMDBCatalogService
from services.tmdb_sync import TMDBSyncService

from common.config import settings as common_settings
from common.db import session_factory
from common.uow import SqlAlchemyUnitOfWork


@asynccontextmanager
async def tmdb_sync_service() -> AsyncIterator[TMDBSyncService]:
    redis = Redis.from_url(common_settings.redis_url)
    try:
        async with TMDBClient(
            settings.tmdb_read_api_key, settings.tmdb_language, settings.tmdb_concurrency
        ) as tmdb:
            yield TMDBSyncService(
                tmdb=tmdb,
                catalog=TMDBCatalogService(lambda: SqlAlchemyUnitOfWork(session_factory)),
                state=TMDBSyncState(redis),
                skip_tv_types=settings.tmdb_skip_tv_types,
            )
    finally:
        await redis.aclose()
