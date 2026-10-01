class AuthError(Exception):
    """Не удалось подтвердить личность: неверные данные, токен или подпись."""


class EmailTaken(Exception):
    pass


class InvalidAccessToken(Exception):
    pass
