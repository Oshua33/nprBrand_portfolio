from uuid import UUID
from esmerald import Stream
from esmerald import (
    JSON,
    APIView,
    JSONResponse,
    Query,
    Response,
    delete,
    get,
    Inject,
    Injects,
    patch,
    post,
    put,
    status,
)
from h11 import Request
from nprOlusolaBe.apps.account.models import User
from nprOlusolaBe.apps.account.service import AccountService
from nprOlusolaBe.core.schema import (
    GetSingleParams,
    IFilterList,
    IFilterSingle,
    IResponseMessage,
)
from nprOlusolaBe.utils.list_endpoint_query_params import (
    query_params,
    QueryType,
    single_details_params,
    response,
)
from nprOlusolaBe.apps.account.v1 import schemas
from nprOlusolaBe.middleware.jwtAuthentication import JWTAuthMiddleware
from nprOlusolaBe.middleware.permission import (
    IsAdminOrSuperAdmin,
    IsCustomer,
    IsUserSuperAdmin,
)
from nprOlusolaBe.utils.get_owner_by_id import get_owner_view_id_from_request


class AccountAPIView(APIView):
    path = "/users"
    tags = ["User management"]
    dependencies = {"service": Inject(AccountService)}

    # this creates a user
    @post("/", status_code=status.HTTP_201_CREATED, responses=response)
    async def create_user(
        self,
        payload: schemas.UserRegistration,
        service: AccountService = Injects(),
    ) -> JSONResponse:
        return await service.create(payload=payload)

    # this create a user admin or superuser
    @post(
        "/admin",
        responses=response,
        middleware=[JWTAuthMiddleware],
        permissions=[IsUserSuperAdmin],
    )
    async def create_special_user(
        self,
        payload: schemas.UserAdminRegistration,
        service: AccountService = Injects(),
    ) -> JSONResponse:
        return await service.create_special_user(payload=payload)

    @get(
        "/",
        dependencies={"params": Inject(query_params)},
        # middleware=[JWTAuthMiddleware],
        # permissions=[IsAdminOrSuperAdmin],
    )
    async def list_users(
        self,
        params: QueryType = Injects(),
        service: AccountService = Injects(),
        is_active: bool | None = None,
        is_staff: bool | None = None,
        is_superuser: bool | None = None,
    ) -> IFilterList | list[User] | Stream:
        return await service.get_all(
            params=params,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser,
        )

    # fetches one users by id
    # permission for isadmin
    @get(
        "/{user_id}",
        dependencies={"params": Inject(single_details_params)},
        responses=response,
        # middleware=[JWTAuthMiddleware],
        # permissions=[IsAdminOrSuperAdmin],
    )
    async def get_user_details(
        self,
        user_id: UUID,
        is_active: bool | None = Query(default=None),
        params: GetSingleParams = Injects(),
        service: AccountService = Injects(),
    ) -> IFilterSingle:
        return await service.get(
            user_id=user_id,
            params=params,
            is_active=is_active,
        )

    # update a user details
    @put(
        "/",
        responses=response,
        # middleware=[JWTAuthMiddleware],
        # permissions=[IsCustomer],
    )
    async def update_user_details(
        self,
        request: Request,
        payload: schemas.UserUpdate,
        service: AccountService = Injects(),
    ) -> IResponseMessage:
        return await service.update(
            user_id=get_owner_view_id_from_request(request),
            payload=payload,
        )

    # update made by admin -- patch endpoint
    @patch(
        "/{user_id}",
        responses=response,
        # middleware=[JWTAuthMiddleware],
        # permissions=[IsAdminOrSuperAdmin],
    )
    async def update_user_details_by_admin(
        self,
        user_id: UUID,
        payload: schemas.UserUpdateByAdmin,
        service: AccountService = Injects(),
    ) -> IResponseMessage:
        return await service.update(user_id=user_id, payload=payload)

    @patch("/verify", responses=response)
    async def account_verification(
        self,
        payload: schemas.EmailConfirmation,
        service: AccountService = Injects(),
    ) -> User:
        return await service.activate_account(payload=payload)

    @post("/forgotpassword", responses=response)
    async def forgot_password(
        self,
        payload: schemas.UserForgotPassword,
        service: AccountService = Injects(),
    ) -> JSONResponse:
        return await service.forgot_password(payload=payload)

    @patch("/resetpassword", responses=response)
    async def reset_password(
        self,
        payload: schemas.UserResetPassword,
        service: AccountService = Injects(),
    ) -> JSONResponse:
        return await service.reset_password(payload=payload)

    # delete a user
    # permisonm-- only admin sud delete a user
    @delete("/{user_id}", status_code=status.HTTP_200_OK, responses=response, permissions=[IsUserSuperAdmin])
    async def delete_user(
        self,
        user_id: UUID,
        service: AccountService = Injects(),
    ) -> IResponseMessage:
        return await service.delete(user_id=user_id)
