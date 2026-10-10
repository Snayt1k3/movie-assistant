class AuthError(Exception):
    """Не удалось подтвердить личность: неверные данные, токен или подпись."""


class EmailTakenError(Exception):
    pass


class InvalidAccessTokenError(Exception):
    pass
