from esmerald import APIView, Inject, Injects, Request, get, post, status
from nprOlusolaBe.apps.account.models import User
from nprOlusolaBe.apps.auth.service import AuthService
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware
from nprOlusolaBe.middleware.permission import IsCustomer
from nprOlusolaBe.utils.list_endpoint_query_params import response
from nprOlusolaBe.apps.auth.v1 import schemas


class AuthAPIView(APIView):
    path = "/auths"
    tags = ["Auth management"]
    dependencies = {"service": Inject(AuthService)}

    @post("/login", status_code=status.HTTP_200_OK, responses=response)
    async def login(
        self,
        payload: schemas.LoginIn,
        request: Request,
        service: AuthService = Injects(),
    ) -> schemas.TokenResponse:
        return await service.authenticate(
            payload=payload,
            request=request,
        )

    @get(
        "/whoami",
        status_code=status.HTTP_200_OK,
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsCustomer],
    )
    async def get_current_login_user(
        self,
        request: Request,
    ) -> User:
        return request.user

    @post("/refresh", responses=response)
    async def login_refresh_token(
        self,
        payload: schemas.IRefreshToken,
        request: Request,
        service: AuthService = Injects(),
    ) -> schemas.TokenResponse:
        return await service.refresh_authenticate(
            payload=payload,
            request=request,
        )
