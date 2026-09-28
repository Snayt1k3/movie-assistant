import datetime
import logging

from adapters.tmdb import CHANGES_MAX_DAYS
from services.tmdb_sync import SyncResult, format_stats

from jobs.tmdb_deps import tmdb_sync_service

logger = logging.getLogger(__name__)


async def sync_tmdb_changes(limit: int | None = None) -> None:
    """
    Обновить тайтлы каталога, которые изменились в TMDB: статус, рейтинг, новые серии.

    Окно изменений начинается с даты прошлого успешного запуска. Дата сдвигается,
    только если все тайтлы обновились, иначе следующий запуск пройдёт окно заново.
    TMDB отдаёт изменения не больше чем за 14 дней, более старые пропуски не догнать.
    """
    today = datetime.datetime.now(datetime.UTC).date()
    async with tmdb_sync_service() as sync:
        oldest = today - datetime.timedelta(days=CHANGES_MAX_DAYS - 1)
        start = await sync.state.changes_cursor() or today - datetime.timedelta(days=1)
        if start < oldest:
            logger.warning(
                "tmdb changes: last sync %s is older than 14 days, gap until %s", start, oldest
            )
            start = oldest

        all_ok = True
        for kind in ("movie", "tv"):
            changed = await sync.tmdb.changed_ids(kind, start, today)
            known = await sync.catalog.known_ids(kind)
            ids = sorted(changed & known)[:limit]
            logger.info(
                "tmdb changes %s since %s: %d changed, %d in catalog",
                kind,
                start,
                len(changed),
                len(ids),
            )
            stats = await sync.sync_many(kind, ids)
            logger.info("tmdb changes %s: done, %s", kind, format_stats(stats))
            all_ok = all_ok and not stats[SyncResult.failed]

        if all_ok and limit is None:
            await sync.state.set_changes_cursor(today)
