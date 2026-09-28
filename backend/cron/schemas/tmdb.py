import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator

TMDBKind = Literal["movie", "tv"]

# TMDB отдаёт пустую строку вместо null для неизвестных дат
OptionalDate = Annotated[datetime.date | None, BeforeValidator(lambda v: v or None)]


class ExportItem(BaseModel):
    """Строка ежедневной выгрузки id."""

    id: int
    popularity: float
    adult: bool | None = None
    video: bool | None = None


class ChangedItem(BaseModel):
    id: int
    adult: bool | None = None


class ChangesPage(BaseModel):
    results: list[ChangedItem]
    page: int
    total_pages: int


class Genre(BaseModel):
    id: int
    name: str


class Country(BaseModel):
    iso_3166_1: str


class ExternalIds(BaseModel):
    imdb_id: str | None = None


class SeasonShort(BaseModel):
    season_number: int
    episode_count: int


class Movie(BaseModel):
    id: int
    title: str
    original_title: str | None = None
    original_language: str | None = None
    overview: str | None = None
    release_date: OptionalDate = None
    status: str | None = None
    runtime: int | None = None
    poster_path: str | None = None
    backdrop_path: str | None = None
    popularity: float = 0
    vote_average: float = 0
    vote_count: int = 0
    genres: list[Genre] = []
    production_countries: list[Country] = []
    external_ids: ExternalIds = ExternalIds()


class Tv(BaseModel):
    id: int
    name: str
    original_name: str | None = None
    original_language: str | None = None
    overview: str | None = None
    first_air_date: OptionalDate = None
    status: str | None = None
    # Scripted | Miniseries | Documentary | Reality | Talk Show | News | Video
    type: str | None = None
    episode_run_time: list[int] = []
    poster_path: str | None = None
    backdrop_path: str | None = None
    popularity: float = 0
    vote_average: float = 0
    vote_count: int = 0
    genres: list[Genre] = []
    origin_country: list[str] = []
    seasons: list[SeasonShort] = []
    external_ids: ExternalIds = ExternalIds()


class Episode(BaseModel):
    season_number: int
    episode_number: int
    name: str | None = None
    air_date: OptionalDate = None
    runtime: int | None = None


class Season(BaseModel):
    season_number: int
    episodes: list[Episode] = []
