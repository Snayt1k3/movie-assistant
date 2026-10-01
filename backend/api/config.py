import datetime

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_ttl: datetime.timedelta = datetime.timedelta(minutes=15)
    refresh_token_ttl: datetime.timedelta = datetime.timedelta(days=30)
    # токеном бота подписаны данные Telegram Login Widget
    bot_token: str
    # старые данные виджета не принимаем, чтобы перехваченную подпись нельзя было переиспользовать
    telegram_auth_max_age: datetime.timedelta = datetime.timedelta(days=1)


settings = Settings()
