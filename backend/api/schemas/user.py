import datetime
from functools import cache
from typing import Annotated, Self
from zoneinfo import available_timezones

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

from common.models.enums import LibraryStatus, Visibility

# первая буква обязательна: так username не спутать с числовым id в /users/{ref}
USERNAME_PATTERN = r"^[A-Za-z][A-Za-z0-9_]{2,31}$"

# числовой id или username в пути; FastAPI не умеет модели для path-параметров
UserRef = Annotated[str, Path(pattern=r"^(\d{1,18}|[A-Za-z][A-Za-z0-9_]{2,31})$")]

# в базе эти поля not null: их можно поменять, но не стереть
NOT_NULL_FIELDS = ("display_name", "locale", "timezone", "profile_visibility")


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str | None
    email: str | None
    telegram_id: int | None
    display_name: str
    avatar_url: str | None
    locale: str
    timezone: str
    profile_visibility: Visibility
    is_pro: bool


class UserShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str | None
    display_name: str
    avatar_url: str | None
    is_pro: bool


@cache
def _timezones() -> frozenset[str]:
    return frozenset(available_timezones())


class UserUpdateIn(BaseModel):
    """Частичное обновление своего профиля: меняются только переданные поля."""

    username: str | None = Field(None, pattern=USERNAME_PATTERN)
    display_name: str | None = Field(None, min_length=1, max_length=64)
    avatar_url: HttpUrl | None = None
    locale: str | None = Field(None, pattern=r"^[a-z]{2}$")
    timezone: str | None = None
    profile_visibility: Visibility | None = None

    @field_validator("timezone")
    @classmethod
    def _known_timezone(cls, value: str | None) -> str | None:
        if value is not None and value not in _timezones():
            raise ValueError("Unknown timezone")
        return value

    @model_validator(mode="after")
    def _no_null_for_required(self) -> Self:
        for name in NOT_NULL_FIELDS:
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self


class ProfileStats(BaseModel):
    library: dict[LibraryStatus, int]
    favorites: int
    rated: int
    avg_rating: float | None
    episodes_watched: int
    followers: int
    following: int
    reviews: int
    collections: int


class ProfileOut(BaseModel):
    id: int
    username: str | None
    display_name: str
    avatar_url: str | None
    profile_visibility: Visibility
    is_pro: bool
    created_at: datetime.datetime
    is_me: bool
    is_following: bool
    follows_you: bool
    # None, если настройки видимости скрывают профиль от зрителя
    stats: ProfileStats | None
