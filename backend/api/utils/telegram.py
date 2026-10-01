import hashlib
import hmac


def verify_login_widget(data: dict[str, str | int], bot_token: str) -> bool:
    """
    Проверить подпись данных Telegram Login Widget.

    https://core.telegram.org/widgets/login#checking-authorization
    """
    # пустым ключом подпись подделает кто угодно
    if not bot_token:
        return False

    fields = {key: value for key, value in data.items() if value is not None}
    received_hash = fields.pop("hash", None)
    if not isinstance(received_hash, str):
        return False

    check_string = "\n".join(f"{key}={fields[key]}" for key in sorted(fields))
    secret = hashlib.sha256(bot_token.encode()).digest()
    expected = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received_hash)
