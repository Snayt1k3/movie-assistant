import datetime

from sqlalchemy import ForeignKey, Index, SmallInteger, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base, CreatedAtMixin, IdMixin


class Notification(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_due", "scheduled_at", postgresql_where=text("sent_at is null")),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    kind: Mapped[str] = mapped_column(Text)  # episode_release | friend_review | digest
    payload: Mapped[dict] = mapped_column(JSONB)
    dedup_key: Mapped[str] = mapped_column(Text, unique=True)
    scheduled_at: Mapped[datetime.datetime]
    sent_at: Mapped[datetime.datetime | None]
    failed_attempts: Mapped[int] = mapped_column(SmallInteger, server_default="0")
    last_error: Mapped[str | None] = mapped_column(Text)
