from collections.abc import Callable

from schemas.tmdb import Movie, Season, TMDBKind, Tv
from utils.tmdb_mapping import (
    IMDB_PROVIDER,
    TMDB_PROVIDER,
    movie_to_title,
    season_to_episodes,
    tmdb_external_id,
    tv_to_title,
)

from common.interfaces import AbstractUow


class TMDBCatalogService:
    def __init__(self, uow_factory: Callable[[], AbstractUow]):
        self.uow_factory = uow_factory

    async def known_ids(self, kind: TMDBKind) -> set[int]:
        """TMDB id тайтлов этого типа, которые уже есть в каталоге."""
        async with self.uow_factory() as uow:
            external_ids = await uow.title_external_ids.list_external_ids(
                TMDB_PROVIDER, prefix=f"{kind}/"
            )
        return {int(ext.split("/", 1)[1]) for ext in external_ids}

    async def save_movie(self, movie: Movie) -> int:
        async with self.uow_factory() as uow:
            return await self._upsert_title(
                uow,
                tmdb_external_id("movie", movie.id),
                movie_to_title(movie),
                movie.external_ids.imdb_id,
            )

    async def save_tv(self, tv: Tv, seasons: list[Season]) -> int:
        async with self.uow_factory() as uow:
            title_id = await self._upsert_title(
                uow,
                tmdb_external_id("tv", tv.id),
                tv_to_title(tv),
                tv.external_ids.imdb_id,
            )
            episodes = [ep for s in seasons for ep in season_to_episodes(title_id, s)]
            await uow.episodes.upsert_many(episodes)
            return title_id

    async def _upsert_title(
        self, uow: AbstractUow, external_id: str, values: dict, imdb_id: str | None
    ) -> int:
        found = await uow.title_external_ids.find_title_ids(TMDB_PROVIDER, [external_id])
        if title_id := found.get(external_id):
            await uow.titles.update_one(title_id, **values)
        else:
            title_id = (await uow.titles.add_one(**values)).id

        links = [
            {
                "provider": TMDB_PROVIDER,
                "external_id": external_id,
                "title_id": title_id,
                "is_primary": True,
            }
        ]
        # imdb id пригодится для склейки с Кинопоиском и Letterboxd
        if imdb_id:
            links.append(
                {
                    "provider": IMDB_PROVIDER,
                    "external_id": imdb_id,
                    "title_id": title_id,
                    "is_primary": False,
                }
            )
        await uow.title_external_ids.add_many_ignore_conflicts(links)
        return title_id
