from dataclasses import dataclass

from sqlalchemy import func, select

from common.models import Title, UserEpisode, UserTitle
from common.models.enums import LibraryStatus
from common.repositories.base import SQLAlchemyRepository


@dataclass(frozen=True, slots=True)
class LibraryStats:
    by_status: dict[LibraryStatus, int]
    favorites: int
    rated: int
    avg_rating: float | None


class UserTitleRepo(SQLAlchemyRepository[UserTitle]):
    model = UserTitle

    async def stats(self, user_id: int) -> LibraryStats:
        """Сводка по библиотеке пользователя для профиля."""
        by_status = await self.session.execute(
            select(self.model.status, func.count())
            .where(self.model.user_id == user_id)
            .group_by(self.model.status)
        )
        totals = await self.session.execute(
            select(
                func.count().filter(self.model.is_favorite),
                func.count(self.model.rating),
                func.avg(self.model.rating),
            ).where(self.model.user_id == user_id)
        )
        favorites, rated, avg_rating = totals.one()
        return LibraryStats(
            by_status=dict(by_status.tuples().all()),
            favorites=favorites,
            rated=rated,
            avg_rating=round(float(avg_rating), 2) if avg_rating is not None else None,
        )

    async def list_with_titles(
        self,
        user_id: int,
        *,
        status: LibraryStatus | None = None,
        favorite: bool | None = None,
        limit: int,
        offset: int,
    ) -> list[tuple[UserTitle, Title]]:
        """Записи библиотеки вместе с тайтлами, свежие изменения первыми."""
        stmt = (
            select(self.model, Title)
            .join(Title, Title.id == self.model.title_id)
            .where(self.model.user_id == user_id)
            .order_by(self.model.updated_at.desc(), self.model.title_id.desc())
            .limit(limit)
            .offset(offset)
        )
        if status is not None:
            stmt = stmt.where(self.model.status == status)
        if favorite is not None:
            stmt = stmt.where(self.model.is_favorite == favorite)
        res = await self.session.execute(stmt)
        return list(res.tuples().all())


class UserEpisodeRepo(SQLAlchemyRepository[UserEpisode]):
    model = UserEpisode
