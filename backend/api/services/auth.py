import datetime
from collections.abc import Callable

from config import Settings
from exceptions import AuthError, EmailTaken, InvalidAccessToken
from schemas.auth import TelegramLoginIn, TokenPair
from sqlalchemy.exc import IntegrityError
from utils import security
from utils.telegram import verify_login_widget

from common.interfaces import AbstractUow
from common.models import User


class AuthService:
    def __init__(self, uow_factory: Callable[[], AbstractUow], settings: Settings):
        self.uow_factory = uow_factory
        self.settings = settings
        # сверяем пароль и для несуществующего email, чтобы по времени ответа
        # нельзя было узнать, зарегистрирован ли адрес
        self._dummy_hash = security.hash_password("dummy-password")

    async def register(
        self, email: str, password: str, display_name: str, user_agent: str | None
    ) -> TokenPair:
        async with self.uow_factory() as uow:
            if await uow.users.find_one(email=email):
                raise EmailTaken
            try:
                user = await uow.users.add_one(
                    email=email,
                    password_hash=security.hash_password(password),
                    display_name=display_name,
                )
            except IntegrityError as e:
                raise EmailTaken from e
            return await self._issue_tokens(uow, user.id, user_agent)

    async def login(self, email: str, password: str, user_agent: str | None) -> TokenPair:
        async with self.uow_factory() as uow:
            user = await uow.users.find_one(email=email)
            password_hash = user.password_hash if user and user.password_hash else self._dummy_hash
            password_ok = security.verify_password(password, password_hash)
            if not user or not user.password_hash or not password_ok or user.deleted_at:
                raise AuthError
            return await self._issue_tokens(uow, user.id, user_agent)

    async def telegram_login(self, data: TelegramLoginIn, user_agent: str | None) -> TokenPair:
        """Войти через Telegram Login Widget, при первом входе завести пользователя."""
        if not verify_login_widget(data.model_dump(), self.settings.bot_token):
            raise AuthError
        signed_at = datetime.datetime.fromtimestamp(data.auth_date, datetime.UTC)
        if datetime.datetime.now(datetime.UTC) - signed_at > self.settings.telegram_auth_max_age:
            raise AuthError

        async with self.uow_factory() as uow:
            user = await uow.users.find_one(telegram_id=data.id)
            if user is None:
                display_name = " ".join(filter(None, [data.first_name, data.last_name]))
                user = await uow.users.add_one(
                    telegram_id=data.id, display_name=display_name, avatar_url=data.photo_url
                )
            elif user.deleted_at:
                raise AuthError
            return await self._issue_tokens(uow, user.id, user_agent)

    async def refresh(self, refresh_token: str, user_agent: str | None) -> TokenPair:
        """
        Обменять refresh-токен на новую пару, старый отзывается.

        Повторное предъявление отозванного токена значит, что его украли: тогда отзываем
        все сессии пользователя, и вору, и владельцу придётся войти заново.
        """
        token_hash = security.hash_refresh_token(refresh_token)
        now = datetime.datetime.now(datetime.UTC)
        async with self.uow_factory() as uow:
            # отзываем одним UPDATE, чтобы два параллельных refresh не получили по паре
            claimed = await uow.refresh_tokens.update_many(
                {"token_hash": token_hash, "revoked_at": None}, revoked_at=now
            )
            if not claimed:
                stored = await uow.refresh_tokens.find_one(token_hash=token_hash)
                if stored is not None:
                    await self._revoke_all(uow, stored.user_id, now)
                    await uow.commit()
                raise AuthError

            token = claimed[0]
            user: User | None = await uow.users.find_one(id=token.user_id)
            if token.expires_at <= now or user is None or user.deleted_at:
                raise AuthError
            return await self._issue_tokens(uow, user.id, user_agent)

    async def logout(self, refresh_token: str) -> None:
        async with self.uow_factory() as uow:
            await uow.refresh_tokens.update_many(
                {"token_hash": security.hash_refresh_token(refresh_token), "revoked_at": None},
                revoked_at=datetime.datetime.now(datetime.UTC),
            )

    async def authenticate(self, access_token: str) -> User:
        """Пользователь по access-токену из заголовка Authorization."""
        try:
            user_id = security.decode_access_token(
                access_token, self.settings.jwt_secret, self.settings.jwt_algorithm
            )
        except InvalidAccessToken as e:
            raise AuthError from e
        async with self.uow_factory() as uow:
            user = await uow.users.find_one(id=user_id)
        if user is None or user.deleted_at:
            raise AuthError
        return user

    async def _issue_tokens(
        self, uow: AbstractUow, user_id: int, user_agent: str | None
    ) -> TokenPair:
        refresh_token = security.new_refresh_token()
        await uow.refresh_tokens.add_one(
            user_id=user_id,
            token_hash=security.hash_refresh_token(refresh_token),
            user_agent=user_agent,
            expires_at=datetime.datetime.now(datetime.UTC) + self.settings.refresh_token_ttl,
        )
        access_token = security.create_access_token(
            user_id,
            self.settings.jwt_secret,
            self.settings.jwt_algorithm,
            self.settings.access_token_ttl,
        )
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(self.settings.access_token_ttl.total_seconds()),
        )

    async def _revoke_all(self, uow: AbstractUow, user_id: int, now: datetime.datetime) -> None:
        await uow.refresh_tokens.update_many(
            {"user_id": user_id, "revoked_at": None}, revoked_at=now
        )
