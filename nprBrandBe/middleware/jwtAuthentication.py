import uuid
from esmerald import HTTPException
from nprOlusolaBe.configs import settings
from esmerald.exceptions import NotAuthorized
from esmerald.middleware.authentication import AuthResult, BaseAuthMiddleware
from esmerald.security.jwt.token import Token
from lilya._internal._connection import Connection
from lilya.types import ASGIApp
from edgy.exceptions import ObjectNotFound
from nprOlusolaBe.apps.account.models import User
from nprOlusolaBe.apps.account.service import AccountService



class JWTAuthMiddleware(BaseAuthMiddleware):
    def __init__(self, app: "ASGIApp"):
        super().__init__(app)
        self.app = app
        self.config = settings.jwt_config
        self.user_service = AccountService()

    async def retrieve_user(self, user_id: uuid.UUID) -> User:
        try:
            return await self.user_service._service.model.query.exclude_secrets().get(
                pk=user_id
            )
        except ObjectNotFound:
            raise NotAuthorized()
        except HTTPException:
            raise NotAuthorized(f"Failed to authenticate user")

    async def authenticate(self, request: Connection) -> AuthResult:
        token = request.headers.get(self.config.api_key_header)

        if not token:
            token = request.cookies.get(self.config.api_key_header)
        if not token:
            token = request.headers.get(self.config.authorization_header)
            if token:
                token = token.split()[1]
        if not token:
            raise NotAuthorized("JWT token not found.")
        try:

            token: Token = Token.decode(
                token=token,
                key=self.config.signing_key,
                algorithms=self.config.algorithm,
            )

            user = await self.retrieve_user(token.sub)
            return AuthResult(user=user)
        except Exception as e:
            raise NotAuthorized(str(e))
