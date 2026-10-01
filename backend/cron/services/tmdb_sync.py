import asyncio
import enum
import logging
import time
from collections import Counter

from adapters.tmdb import TMDBClient, TMDBNotFound
from adapters.tmdb_state import TMDBSyncState
from schemas.tmdb import TMDBKind
from utils.tmdb_mapping import regular_season_numbers

from services.tmdb_catalog import TMDBCatalogService

logger = logging.getLogger(__name__)

BATCH_SIZE = 200


class SyncResult(enum.StrEnum):
    saved = "saved"
    skipped = "skipped"
    not_found = "not_found"
    failed = "failed"


class TMDBSyncService:
    """Скачать тайтлы из TMDB и сохранить в каталог. Общая часть импорта и обновления."""

    def __init__(
        self,
        tmdb: TMDBClient,
        catalog: TMDBCatalogService,
        state: TMDBSyncState,
        skip_tv_types: set[str],
    ):
        self.tmdb = tmdb
        self.catalog = catalog
        self.state = state
        self.skip_tv_types = skip_tv_types

    async def sync_many(self, kind: TMDBKind, ids: list[int]) -> Counter[SyncResult]:
        stats: Counter[SyncResult] = Counter()
        started = time.monotonic()

        for i in range(0, len(ids), BATCH_SIZE):
            batch = ids[i: i + BATCH_SIZE]
            stats.update(await asyncio.gather(*(self.sync_one(kind, tmdb_id) for tmdb_id in batch)))

            logger.info(
                "tmdb %s: %d/%d, %s, %.0fs",
                kind,
                i + len(batch),
                len(ids),
                format_stats(stats),
                time.monotonic() - started,
            )

        return stats

    async def sync_one(self, kind: TMDBKind, tmdb_id: int) -> SyncResult:
        try:
            if kind == "movie":
                await self.catalog.save_movie(await self.tmdb.movie(tmdb_id))
                return SyncResult.saved

            tv = await self.tmdb.tv(tmdb_id)

            if tv.type in self.skip_tv_types:
                await self.state.add_skipped(kind, tmdb_id)
                return SyncResult.skipped

            seasons = await self.tmdb.seasons(tmdb_id, regular_season_numbers(tv))
            await self.catalog.save_tv(tv, seasons)

            return SyncResult.saved

        except TMDBNotFound:
            logger.warning("tmdb %s/%d: not found", kind, tmdb_id)
            return SyncResult.not_found

        except Exception:
            # один битый тайтл не должен останавливать всю пачку
            logger.exception("tmdb %s/%d: failed", kind, tmdb_id)
            return SyncResult.failed


def format_stats(stats: Counter[SyncResult]) -> str:
    return ", ".join(f"{result} {stats[result]}" for result in SyncResult if stats[result])
