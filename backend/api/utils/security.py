import datetime
import hashlib
import secrets

import jwt
from exceptions import InvalidAccessToken
from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return _password_hash.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _password_hash.verify(password, password_hash)


def create_access_token(user_id: int, secret: str, algorithm: str, ttl: datetime.timedelta) -> str:
    now = datetime.datetime.now(datetime.UTC)
    payload = {"sub": str(user_id), "iat": now, "exp": now + ttl, "type": "access"}
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_access_token(token: str, secret: str, algorithm: str) -> int:
    try:
        payload = jwt.decode(
            token, secret, algorithms=[algorithm], options={"require": ["sub", "exp"]}
        )
    except jwt.PyJWTError as e:
        raise InvalidAccessToken from e
    if payload.get("type") != "access":
        raise InvalidAccessToken
    return int(payload["sub"])


def new_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> bytes:
    return hashlib.sha256(token.encode()).digest()
