import datetime

from redis.asyncio import Redis
from schemas.tmdb import TMDBKind

SKIPPED_KEY = "tmdb:skipped:{kind}"
CHANGES_CURSOR_KEY = "tmdb:changes:last_date"


class TMDBSyncState:
    """
    Служебное состояние синхронизации с TMDB.

    - отсеянные тайтлы (новости, ток-шоу), чтобы не запрашивать их каждый день заново;
      если список отсеиваемых типов поменяется, ключ нужно удалить руками;
    - дата, с которой job по changes продолжит в следующий раз.
    """

    def __init__(self, redis: Redis):
        self.redis = redis

    async def skipped_ids(self, kind: TMDBKind) -> set[int]:
        members = await self.redis.smembers(SKIPPED_KEY.format(kind=kind))
        return {int(m) for m in members}

    async def add_skipped(self, kind: TMDBKind, tmdb_id: int) -> None:
        await self.redis.sadd(SKIPPED_KEY.format(kind=kind), tmdb_id)

    async def changes_cursor(self) -> datetime.date | None:
        value = await self.redis.get(CHANGES_CURSOR_KEY)
        return datetime.date.fromisoformat(value.decode()) if value else None

    async def set_changes_cursor(self, day: datetime.date) -> None:
        await self.redis.set(CHANGES_CURSOR_KEY, day.isoformat())
