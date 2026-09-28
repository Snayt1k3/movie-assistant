from common.models import UserEpisode, UserTitle
from common.repositories.base import SQLAlchemyRepository


class UserTitleRepo(SQLAlchemyRepository[UserTitle]):
    model = UserTitle


class UserEpisodeRepo(SQLAlchemyRepository[UserEpisode]):
    model = UserEpisode
