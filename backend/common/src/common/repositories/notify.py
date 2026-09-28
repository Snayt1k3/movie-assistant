from common.models import Notification
from common.repositories.base import SQLAlchemyRepository


class NotificationRepo(SQLAlchemyRepository[Notification]):
    model = Notification
