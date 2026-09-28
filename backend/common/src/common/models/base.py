import datetime
from typing import ClassVar

from sqlalchemy import BigInteger, DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    type_annotation_map: ClassVar[dict] = {
        datetime.datetime: DateTime(timezone=True),
    }


class IdMixin:
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)


class CreatedAtMixin:
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())


class UpdatedAtMixin:
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
