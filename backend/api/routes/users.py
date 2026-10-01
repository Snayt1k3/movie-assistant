from deps import CurrentUser
from fastapi import APIRouter
from schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)
