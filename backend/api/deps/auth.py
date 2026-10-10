from typing import Annotated

from config import settings
from exceptions import AuthError
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from services.auth import AuthService
from utils.http import unauthorized

from common.db import session_factory
from common.models import User
from common.uow import SqlAlchemyUnitOfWork

_bearer = HTTPBearer(auto_error=False)
_auth_service = AuthService(lambda: SqlAlchemyUnitOfWork(session_factory), settings)


def get_auth_service() -> AuthService:
    return _auth_service


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> User | None:
    """Пользователь, если токен передан. Битый токен всё равно 401, а не аноним."""
    if credentials is None:
        return None
    try:
        return await auth.authenticate(credentials.credentials)
    except AuthError as e:
        raise unauthorized() from e


async def get_current_user(
    user: Annotated[User | None, Depends(get_optional_user)],
) -> User:
    if user is None:
        raise unauthorized()
    return user


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
