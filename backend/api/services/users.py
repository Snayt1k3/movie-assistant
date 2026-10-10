from collections.abc import Callable
from dataclasses import dataclass

from exceptions import (
    CannotFollowSelfError,
    ProfileHiddenError,
    UsernameTakenError,
    UserNotFoundError,
)
from schemas.library import LibraryItemOut, LibraryParams, TitleShort
from schemas.pagination import Page, PageParams
from schemas.user import ProfileOut, ProfileStats, UserShort
from sqlalchemy.exc import IntegrityError

from common.interfaces import AbstractUow
from common.models import User
from common.models.enums import LibraryStatus, Visibility


@dataclass(frozen=True, slots=True)
class Relation:
    """Кем зритель приходится владельцу профиля."""

    is_me: bool = False
    is_following: bool = False
    follows_you: bool = False

    @property
    def audience(self) -> list[Visibility]:
        """Уровни видимости, которые этому зрителю открыты."""
        if self.is_me:
            return list(Visibility)

        if self.is_following:
            return [Visibility.public, Visibility.followers]

        return [Visibility.public]


class UserService:
    def __init__(self, uow: Callable[[], AbstractUow]):
        self.uow = uow

    async def update_me(self, user: User, values: dict) -> User:
        if not values:
            return user

        async with self.uow() as uow:
            username = values.get("username")
            if username is not None:
                owner = await uow.users.find_one(username=username)
                if owner is not None and owner.id != user.id:
                    raise UsernameTakenError

            try:
                return await uow.users.update_one(user.id, **values)
            except IntegrityError as e:
                raise UsernameTakenError from e

    async def get_profile(self, ref: str, viewer: User | None) -> ProfileOut:
        async with self.uow() as uow:
            owner = await self._resolve(uow, ref)
            relation = await self._relation(uow, owner, viewer)

            stats = None
            if owner.profile_visibility in relation.audience:
                stats = await self._stats(uow, owner.id, relation.audience)

        return ProfileOut(
            id=owner.id,
            username=owner.username,
            display_name=owner.display_name,
            avatar_url=owner.avatar_url,
            profile_visibility=owner.profile_visibility,
            is_pro=owner.is_pro,
            created_at=owner.created_at,
            is_me=relation.is_me,
            is_following=relation.is_following,
            follows_you=relation.follows_you,
            stats=stats,
        )

    async def library(
        self, ref: str, viewer: User | None, params: LibraryParams
    ) -> Page[LibraryItemOut]:
        async with self.uow() as uow:
            owner = await self._visible_owner(uow, ref, viewer)
            rows = await uow.user_titles.list_with_titles(
                owner.id,
                status=params.status,
                favorite=params.favorite,
                limit=params.limit + 1,
                offset=params.offset,
            )

        items = [
            LibraryItemOut(
                title=TitleShort.model_validate(title),
                status=entry.status,
                rating=entry.rating,
                is_favorite=entry.is_favorite,
                episodes_watched=entry.episodes_watched,
                rewatch_count=entry.rewatch_count,
                started_at=entry.started_at,
                finished_at=entry.finished_at,
                updated_at=entry.updated_at,
            )
            for entry, title in rows[: params.limit]
        ]

        return Page(items=items, has_more=len(rows) > params.limit)

    async def followers(self, ref: str, viewer: User | None, params: PageParams) -> Page[UserShort]:
        async with self.uow() as uow:
            owner = await self._visible_owner(uow, ref, viewer)
            users = await uow.follows.list_followers(
                owner.id, limit=params.limit + 1, offset=params.offset
            )

        return self._users_page(users, params.limit)

    async def following(self, ref: str, viewer: User | None, params: PageParams) -> Page[UserShort]:
        async with self.uow() as uow:
            owner = await self._visible_owner(uow, ref, viewer)
            users = await uow.follows.list_following(
                owner.id, limit=params.limit + 1, offset=params.offset
            )

        return self._users_page(users, params.limit)

    async def follow(self, follower: User, ref: str) -> None:
        async with self.uow() as uow:
            followee = await self._resolve(uow, ref)
            if followee.id == follower.id:
                raise CannotFollowSelfError

            await uow.follows.add_ignore_conflict(follower.id, followee.id)

    async def unfollow(self, follower: User, ref: str) -> None:
        async with self.uow() as uow:
            followee = await self._resolve(uow, ref)
            await uow.follows.delete_many(follower_id=follower.id, followee_id=followee.id)

    async def _resolve(self, uow: AbstractUow, ref: str) -> User:
        """Пользователь по числовому id или username."""
        filters = {"id": int(ref)} if ref.isdecimal() else {"username": ref}
        user = await uow.users.find_one(**filters)

        if user is None or user.deleted_at:
            raise UserNotFoundError

        return user

    async def _visible_owner(self, uow: AbstractUow, ref: str, viewer: User | None) -> User:
        owner = await self._resolve(uow, ref)
        relation = await self._relation(uow, owner, viewer)

        if owner.profile_visibility not in relation.audience:
            raise ProfileHiddenError

        return owner

    async def _relation(self, uow: AbstractUow, owner: User, viewer: User | None) -> Relation:
        if viewer is None:
            return Relation()

        if viewer.id == owner.id:
            return Relation(is_me=True)

        edges = await uow.follows.find_many(
            follower_id__in=[viewer.id, owner.id], followee_id__in=[viewer.id, owner.id]
        )
        pairs = {(edge.follower_id, edge.followee_id) for edge in edges}

        return Relation(
            is_following=(viewer.id, owner.id) in pairs,
            follows_you=(owner.id, viewer.id) in pairs,
        )

    async def _stats(
        self, uow: AbstractUow, user_id: int, audience: list[Visibility]
    ) -> ProfileStats:
        library = await uow.user_titles.stats(user_id)
        followers, following = await uow.follows.counts(user_id)
        episodes_watched = await uow.user_episodes.count(user_id=user_id)
        reviews = await uow.reviews.count(user_id=user_id, deleted_at=None, visibility__in=audience)
        collections = await uow.collections.count(
            owner_id=user_id, deleted_at=None, visibility__in=audience
        )

        return ProfileStats(
            library={status: library.by_status.get(status, 0) for status in LibraryStatus},
            favorites=library.favorites,
            rated=library.rated,
            avg_rating=library.avg_rating,
            episodes_watched=episodes_watched,
            followers=followers,
            following=following,
            reviews=reviews,
            collections=collections,
        )

    @staticmethod
    def _users_page(users: list[User], limit: int) -> Page[UserShort]:
        return Page(
            items=[UserShort.model_validate(user) for user in users[:limit]],
            has_more=len(users) > limit,
        )
