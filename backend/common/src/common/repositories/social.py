from common.models import (
    ActivityEvent,
    Collection,
    CollectionItem,
    Comment,
    Follow,
    Reaction,
    Review,
)
from common.repositories.base import SQLAlchemyRepository


class FollowRepo(SQLAlchemyRepository[Follow]):
    model = Follow


class ReviewRepo(SQLAlchemyRepository[Review]):
    model = Review


class CommentRepo(SQLAlchemyRepository[Comment]):
    model = Comment


class ReactionRepo(SQLAlchemyRepository[Reaction]):
    model = Reaction


class CollectionRepo(SQLAlchemyRepository[Collection]):
    model = Collection


class CollectionItemRepo(SQLAlchemyRepository[CollectionItem]):
    model = CollectionItem


class ActivityEventRepo(SQLAlchemyRepository[ActivityEvent]):
    model = ActivityEvent
