from common.models import ProviderAccount, RefreshToken, User
from common.repositories.base import SQLAlchemyRepository


class UserRepo(SQLAlchemyRepository[User]):
    model = User


class RefreshTokenRepo(SQLAlchemyRepository[RefreshToken]):
    model = RefreshToken


class ProviderAccountRepo(SQLAlchemyRepository[ProviderAccount]):
    model = ProviderAccount
