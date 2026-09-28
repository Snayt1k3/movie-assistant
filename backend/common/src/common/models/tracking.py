import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, SmallInteger, func, text
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base, UpdatedAtMixin
from common.models.enums import LibraryStatus, library_status_enum


class UserTitle(UpdatedAtMixin, Base):
    """Запись в библиотеке пользователя."""

    __tablename__ = "user_titles"
    __table_args__ = (
        CheckConstraint("rating between 1 and 10", name="rating_range"),
        Index("ix_user_titles_status", "user_id", "status", text("updated_at desc")),
        Index(
            "ix_user_titles_watching",
            "title_id",
            postgresql_where=text("status in ('watching', 'planned')"),
        ),
        Index(
            "ix_user_titles_rated",
            "title_id",
            "rating",
            postgresql_where=text("rating is not null"),
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    title_id: Mapped[int] = mapped_column(
        ForeignKey("titles.id", ondelete="CASCADE"), primary_key=True
    )
    status: Mapped[LibraryStatus] = mapped_column(library_status_enum)
    rating: Mapped[int | None] = mapped_column(SmallInteger)
    is_favorite: Mapped[bool] = mapped_column(server_default=text("false"))
    progress_rank: Mapped[int] = mapped_column(server_default="0")
    episodes_watched: Mapped[int] = mapped_column(SmallInteger, server_default="0")
    rewatch_count: Mapped[int] = mapped_column(SmallInteger, server_default="0")
    started_at: Mapped[datetime.datetime | None]
    finished_at: Mapped[datetime.datetime | None]


class UserEpisode(Base):
    """Факт просмотра серии."""

    __tablename__ = "user_episodes"
    __table_args__ = (
        Index("ix_user_episodes_user_title", "user_id", "title_id"),
        Index("ix_user_episodes_user_watched", "user_id", text("watched_at desc")),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    episode_id: Mapped[int] = mapped_column(
        ForeignKey("episodes.id", ondelete="CASCADE"), primary_key=True
    )
    title_id: Mapped[int] = mapped_column(ForeignKey("titles.id", ondelete="CASCADE"))
    watched_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
