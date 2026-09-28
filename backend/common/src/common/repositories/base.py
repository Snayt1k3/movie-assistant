from typing import Any

from sqlalchemy import ColumnElement, Delete, Select, Update, delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.interfaces import AbstractRepository
from common.models import Base


class SQLAlchemyRepository[ModelT: Base](AbstractRepository[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, **values: Any) -> ModelT:
        stmt = insert(self.model).values(**values).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def add_many(self, objs: list[dict]) -> list[ModelT]:
        if not objs:
            return []
        stmt = insert(self.model).values(objs).returning(self.model)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def find_one(self, **filters: Any) -> ModelT | None:
        stmt = self._filter(select(self.model), filters)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def find_many(self, **filters: Any) -> list[ModelT]:
        stmt = self._filter(select(self.model), filters)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def find_all(self) -> list[ModelT]:
        res = await self.session.execute(select(self.model))
        return list(res.scalars().all())

    async def update_one(self, id: int, **values: Any) -> ModelT:
        stmt = update(self.model).where(self.model.id == id).values(**values).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def update_many(self, filters: dict, **values: Any) -> list[ModelT]:
        stmt = self._filter(update(self.model), filters).values(**values).returning(self.model)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def delete_one(self, id: int) -> int | None:
        stmt = delete(self.model).where(self.model.id == id).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def delete_many(self, **filters: Any) -> int:
        stmt = self._filter(delete(self.model), filters)
        res = await self.session.execute(stmt)
        return res.rowcount

    def _filter[StmtT: Select | Update | Delete](
        self, stmt: StmtT, filters: dict[str, Any]
    ) -> StmtT:
        return stmt.where(*(self._condition(key, value) for key, value in filters.items()))

    def _condition(self, key: str, value: Any) -> ColumnElement[bool]:
        if key.endswith("__icontains"):
            field = getattr(self.model, key.removesuffix("__icontains"))
            return field.ilike(f"%{value}%")
        if key.endswith("__in"):
            field = getattr(self.model, key.removesuffix("__in"))
            return field.in_(value)
        return getattr(self.model, key) == value
