from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from common.models import Episode, Title, TitleExternalId
from common.repositories.base import SQLAlchemyRepository

UPSERT_CHUNK = 1000


class TitleRepo(SQLAlchemyRepository[Title]):
    model = Title


class TitleExternalIdRepo(SQLAlchemyRepository[TitleExternalId]):
    model = TitleExternalId

    async def find_title_ids(self, provider: str, external_ids: list[str]) -> dict[str, int]:
        """Вернуть {external_id: title_id} для уже известных внешних идентификаторов."""
        stmt = select(self.model.external_id, self.model.title_id).where(
            self.model.provider == provider,
            self.model.external_id.in_(external_ids),
        )
        res = await self.session.execute(stmt)
        return dict(res.tuples().all())

    async def list_external_ids(self, provider: str, prefix: str = "") -> list[str]:
        stmt = select(self.model.external_id).where(
            self.model.provider == provider,
            self.model.external_id.startswith(prefix),
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def add_many_ignore_conflicts(self, objs: list[dict]) -> None:
        """Добавить связки, пропуская уже занятые (provider, external_id)."""
        if objs:
            await self.session.execute(insert(self.model).values(objs).on_conflict_do_nothing())


class EpisodeRepo(SQLAlchemyRepository[Episode]):
    model = Episode

    async def upsert_many(self, objs: list[dict]) -> None:
        """Создать серии или обновить существующие по (title_id, season, number)."""
        # одна серия дважды в одном insert ломает on conflict, оставляем последнюю
        unique = {(o["title_id"], o["season"], o["number"]): o for o in objs}
        rows = list(unique.values())
        # у ежедневных шоу тысячи серий, а asyncpg держит максимум 32767 параметров
        for i in range(0, len(rows), UPSERT_CHUNK):
            stmt = insert(self.model).values(rows[i : i + UPSERT_CHUNK])
            stmt = stmt.on_conflict_do_update(
                index_elements=["title_id", "season", "number"],
                set_={
                    "name": stmt.excluded.name,
                    "air_date": stmt.excluded.air_date,
                    "runtime_min": stmt.excluded.runtime_min,
                },
            )
            await self.session.execute(stmt)
