import datetime

from schemas.tmdb import Genre, Movie, Season, TMDBKind, Tv

from common.models.enums import TitleCategory, TitleStatus, TitleType

TMDB_PROVIDER = "tmdb"
IMDB_PROVIDER = "imdb"
ANIMATION_GENRE_ID = 16

MOVIE_STATUSES = {
    "Released": TitleStatus.released,
    "Canceled": TitleStatus.canceled,
}
TV_STATUSES = {
    "Returning Series": TitleStatus.ongoing,
    "Ended": TitleStatus.ended,
    "Canceled": TitleStatus.canceled,
}


def tmdb_external_id(kind: TMDBKind, tmdb_id: int) -> str:
    """id фильмов и сериалов в TMDB пересекаются, поэтому храним вместе с типом: movie/603."""
    return f"{kind}/{tmdb_id}"


def movie_to_title(movie: Movie) -> dict:
    return {
        "type": TitleType.movie,
        "category": _category(movie.genres, movie.original_language, TitleCategory.film),
        "title_ru": movie.title,
        "title_orig": movie.original_title,
        "year": movie.release_date.year if movie.release_date else None,
        # всё, что ещё не вышло: Rumored, Planned, In Production, Post Production
        "status": MOVIE_STATUSES.get(movie.status or "", TitleStatus.announced),
        "overview": movie.overview or None,
        "runtime_min": movie.runtime or None,
        "poster_path": movie.poster_path,
        "backdrop_path": movie.backdrop_path,
        "genres": [g.name for g in movie.genres],
        "countries": [c.iso_3166_1 for c in movie.production_countries],
        "ext_rating": _rating(movie.vote_average, movie.vote_count),
        "popularity": movie.popularity,
        "synced_at": _now(),
    }


def tv_to_title(tv: Tv) -> dict:
    return {
        "type": TitleType.show,
        "category": _category(tv.genres, tv.original_language, TitleCategory.series),
        "title_ru": tv.name,
        "title_orig": tv.original_name,
        "year": tv.first_air_date.year if tv.first_air_date else None,
        # Planned, In Production, Pilot
        "status": TV_STATUSES.get(tv.status or "", TitleStatus.announced),
        "overview": tv.overview or None,
        "runtime_min": tv.episode_run_time[0] if tv.episode_run_time else None,
        "poster_path": tv.poster_path,
        "backdrop_path": tv.backdrop_path,
        "genres": [g.name for g in tv.genres],
        "countries": tv.origin_country,
        "episodes_total": sum(s.episode_count for s in tv.seasons if s.season_number > 0),
        "ext_rating": _rating(tv.vote_average, tv.vote_count),
        "popularity": tv.popularity,
        "synced_at": _now(),
    }


def regular_season_numbers(tv: Tv) -> list[int]:
    """Сезон 0 в TMDB это спецвыпуски, в прогресс их не берём."""
    return [s.season_number for s in tv.seasons if s.season_number > 0]


def season_to_episodes(title_id: int, season: Season) -> list[dict]:
    return [
        {
            "title_id": title_id,
            "season": ep.season_number,
            "number": ep.episode_number,
            "name": ep.name or None,
            # TMDB знает только дату выхода, без времени
            "air_date": _midnight_utc(ep.air_date) if ep.air_date else None,
            "runtime_min": ep.runtime or None,
        }
        for ep in season.episodes
    ]


def _category(
    genres: list[Genre], original_language: str | None, default: TitleCategory
) -> TitleCategory:
    is_animation = any(g.id == ANIMATION_GENRE_ID for g in genres)
    if is_animation and original_language == "ja":
        return TitleCategory.anime
    return default


def _rating(vote_average: float, vote_count: int) -> float | None:
    return round(vote_average, 1) if vote_count else None


def _midnight_utc(day: datetime.date) -> datetime.datetime:
    return datetime.datetime.combine(day, datetime.time.min, tzinfo=datetime.UTC)


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)
