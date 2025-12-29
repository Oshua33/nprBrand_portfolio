from esmerald import Request
from esmerald.permissions.base import BaseAbstractUserPermission
from esmerald.types import APIGateHandler
from nprOlusolaBe.apps.account.models import User


class IsUserSuperAdmin(BaseAbstractUserPermission):
    def is_user_authenticated(self, request: "Request") -> bool:
        if request.user:
            return True

    def is_user_staff(self, request: "Request") -> bool:
        user: User = request.user
        if user and user.is_superuser:
            return True

    def has_permission(self, request: "Request", apiview: "APIGateHandler"):
        super().has_permission(request, apiview)
        return bool(request.user and self.is_user_staff(request))


class IsAdminOrSuperAdmin(IsUserSuperAdmin):
    def is_user_staff(self, request: "Request") -> bool:
        user: User = request.user
        if user and (user.is_superuser or user.is_staff):
            return True


class IsCustomer(IsUserSuperAdmin):
    def is_user_staff(self, request: "Request") -> bool:
        user: User = request.user
        if user and user.is_active:
            return True
