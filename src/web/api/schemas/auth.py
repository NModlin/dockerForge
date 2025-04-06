"""
Authentication schemas for the DockerForge Web UI.

This module provides the Pydantic schemas for authentication.
"""

from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """
    Token schema for JWT authentication.
    """

    access_token: str
    token_type: str
    password_change_required: bool = False


class TokenData(BaseModel):
    """
    Token data schema for JWT payload.
    """

    username: Optional[str] = None
    scopes: List[str] = []


class UserBase(BaseModel):
    """
    Base user schema.
    """

    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """
    User creation schema.
    """

    password: str


class UserUpdate(BaseModel):
    """
    User update schema.
    """

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """
    User schema for responses.
    """

    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    roles: List[str] = []

    class Config:
        orm_mode = True


class User(UserBase):
    """
    User schema for internal use.
    """

    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True


class UserInDB(User):
    """
    User schema for database storage.
    """

    hashed_password: str

    class Config:
        orm_mode = True


class RoleBase(BaseModel):
    """
    Base role schema.
    """

    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """
    Role creation schema.
    """

    permissions: List[str] = []


class RoleUpdate(BaseModel):
    """
    Role update schema.
    """

    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class Role(RoleBase):
    """
    Role schema for responses.
    """

    id: int
    permissions: List[str] = []

    class Config:
        orm_mode = True


class PermissionBase(BaseModel):
    """
    Base permission schema.
    """

    name: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    """
    Permission creation schema.
    """

    pass


class Permission(PermissionBase):
    """
    Permission schema for responses.
    """

    id: int

    class Config:
        orm_mode = True


class PasswordChange(BaseModel):
    """
    Password change schema.
    """

    current_password: str
    new_password: str


class PasswordReset(BaseModel):
    """
    Password reset schema.
    """

    username: str


class PasswordResetVerify(BaseModel):
    """
    Password reset verification schema using local login.
    """

    username: str
    local_username: str
    local_password: str
    new_password: str
