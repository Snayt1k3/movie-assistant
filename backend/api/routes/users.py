from typing import Annotated

from deps import CurrentUser, OptionalUser, UserServiceDep
from exceptions import (
    CannotFollowSelfError,
    ProfileHiddenError,
    UsernameTakenError,
    UserNotFoundError,
)
from fastapi import APIRouter, HTTPException, Query, status
from schemas.library import LibraryItemOut, LibraryParams
from schemas.pagination import Page, PageParams
from schemas.user import ProfileOut, UserOut, UserRef, UserShort, UserUpdateIn

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)


@router.patch("/me")
async def update_me(body: UserUpdateIn, user: CurrentUser, users: UserServiceDep) -> UserOut:
    try:
        updated = await users.update_me(user, body.model_dump(mode="json", exclude_unset=True))
    except UsernameTakenError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken") from e
    return UserOut.model_validate(updated)


@router.get("/{user_ref}")
async def profile(user_ref: UserRef, viewer: OptionalUser, users: UserServiceDep) -> ProfileOut:
    try:
        return await users.get_profile(user_ref, viewer)
    except UserNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found") from e


@router.get("/{user_ref}/library")
async def library(
    user_ref: UserRef,
    params: Annotated[LibraryParams, Query()],
    viewer: OptionalUser,
    users: UserServiceDep,
) -> Page[LibraryItemOut]:
    try:
        return await users.library(user_ref, viewer, params)
    except UserNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found") from e
    except ProfileHiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Profile is hidden") from e


@router.get("/{user_ref}/followers")
async def followers(
    user_ref: UserRef,
    params: Annotated[PageParams, Query()],
    viewer: OptionalUser,
    users: UserServiceDep,
) -> Page[UserShort]:
    try:
        return await users.followers(user_ref, viewer, params)
    except UserNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found") from e
    except ProfileHiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Profile is hidden") from e


@router.get("/{user_ref}/following")
async def following(
    user_ref: UserRef,
    params: Annotated[PageParams, Query()],
    viewer: OptionalUser,
    users: UserServiceDep,
) -> Page[UserShort]:
    try:
        return await users.following(user_ref, viewer, params)
    except UserNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found") from e
    except ProfileHiddenError as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Profile is hidden") from e


@router.put("/{user_ref}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def follow(user_ref: UserRef, user: CurrentUser, users: UserServiceDep) -> None:
    try:
        await users.follow(user, user_ref)
    except UserNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found") from e
    except CannotFollowSelfError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot follow yourself") from e


@router.delete("/{user_ref}/follow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow(user_ref: UserRef, user: CurrentUser, users: UserServiceDep) -> None:
    try:
        await users.unfollow(user, user_ref)
    except UserNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found") from e
