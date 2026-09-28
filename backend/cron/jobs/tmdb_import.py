import logging

from config import settings
from schemas.tmdb import TMDBKind
from services.tmdb_sync import TMDBSyncService, format_stats

from jobs.tmdb_deps import tmdb_sync_service

logger = logging.getLogger(__name__)


async def import_tmdb_catalog(limit: int | None = None) -> None:
    """
    Докачать из TMDB тайтлы, которых ещё нет в каталоге.

    Берёт ежедневную выгрузку id, оставляет тайтлы с popularity не ниже порога,
    выкидывает уже импортированные и отсеянные и качает остальные, самые популярные первыми.
    Обновление уже импортированных делает sync_tmdb_changes.
    """
    async with tmdb_sync_service() as sync:
        for kind in ("movie", "tv"):
            await _import_kind(sync, kind, limit)


async def _import_kind(sync: TMDBSyncService, kind: TMDBKind, limit: int | None) -> None:
    export = await sync.tmdb.daily_export(kind, settings.tmdb_min_popularity)
    exclude = await sync.catalog.known_ids(kind) | await sync.state.skipped_ids(kind)
    candidates = sorted(
        (item for item in export if not item.adult and not item.video and item.id not in exclude),
        key=lambda item: item.popularity,
        reverse=True,
    )
    ids = [item.id for item in candidates][:limit]
    logger.info(
        "tmdb import %s: %d popular in export, %d known or skipped, %d to import",
        kind,
        len(export),
        len(exclude),
        len(ids),
    )
    stats = await sync.sync_many(kind, ids)
    logger.info("tmdb import %s: done, %s", kind, format_stats(stats))
