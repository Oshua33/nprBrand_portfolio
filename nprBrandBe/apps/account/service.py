from datetime import datetime, timedelta
import uuid
from esmerald import status
from edgy import or_
from nprOlusolaBe.core.schema import GetSingleParams, QueryType
from nprOlusolaBe.core.service import BaseService
from nprOlusolaBe.apps.account.models import User
from nprOlusolaBe.apps.account.v1 import schemas
from nprOlusolaBe.utils.base_response import get_error_response, get_response
from nprOlusolaBe.utils.password_hasher import PasswordManager
from nprOlusolaBe.lib.mail.mailer import Mailer
from nprOlusolaBe.configs import settings
from esmerald.security.jwt.token import Token
from esmerald.responses import JSONResponse
from esmerald.background import BackgroundTask


class AccountService:
    _service = BaseService[User](model=User, model_name="User")
    passwordManager = PasswordManager()

    async def _create_user_type(
        self,
        payload: schemas.UserRegistration,
        is_staff: bool = False,
        is_superuser: bool = False,
    ):
        check_user = await self._service.filter_obj(
            get_first=True,
            check={"email": payload.email},
            raise_error=False,
        )
        if check_user:
            raise get_error_response(
                detail=f"{self._service.model_name} already exists",
                status_code=status.HTTP_409_CONFLICT,
            )
        user_type = {}
        if is_staff:
            user_type["is_staff"] = True
        if is_superuser:
            user_type["is_superuser"] = True
        password = self.passwordManager.set_password(payload.password)
        user_data = payload.model_dump(exclude={"password"})
        user_data.update(user_type)

        user = await self._service.create(
            {
                "password": password,
                **user_data,
            }
        )
        exp = datetime.now() + timedelta(days=5)
        token = Token(sub=str(user.id), exp=exp)
        token_result = token.encode(
            key=settings.jwt_config.signing_key,
            algorithm=settings.jwt_config.algorithm,
        )
        mailer = Mailer(
            subject="Welcome email",
            template_name="email_verification_and_welcome.html",
            context={
                "username": user.first_name,
                "url": f"{settings.project_url}/confirm_email?token={token_result}",
            },
        )

        return JSONResponse(
            content={
                "data": "Account was created successfully, kindly check your email for email verification"
            },
            status_code=status.HTTP_201_CREATED,
            background=BackgroundTask(mailer.send_mail, recipient_emails=user.email),
        )

    async def forgot_password(self, payload: schemas.UserForgotPassword):
        user = await self._service.filter_obj(
            get_first=True,
            check={"email": payload.email, "is_active": True},
            raise_error=False,
        )
        if not user:
            return JSONResponse(
                content={
                    "data": "If your account exist, a password reset link has been sent to your email"
                },
                status_code=status.HTTP_200_OK,
            )
        exp = datetime.now() + timedelta(hours=5)
        token = Token(sub=str(user.id), exp=exp)
        token_result = token.encode(
            key=settings.jwt_config.signing_key,
            algorithm=settings.jwt_config.algorithm,
        )
        mailer = Mailer(
            subject="Password reset link",
            template_name="forgot_password.html",
            context={
                "username": user.first_name,
                "url": f"{settings.project_url}/reset_password?token={token_result}",
            },
        )
        return JSONResponse(
            content={"data": "Password reset link has been sent to your email"},
            status_code=status.HTTP_200_OK,
            background=BackgroundTask(mailer.send_mail, recipient_emails=user.email),
        )

    async def reset_password(self, payload: schemas.UserResetPassword):
        token = Token.decode(
            payload.token,
            key=settings.jwt_config.signing_key,
            algorithms=settings.jwt_config.algorithm,
        )
        if not token or not token.sub:
            raise get_error_response(
                detail="Invalid or expired token",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        user = await self._service.filter_obj(
            get_first=True,
            check={"id": token.sub},
            raise_error=False,
        )

        password = self.passwordManager.set_password(payload.password)
        to_update = {"password": password}
        if not user.is_verified:
            to_update.update({"is_verified": True})

        result = await self._service.update(id=user.id, payload=to_update)
        if not result:
            raise get_error_response(
                detail=f"Failed to update {self._service.model_name}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return JSONResponse(
            content={"data": "Password was reset successful"},
            status_code=status.HTTP_200_OK,
        )

    async def create_special_user(
        self,
        payload: schemas.UserAdminRegistration,
    ):

        if payload.is_staff and payload.is_superuser:
            return await self._create_user_type(
                payload=payload,
                is_staff=True,
                is_superuser=True,
            )
        if payload.is_staff:
            return await self._create_user_type(
                payload=payload,
                is_staff=True,
                is_superuser=False,
            )
        elif payload.is_superuser:
            return await self._create_user_type(
                payload,
                is_superuser=True,
                is_staff=True,
            )
        else:
            raise get_error_response(
                detail="user type must be provided, e.g. staff(is_staff) or superuser(is_superuser)",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    async def create(self, payload: schemas.UserRegistration):
        return await self._create_user_type(payload)


    async def activate_account(self, payload: schemas.EmailConfirmation):
        token: Token = Token.decode(
            payload.token,
            key=settings.jwt_config.signing_key,
            algorithms=settings.jwt_config.algorithm,
        )
        if not token or not token.sub:
            raise get_error_response(
                detail="Invalid or expired token",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        user = await self._service.filter_obj(
            get_first=True,
            check={"id": token.sub},
            raise_error=False,
        )
        if user.is_verified:
            return get_response(
                data={"message": "Account already verified"},
                status_code=status.HTTP_200_OK,
            )
        await self._service.update(id=user.id, payload={"is_verified": True})

        return get_response(
            data={"message": "Account activated successfully"},
            status_code=status.HTTP_200_OK,
        )

    async def get(
        self,
        user_id: uuid.UUID,
        params: GetSingleParams,
        is_active: bool | None = None,
    ):
        check = {}
        if is_active is not None:
            check["is_active"] = is_active
        return await self._service.get_single(
            object_id=user_id,
            **params.model_dump(),
            check=check,
            raise_error=True,
        )

    async def get_all(
        self,
        params: QueryType,
        is_active: bool | None = None,
        is_staff: bool | None = False,
        is_superuser: bool | None = False,
    ):
        check_list = []
        checks = {}
        if params.filter_string:
            check_list.append(
                or_.from_kwargs(
                    first_name__icontains=params.filter_string,
                    last_name__icontains=params.filter_string,
                    email__icontains=params.filter_string,
                )
            )
        if is_superuser is not None:
            checks["is_superuser"] = is_superuser
        if is_staff is not None:
            checks["is_staff"] = is_staff
        if is_active is not None:
            checks["is_active"] = is_active
        result = await self._service.filter_and_list(
            **params.model_dump(exclude={"filter_string"}),
            check=checks,
            check_list=check_list,
            fetch_distinct=True,
            exclude_secrets=True,
        )
        return result

    async def delete(self, user_id: uuid.UUID):
        return await self._service.delete(id=user_id)

    async def update(
        self,
        user_id: uuid.UUID,
        payload: schemas.UserUpdate | schemas.UserUpdateByAdmin,
    ) -> User:
        user = await self._service.get(
            id=user_id,
            raise_error=False,
        )
        check = {}
        if getattr(payload, "email", None) and user.email != payload.email:
            check = {"email__icontains": payload.email}
        if not user:
            raise get_error_response(
                detail="User does not exist",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return await self._service.update(
            id=user_id,
            payload=payload,
            check=check,
        )
