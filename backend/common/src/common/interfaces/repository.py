from abc import ABC, abstractmethod
from typing import Any


class AbstractRepository[ModelT](ABC):
    @abstractmethod
    async def add_one(self, **values: Any) -> ModelT:
        """Добавить новую сущность в хранилище."""
        raise NotImplementedError

    @abstractmethod
    async def add_many(self, objs: list[dict]) -> list[ModelT]:
        """Добавить новые сущности в хранилище."""
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, **filters: Any) -> ModelT | None:
        """Найти одну сущность по фильтрам, см. find_many."""
        raise NotImplementedError

    @abstractmethod
    async def find_many(self, **filters: Any) -> list[ModelT]:
        """
        Отфильтровать сущности по заданным критериям.

        Поддерживаемые параметры фильтрации:
        - field=value: точное совпадение (например, status="ongoing")
        - field__icontains=value: частичное совпадение без учёта регистра
          (например, title_ru__icontains="наруто")
        - field__in=[v1, v2, ...]: значение поля входит в список (например, id__in=[1, 2, 3])
        """
        raise NotImplementedError

    @abstractmethod
    async def find_all(self) -> list[ModelT]:
        """Вернуть список всех сущностей."""
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, id: int, **values: Any) -> ModelT:
        """Обновить сущность по ID."""
        raise NotImplementedError

    @abstractmethod
    async def update_many(self, filters: dict, **values: Any) -> list[ModelT]:
        """Обновить все сущности, подходящие под фильтры."""
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, id: int) -> int | None:
        """Удалить сущность по ID."""
        raise NotImplementedError

    @abstractmethod
    async def delete_many(self, **filters: Any) -> int:
        """Удалить все сущности, подходящие под фильтры. Возвращает число удалённых."""
        raise NotImplementedError
