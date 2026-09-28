import datetime
from decimal import Decimal

from sqlalchemy import (
    Computed,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base, CreatedAtMixin, IdMixin, UpdatedAtMixin
from common.models.enums import (
    TitleCategory,
    TitleStatus,
    TitleType,
    title_category_enum,
    title_status_enum,
    title_type_enum,
)

SEARCH_VECTOR_SQL = (
    "setweight(to_tsvector('russian', coalesce(title_ru, '')), 'A') || "
    "setweight(to_tsvector('simple', coalesce(title_orig, '')), 'B')"
)


class Title(IdMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "titles"
    __table_args__ = (
        Index("ix_titles_search", "search_vector", postgresql_using="gin"),
        Index(
            "ix_titles_trgm_ru",
            "title_ru",
            postgresql_using="gin",
            postgresql_ops={"title_ru": "gin_trgm_ops"},
        ),
        Index(
            "ix_titles_trgm_orig",
            "title_orig",
            postgresql_using="gin",
            postgresql_ops={"title_orig": "gin_trgm_ops"},
        ),
        Index("ix_titles_popularity", text("popularity desc"), "id"),
        Index("ix_titles_ongoing", "status", postgresql_where=text("status = 'ongoing'")),
    )

    type: Mapped[TitleType] = mapped_column(title_type_enum)
    category: Mapped[TitleCategory] = mapped_column(title_category_enum)
    title_ru: Mapped[str] = mapped_column(Text)
    title_orig: Mapped[str | None] = mapped_column(Text)
    slug: Mapped[str | None] = mapped_column(Text, unique=True)
    year: Mapped[int | None] = mapped_column(SmallInteger)
    status: Mapped[TitleStatus] = mapped_column(
        title_status_enum, server_default=TitleStatus.released
    )
    overview: Mapped[str | None] = mapped_column(Text)
    runtime_min: Mapped[int | None] = mapped_column(SmallInteger)
    poster_path: Mapped[str | None] = mapped_column(Text)
    backdrop_path: Mapped[str | None] = mapped_column(Text)
    genres: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default="{}")
    countries: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default="{}")
    episodes_total: Mapped[int | None] = mapped_column(SmallInteger)
    ext_rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 1))
    popularity: Mapped[float] = mapped_column(server_default="0")
    search_vector: Mapped[str] = mapped_column(
        TSVECTOR, Computed(SEARCH_VECTOR_SQL, persisted=True)
    )
    synced_at: Mapped[datetime.datetime | None]


class TitleExternalId(Base):
    __tablename__ = "title_external_ids"

    # tmdb | kinopoisk | shikimori | anilist | anilibria
    provider: Mapped[str] = mapped_column(Text, primary_key=True)
    external_id: Mapped[str] = mapped_column(Text, primary_key=True)
    title_id: Mapped[int] = mapped_column(ForeignKey("titles.id", ondelete="CASCADE"), index=True)
    is_primary: Mapped[bool] = mapped_column(server_default=text("false"))
    payload: Mapped[dict | None] = mapped_column(JSONB)
    synced_at: Mapped[datetime.datetime | None]


class Episode(IdMixin, Base):
    __tablename__ = "episodes"
    __table_args__ = (
        UniqueConstraint("title_id", "season", "number"),
        Index("ix_episodes_title_rank", "title_id", "rank"),
        Index("ix_episodes_air_date", "air_date", postgresql_where=text("air_date is not null")),
    )

    title_id: Mapped[int] = mapped_column(ForeignKey("titles.id", ondelete="CASCADE"))
    season: Mapped[int] = mapped_column(SmallInteger, server_default="1")
    number: Mapped[int] = mapped_column(SmallInteger)
    name: Mapped[str | None] = mapped_column(Text)
    air_date: Mapped[datetime.datetime | None]
    runtime_min: Mapped[int | None] = mapped_column(SmallInteger)
    rank: Mapped[int] = mapped_column(
        Integer, Computed("season::int * 100000 + number::int", persisted=True)
    )
