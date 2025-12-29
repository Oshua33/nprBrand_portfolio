from datetime import datetime
from jose import JWTError
from esmerald import Request, status
from esmerald.conf import settings
from nprOlusolaBe.apps.account.models import User
from nprOlusolaBe.apps.auth.v1 import schemas
from nprOlusolaBe.configs import settings
from esmerald.security.jwt.token import Token
from nprOlusolaBe.apps.account.service import AccountService
from nprOlusolaBe.utils.base_response import get_error_response
from nprOlusolaBe.utils.ip_checker import get_ip_address
from nprOlusolaBe.utils.password_hasher import PasswordManager


class AuthService:
    _user_service = AccountService()
    _password_manager = PasswordManager()

    @classmethod
    async def authenticate(cls, payload: schemas.LoginIn, request: Request) -> str:
        try:
            user = await cls._user_service._service.filter_obj(
                get_first=True,
                check=dict(email=payload.email),
            )
            if not user:
                raise get_error_response(
                    detail=f"Either email or password do not match",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            is_password_valid = await cls._password_manager.check_password(
                plain_password=payload.password,
                hashed_password=user.password,
            )

            if is_password_valid and cls.is_user_able_to_authenticate(user):
                return cls.generate_user_token(
                    user_id=user.id,
                    user_ip_address=get_ip_address(request),
                )
            raise get_error_response(
                detail="Email address or password is incorrect",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        except JWTError:
            cls._password_manager.set_password("passwordhsdhddfsdfffsfsdfs")
            raise get_error_response(
                detail="Authentication failed",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

    async def refresh_authenticate(
        cls, payload: schemas.IRefreshToken, request: Request
    ) -> str:

        try:
            token = Token.decode(
                payload.refresh_token,
                key=settings.secret_key,
                algorithms=settings.jwt_config.algorithm,
            )
            if token and token.aud != get_ip_address(request):
                raise get_error_response(
                    detail="Invalid token",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )
            if token:
                return cls.generate_user_token(
                    user_id=token.sub,
                    user_ip_address=get_ip_address(request),
                )
        except Exception:
            raise get_error_response(
                detail="Authentication failed",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

    @classmethod
    def is_user_able_to_authenticate(cls, user: User):
        if user.is_staff and user.is_active and user.is_verified:
            return True
        elif user.is_superuser and user.is_active and user.is_verified:
            return True
        elif not user.is_verified and user.is_active:
            return True
        elif user.is_active:
            return True
        else:
            raise get_error_response(
                "Authentication failed please contact the administrator",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

    @classmethod
    def generate_user_token(
        cls,
        user_id: str,
        user_ip_address: str,
    ):

        access_token = Token(
            sub=str(user_id),
            exp=datetime.now() + settings.jwt_config.access_token_lifetime,
            aud=user_ip_address,
        )
        refresh_token = Token(
            sub=str(user_id),
            exp=datetime.now() + settings.jwt_config.refresh_token_lifetime,
            aud=user_ip_address,
        )
        return schemas.TokenResponse(
            access_token=access_token.encode(
                key=settings.jwt_config.signing_key,
                algorithm=settings.jwt_config.algorithm,
            ),
            refresh_token=refresh_token.encode(
                key=settings.secret_key,
                algorithm=settings.jwt_config.algorithm,
            ),
        ).model_dump()
