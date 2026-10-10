import datetime

from pydantic import BaseModel, ConfigDict

from common.models.enums import LibraryStatus, TitleCategory, TitleStatus, TitleType
from schemas.pagination import PageParams


class TitleShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: TitleType
    category: TitleCategory
    title_ru: str
    title_orig: str | None
    slug: str | None
    year: int | None
    status: TitleStatus
    poster_path: str | None
    episodes_total: int | None


class LibraryItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: TitleShort
    status: LibraryStatus
    rating: int | None
    is_favorite: bool
    episodes_watched: int
    rewatch_count: int
    started_at: datetime.datetime | None
    finished_at: datetime.datetime | None
    updated_at: datetime.datetime


class LibraryParams(PageParams):
    status: LibraryStatus | None = None
    favorite: bool | None = None
