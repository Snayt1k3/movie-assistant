from typing import Annotated

from deps import AuthServiceDep
from exceptions import AuthError, EmailTaken
from fastapi import APIRouter, Header, HTTPException, status
from schemas.auth import LoginIn, RefreshIn, RegisterIn, TelegramLoginIn, TokenPair
from utils.http import unauthorized

router = APIRouter(prefix="/auth", tags=["auth"])

UserAgent = Annotated[str | None, Header()]


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterIn, auth: AuthServiceDep, user_agent: UserAgent = None
) -> TokenPair:
    try:
        return await auth.register(body.email, body.password, body.display_name, user_agent)
    except EmailTaken as e:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered") from e


@router.post("/login")
async def login(body: LoginIn, auth: AuthServiceDep, user_agent: UserAgent = None) -> TokenPair:
    try:
        return await auth.login(body.email, body.password, user_agent)
    except AuthError as e:
        raise unauthorized("Invalid email or password") from e


@router.post("/telegram")
async def telegram_login(
    body: TelegramLoginIn, auth: AuthServiceDep, user_agent: UserAgent = None
) -> TokenPair:
    try:
        return await auth.telegram_login(body, user_agent)
    except AuthError as e:
        raise unauthorized("Invalid Telegram login data") from e


@router.post("/refresh")
async def refresh(body: RefreshIn, auth: AuthServiceDep, user_agent: UserAgent = None) -> TokenPair:
    try:
        return await auth.refresh(body.refresh_token, user_agent)
    except AuthError as e:
        raise unauthorized("Invalid refresh token") from e


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(body: RefreshIn, auth: AuthServiceDep) -> None:
    await auth.logout(body.refresh_token)
