import enum

from sqlalchemy.dialects.postgresql import ENUM


class TitleType(enum.StrEnum):
    movie = "movie"
    show = "show"


class TitleCategory(enum.StrEnum):
    film = "film"
    series = "series"
    anime = "anime"


class TitleStatus(enum.StrEnum):
    announced = "announced"
    ongoing = "ongoing"
    ended = "ended"
    released = "released"
    canceled = "canceled"


class LibraryStatus(enum.StrEnum):
    planned = "planned"
    watching = "watching"
    completed = "completed"
    on_hold = "on_hold"
    dropped = "dropped"


class Visibility(enum.StrEnum):
    public = "public"
    followers = "followers"
    private = "private"


def pg_enum(enum_cls: type[enum.StrEnum], name: str) -> ENUM:
    return ENUM(enum_cls, name=name, values_callable=lambda e: [m.value for m in e])


title_type_enum = pg_enum(TitleType, "title_type")
title_category_enum = pg_enum(TitleCategory, "title_category")
title_status_enum = pg_enum(TitleStatus, "title_status")
library_status_enum = pg_enum(LibraryStatus, "library_status")
visibility_enum = pg_enum(Visibility, "visibility")
