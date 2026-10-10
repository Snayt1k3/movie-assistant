from typing import Annotated

from fastapi import Depends
from services.users import UserService

from common.db import session_factory
from common.uow import SqlAlchemyUnitOfWork

_user_service = UserService(lambda: SqlAlchemyUnitOfWork(session_factory))


def get_user_service() -> UserService:
    return _user_service


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
