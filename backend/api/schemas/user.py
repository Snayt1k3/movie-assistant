from pydantic import BaseModel, ConfigDict

from common.models.enums import Visibility


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str | None
    email: str | None
    telegram_id: int | None
    display_name: str
    avatar_url: str | None
    locale: str
    timezone: str
    profile_visibility: Visibility
    is_pro: bool
