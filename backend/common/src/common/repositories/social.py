from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import InstrumentedAttribute

from common.models import (
    ActivityEvent,
    Collection,
    CollectionItem,
    Comment,
    Follow,
    Reaction,
    Review,
    User,
)
from common.repositories.base import SQLAlchemyRepository


class FollowRepo(SQLAlchemyRepository[Follow]):
    model = Follow

    async def add_ignore_conflict(self, follower_id: int, followee_id: int) -> None:
        """Подписаться; повторная подписка ничего не меняет."""
        stmt = insert(self.model).values(follower_id=follower_id, followee_id=followee_id)
        await self.session.execute(stmt.on_conflict_do_nothing())

    async def counts(self, user_id: int) -> tuple[int, int]:
        """Число подписчиков и подписок без удалённых аккаунтов."""
        followers = await self._count_users(self.model.follower_id, self.model.followee_id, user_id)
        following = await self._count_users(self.model.followee_id, self.model.follower_id, user_id)
        return followers, following

    async def list_followers(self, user_id: int, *, limit: int, offset: int) -> list[User]:
        return await self._list_users(
            self.model.follower_id, self.model.followee_id, user_id, limit, offset
        )

    async def list_following(self, user_id: int, *, limit: int, offset: int) -> list[User]:
        return await self._list_users(
            self.model.followee_id, self.model.follower_id, user_id, limit, offset
        )

    async def _count_users(
        self,
        other_col: InstrumentedAttribute[int],
        own_col: InstrumentedAttribute[int],
        user_id: int,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(self.model)
            .join(User, User.id == other_col)
            .where(own_col == user_id, User.deleted_at.is_(None))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def _list_users(
        self,
        other_col: InstrumentedAttribute[int],
        own_col: InstrumentedAttribute[int],
        user_id: int,
        limit: int,
        offset: int,
    ) -> list[User]:
        stmt = (
            select(User)
            .join(self.model, User.id == other_col)
            .where(own_col == user_id, User.deleted_at.is_(None))
            .order_by(self.model.created_at.desc(), User.id.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())


class ReviewRepo(SQLAlchemyRepository[Review]):
    model = Review


class CommentRepo(SQLAlchemyRepository[Comment]):
    model = Comment


class ReactionRepo(SQLAlchemyRepository[Reaction]):
    model = Reaction


class CollectionRepo(SQLAlchemyRepository[Collection]):
    model = Collection


class CollectionItemRepo(SQLAlchemyRepository[CollectionItem]):
    model = CollectionItem


class ActivityEventRepo(SQLAlchemyRepository[ActivityEvent]):
    model = ActivityEvent
