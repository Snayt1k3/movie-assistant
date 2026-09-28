import datetime

from sqlalchemy import ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from common.models.base import Base, CreatedAtMixin, IdMixin


class ImportJob(IdMixin, CreatedAtMixin, Base):
    __tablename__ = "import_jobs"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    source: Mapped[str] = mapped_column(Text)  # kinopoisk | letterboxd | shikimori | trakt
    # pending | parsing | matching | review | applying | done | failed
    status: Mapped[str] = mapped_column(Text)
    file_key: Mapped[str | None] = mapped_column(Text)
    stats: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))
    error: Mapped[str | None] = mapped_column(Text)
    finished_at: Mapped[datetime.datetime | None]


class ImportItem(IdMixin, Base):
    __tablename__ = "import_items"
    __table_args__ = (Index("ix_import_items_job_state", "job_id", "match_state"),)

    job_id: Mapped[int] = mapped_column(ForeignKey("import_jobs.id", ondelete="CASCADE"))
    raw: Mapped[dict] = mapped_column(JSONB)
    title_id: Mapped[int | None] = mapped_column(ForeignKey("titles.id", ondelete="SET NULL"))
    match_score: Mapped[float | None]
    match_state: Mapped[str] = mapped_column(Text)  # matched | ambiguous | not_found | skipped
    applied: Mapped[bool] = mapped_column(server_default=text("false"))
