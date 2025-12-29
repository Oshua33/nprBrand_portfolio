from typing import Any
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator


class UserBase(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)


class UserRegistration(UserBase):
    password: str = Field(min_length=8)
    email: EmailStr


class UserAdminRegistration(UserBase):
    password: str = Field(min_length=8)
    email: EmailStr
    is_staff: bool = Field(default=False)
    is_superuser: bool = Field(default=False)


class UserUpdate(UserBase):
    pass


class UserUpdateByAdmin(BaseModel):
    email: EmailStr
    is_active: bool = Field(default=True)
    is_staff: bool = Field(default=False)
    is_superuser: bool = Field(default=False)


class EmailConfirmation(BaseModel):
    token: str


class UserLogin(BaseModel):
    password: str = Field(min_length=8)
    email: EmailStr


class UserForgotPassword(BaseModel):
    email: EmailStr


class UserResetPassword(BaseModel):
    password: str = Field(min_length=8)
    password_confirmation: str = Field(min_length=8)
    token: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> "UserResetPassword":
        if self.password != self.password_confirmation:
            raise ValueError("Passwords do not match")
        return self
