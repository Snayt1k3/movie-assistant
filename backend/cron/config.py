from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    tmdb_read_api_key: str
    tmdb_language: str = "en-EN"
    # ниже порога тайтлы не импортируем: ≥3 это ~25 тыс. фильмов и ~50 тыс. сериалов
    tmdb_min_popularity: float = 3.0
    # TMDB держит около 50 rps с одного IP
    tmdb_concurrency: int = 20
    # сериалы этих типов не импортируем: тысячи выпусков, которые никто не отмечает
    tmdb_skip_tv_types: set[str] = {"News", "Talk Show"}


settings = Settings()
