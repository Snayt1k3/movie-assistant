from common.models import ImportItem, ImportJob
from common.repositories.base import SQLAlchemyRepository


class ImportJobRepo(SQLAlchemyRepository[ImportJob]):
    model = ImportJob


class ImportItemRepo(SQLAlchemyRepository[ImportItem]):
    model = ImportItem
