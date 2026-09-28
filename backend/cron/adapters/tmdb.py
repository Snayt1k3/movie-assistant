import asyncio
import datetime
import gzip
import json
import logging
from typing import Any, Self

import httpx
from schemas.tmdb import ChangesPage, ExportItem, Movie, Season, TMDBKind, Tv

logger = logging.getLogger(__name__)

API_URL = "https://api.themoviedb.org/3"
EXPORTS_URL = "https://files.tmdb.org/p/exports"
EXPORT_NAMES: dict[TMDBKind, str] = {"movie": "movie_ids", "tv": "tv_series_ids"}

MAX_ATTEMPTS = 5
# в append_to_response можно передать не больше 20 элементов
APPEND_LIMIT = 20
# /changes принимает окно не длиннее 14 дней
CHANGES_MAX_DAYS = 14


class TMDBNotFound(Exception):
    pass


class TMDBClient:
    def __init__(self, token: str, language: str, concurrency: int):
        self._http = httpx.AsyncClient(
            base_url=API_URL,
            headers={"Authorization": f"Bearer {token}"},
            params={"language": language},
            timeout=30,
        )
        self._semaphore = asyncio.Semaphore(concurrency)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._http.aclose()

    async def daily_export(self, kind: TMDBKind, min_popularity: float = 0) -> list[ExportItem]:
        """
        Ежедневная выгрузка всех id, отфильтрованная по популярности.
        Файл за сегодня появляется около 8:00 UTC, поэтому берём вчерашний,
        а если его нет, позавчерашний.
        """
        today = datetime.datetime.now(datetime.UTC).date()
        for days_ago in (1, 2):
            day = today - datetime.timedelta(days=days_ago)
            url = f"{EXPORTS_URL}/{EXPORT_NAMES[kind]}_{day:%m_%d_%Y}.json.gz"
            resp = await self._http.get(url)
            if resp.status_code == 404:
                continue
            resp.raise_for_status()
            # в файле больше миллиона строк, в модели превращаем только прошедшие порог
            rows = (json.loads(line) for line in gzip.decompress(resp.content).splitlines())
            return [
                ExportItem.model_validate(row)
                for row in rows
                if row["popularity"] >= min_popularity
            ]
        raise TMDBNotFound(f"daily export for {kind} not found")

    async def changed_ids(
        self, kind: TMDBKind, start: datetime.date, end: datetime.date
    ) -> set[int]:
        """id тайтлов, изменившихся в TMDB с start по end включительно."""
        ids: set[int] = set()
        page, total_pages = 1, 1
        while page <= total_pages:
            data = await self._get(
                f"/{kind}/changes",
                start_date=start.isoformat(),
                end_date=end.isoformat(),
                page=page,
            )
            changes = ChangesPage.model_validate(data)
            ids.update(item.id for item in changes.results)
            total_pages = changes.total_pages
            page += 1
        return ids

    async def movie(self, movie_id: int) -> Movie:
        data = await self._get(f"/movie/{movie_id}", append_to_response="external_ids")
        return Movie.model_validate(data)

    async def tv(self, tv_id: int) -> Tv:
        data = await self._get(f"/tv/{tv_id}", append_to_response="external_ids")
        return Tv.model_validate(data)

    async def seasons(self, tv_id: int, numbers: list[int]) -> list[Season]:
        """Сезоны со списком серий, пачками по 20 через append_to_response."""
        seasons = []
        for i in range(0, len(numbers), APPEND_LIMIT):
            keys = [f"season/{n}" for n in numbers[i : i + APPEND_LIMIT]]
            data = await self._get(f"/tv/{tv_id}", append_to_response=",".join(keys))
            seasons += [Season.model_validate(data[key]) for key in keys if key in data]
        return seasons

    async def _get(self, path: str, **params: Any) -> dict:
        async with self._semaphore:
            for attempt in range(1, MAX_ATTEMPTS + 1):
                try:
                    resp = await self._http.get(path, params=params)
                except httpx.TransportError as e:
                    if attempt == MAX_ATTEMPTS:
                        raise
                    logger.warning("tmdb %s: %r, retry %d", path, e, attempt)
                    await asyncio.sleep(2**attempt)
                    continue

                if resp.status_code == 404:
                    raise TMDBNotFound(path)
                if resp.status_code == 429 or resp.status_code >= 500:
                    if attempt == MAX_ATTEMPTS:
                        resp.raise_for_status()
                    delay = float(resp.headers.get("Retry-After", 2**attempt))
                    logger.warning("tmdb %s: %d, retry in %.0fs", path, resp.status_code, delay)
                    await asyncio.sleep(delay)
                    continue

                resp.raise_for_status()
                return resp.json()
        raise AssertionError("unreachable")
