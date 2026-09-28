import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    SmallInteger,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base, CreatedAtMixin, IdMixin, UpdatedAtMixin
from common.models.enums import Visibility, visibility_enum


class Follow(CreatedAtMixin, Base):
    __tablename__ = "follows"
    __table_args__ = (
        CheckConstraint("follower_id <> followee_id", name="not_self"),
        Index("ix_follows_followee", "followee_id"),
    )

    follower_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    followee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )


class Review(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating between 1 and 10", name="rating_range"),
        Index(
            "uq_reviews_one_per_title",
            "user_id",
            "title_id",
            unique=True,
            postgresql_where=text("deleted_at is null"),
        ),
        Index(
            "ix_reviews_title",
            "title_id",
            text("created_at desc"),
            postgresql_where=text("deleted_at is null"),
        ),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title_id: Mapped[int] = mapped_column(ForeignKey("titles.id", ondelete="CASCADE"))
    body: Mapped[str] = mapped_column(Text)
    rating: Mapped[int | None] = mapped_column(SmallInteger)
    spoiler_rank: Mapped[int] = mapped_column(server_default="0")
    visibility: Mapped[Visibility] = mapped_column(
        visibility_enum, server_default=Visibility.public
    )
    likes_count: Mapped[int] = mapped_column(server_default="0")
    comments_count: Mapped[int] = mapped_column(server_default="0")
    edited_at: Mapped[datetime.datetime | None]
    deleted_at: Mapped[datetime.datetime | None]


class Comment(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "comments"
    __table_args__ = (
        Index(
            "ix_comments_subject",
            "subject_type",
            "subject_id",
            "created_at",
            postgresql_where=text("deleted_at is null"),
        ),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    subject_type: Mapped[str] = mapped_column(Text)  # title | review | episode
    subject_id: Mapped[int] = mapped_column(BigInteger)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"))
    title_id: Mapped[int | None] = mapped_column(ForeignKey("titles.id", ondelete="CASCADE"))
    body: Mapped[str] = mapped_column(Text)
    spoiler_rank: Mapped[int] = mapped_column(server_default="0")
    likes_count: Mapped[int] = mapped_column(server_default="0")
    deleted_at: Mapped[datetime.datetime | None]


class Reaction(CreatedAtMixin, Base):
    __tablename__ = "reactions"
    __table_args__ = (Index("ix_reactions_subject", "subject_type", "subject_id"),)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    subject_type: Mapped[str] = mapped_column(
        Text, primary_key=True
    )  # review | comment | collection
    subject_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    kind: Mapped[str] = mapped_column(Text, primary_key=True, server_default="like")


class Collection(IdMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "collections"
    __table_args__ = (Index("ix_collections_owner", "owner_id", text("updated_at desc")),)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    visibility: Mapped[Visibility] = mapped_column(
        visibility_enum, server_default=Visibility.public
    )
    items_count: Mapped[int] = mapped_column(SmallInteger, server_default="0")
    deleted_at: Mapped[datetime.datetime | None]


class CollectionItem(Base):
    __tablename__ = "collection_items"
    __table_args__ = (Index("ix_collection_items_position", "collection_id", "position"),)

    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True
    )
    title_id: Mapped[int] = mapped_column(
        ForeignKey("titles.id", ondelete="CASCADE"), primary_key=True
    )
    position: Mapped[int]
    note: Mapped[str | None] = mapped_column(Text)
    added_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())


class ActivityEvent(Base):
    """Событие ленты. Таблица партиционирована по месяцам, партиции создаёт cron."""

    __tablename__ = "activity_events"
    __table_args__ = (
        PrimaryKeyConstraint("id", "created_at"),
        Index(
            "ix_activity_events_actor",
            "actor_id",
            text("created_at desc"),
            postgresql_where=text("hidden_at is null"),
        ),
        {"postgresql_partition_by": "RANGE (created_at)"},
    )

    id: Mapped[int] = mapped_column(BigInteger, autoincrement=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    # rated | reviewed | watched_episode | completed | added_to_list | created_collection | followed
    type: Mapped[str] = mapped_column(Text)
    title_id: Mapped[int | None] = mapped_column(ForeignKey("titles.id", ondelete="CASCADE"))
    subject_id: Mapped[int | None] = mapped_column(BigInteger)
    payload: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    spoiler_rank: Mapped[int] = mapped_column(server_default="0")
    visibility: Mapped[Visibility] = mapped_column(
        visibility_enum, server_default=Visibility.public
    )
    hidden_at: Mapped[datetime.datetime | None]
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
