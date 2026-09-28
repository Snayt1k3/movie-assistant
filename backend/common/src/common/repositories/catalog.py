from common.models import Episode, Title, TitleExternalId
from common.repositories.base import SQLAlchemyRepository


class TitleRepo(SQLAlchemyRepository[Title]):
    model = Title


class TitleExternalIdRepo(SQLAlchemyRepository[TitleExternalId]):
    model = TitleExternalId


class EpisodeRepo(SQLAlchemyRepository[Episode]):
    model = Episode
