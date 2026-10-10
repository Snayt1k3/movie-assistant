class UserNotFoundError(Exception):
    pass


class ProfileHiddenError(Exception):
    """Профиль закрыт настройкой видимости от этого зрителя."""


class UsernameTakenError(Exception):
    pass


class CannotFollowSelfError(Exception):
    pass
