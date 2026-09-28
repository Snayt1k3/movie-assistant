import datetime

from sqlalchemy import BigInteger, ForeignKey, Index, LargeBinary, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import CITEXT, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base, CreatedAtMixin, IdMixin
from common.models.enums import Visibility, visibility_enum


class User(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "users"

    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)
    username: Mapped[str | None] = mapped_column(CITEXT, unique=True)
    display_name: Mapped[str] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    locale: Mapped[str] = mapped_column(Text, server_default="ru")
    timezone: Mapped[str] = mapped_column(Text, server_default="Europe/Moscow")
    profile_visibility: Mapped[Visibility] = mapped_column(
        visibility_enum, server_default=Visibility.public
    )
    is_pro: Mapped[bool] = mapped_column(server_default=text("false"))
    settings: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    deleted_at: Mapped[datetime.datetime | None]


class RefreshToken(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index(
            "ix_refresh_tokens_active_user_id",
            "user_id",
            postgresql_where=text("revoked_at is null"),
        ),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[bytes] = mapped_column(LargeBinary, unique=True)
    user_agent: Mapped[str | None] = mapped_column(Text)
    expires_at: Mapped[datetime.datetime]
    revoked_at: Mapped[datetime.datetime | None]


class ProviderAccount(Base):
    """Связка с внешним аккаунтом: Shikimori OAuth и подобные."""

    __tablename__ = "provider_accounts"
    __table_args__ = (UniqueConstraint("provider", "external_id"),)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    provider: Mapped[str] = mapped_column(Text, primary_key=True)
    external_id: Mapped[str] = mapped_column(Text)
    access_token: Mapped[bytes | None] = mapped_column(LargeBinary)
    refresh_token: Mapped[bytes | None] = mapped_column(LargeBinary)
    expires_at: Mapped[datetime.datetime | None]
