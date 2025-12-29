from esmerald.contrib.auth.hashers import (
    check_password,
    is_password_usable,
    make_password,
)
from nprOlusolaBe.utils.base_response import get_error_response


class PasswordManager:
    @classmethod
    def set_password(cls, raw_password: str) -> str:
        if not cls._is_valid_password(raw_password):
            raise get_error_response("Password is not valid")
        return make_password(raw_password)

    @classmethod
    def _is_valid_password(cls, password: str) -> None:
        return True if password else False

    @classmethod
    async def check_password(cls, plain_password: str, hashed_password: str) -> bool:
        return await check_password(plain_password, hashed_password)

    @classmethod
    def set_unusable_password(cls) -> None:
        return make_password(None)

    @classmethod
    def has_usable_password(cls, password: str | None) -> bool:
        return is_password_usable(password)
