import abc
from typing import Self

from common.interfaces.repository import AbstractRepository


class AbstractUow(abc.ABC):
    # identity
    users: AbstractRepository
    refresh_tokens: AbstractRepository
    provider_accounts: AbstractRepository
    # catalog
    titles: AbstractRepository
    title_external_ids: AbstractRepository
    episodes: AbstractRepository
    # tracking
    user_titles: AbstractRepository
    user_episodes: AbstractRepository
    # social
    follows: AbstractRepository
    reviews: AbstractRepository
    comments: AbstractRepository
    reactions: AbstractRepository
    collections: AbstractRepository
    collection_items: AbstractRepository
    activity_events: AbstractRepository
    # notify
    notifications: AbstractRepository
    # importer
    import_jobs: AbstractRepository
    import_items: AbstractRepository

    @abc.abstractmethod
    async def __aenter__(self) -> Self:
        raise NotImplementedError

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
