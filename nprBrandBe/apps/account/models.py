from datetime import datetime
from typing import ClassVar
import edgy
from nprOlusolaBe.lib.database.base_model import BaseModel


class InactiveManager(edgy.Manager):
    def get_queryset(self) -> edgy.QuerySet:
        queryset = super().get_queryset().filter(is_active=False)
        return queryset


class ActiveManager(edgy.Manager):
    def get_queryset(self) -> edgy.QuerySet:
        queryset = super().get_queryset().filter(is_active=True)
        return queryset


class StaffManager(edgy.Manager):
    def get_queryset(self) -> edgy.QuerySet:
        queryset = super().get_queryset().filter(is_staff=True)
        return queryset


class SupperUserManager(edgy.Manager):
    def get_queryset(self) -> edgy.QuerySet:
        queryset = super().get_queryset().filter(is_superuser=True)
        return queryset


class SupperUserOrStaffManager(edgy.Manager):
    def get_queryset(self) -> edgy.QuerySet:
        queryset = (
            super()
            .get_queryset()
            .filter(edgy.Q(is_superuser=True) | edgy.Q(is_staff=True))
        )
        return queryset


class User(BaseModel):
    first_name: str = edgy.CharField(max_length=40)
    last_name: str = edgy.CharField(max_length=40)
    email: str = edgy.EmailField(max_length=120, unique=True)
    password: str = edgy.PasswordField(max_length=128, secret=True)
    last_login: datetime = edgy.DateTimeField(null=True)
    is_active: bool = edgy.BooleanField(default=True)
    is_staff: bool = edgy.BooleanField(default=False)
    is_superuser: bool = edgy.BooleanField(default=False)
    is_verified: bool = edgy.BooleanField(default=False, null=True)
    InactiveUserQuery: ClassVar[edgy.Manager] = InactiveManager()
    StaffUserQuery: ClassVar[edgy.Manager] = StaffManager()
    SupperUserQuery: ClassVar[edgy.Manager] = SupperUserManager()
    ActiveQuery: ClassVar[edgy.Manager] = ActiveManager()
    superUserOrStaff: ClassVar[edgy.Manager] = SupperUserOrStaffManager()
