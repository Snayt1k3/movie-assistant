from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from common.interfaces import AbstractUow
from common.repositories import catalog, identity, importer, notify, social, tracking


class SqlAlchemyUnitOfWork(AbstractUow):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def __aenter__(self) -> Self:
        self.session = self.session_factory()

        self.users = identity.UserRepo(self.session)
        self.refresh_tokens = identity.RefreshTokenRepo(self.session)
        self.provider_accounts = identity.ProviderAccountRepo(self.session)

        self.titles = catalog.TitleRepo(self.session)
        self.title_external_ids = catalog.TitleExternalIdRepo(self.session)
        self.episodes = catalog.EpisodeRepo(self.session)

        self.user_titles = tracking.UserTitleRepo(self.session)
        self.user_episodes = tracking.UserEpisodeRepo(self.session)

        self.follows = social.FollowRepo(self.session)
        self.reviews = social.ReviewRepo(self.session)
        self.comments = social.CommentRepo(self.session)
        self.reactions = social.ReactionRepo(self.session)
        self.collections = social.CollectionRepo(self.session)
        self.collection_items = social.CollectionItemRepo(self.session)
        self.activity_events = social.ActivityEventRepo(self.session)

        self.notifications = notify.NotificationRepo(self.session)

        self.import_jobs = importer.ImportJobRepo(self.session)
        self.import_items = importer.ImportItemRepo(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        finally:
            await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
