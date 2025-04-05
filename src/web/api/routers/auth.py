"""
Authentication router for the DockerForge Web UI.

This module provides the API endpoints for user authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from src.web.api.schemas.auth import (
    Token, User, UserCreate, UserUpdate, UserResponse,
    PasswordChange, PasswordReset, PasswordResetVerify
)
from src.web.api.services.auth import (
    authenticate_user, create_access_token, get_current_active_user,
    create_user, get_users, get_user_by_id, check_permission,
    change_password, reset_password_with_local_auth,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.web.api.database import get_db
from src.web.api.models.user import User as UserModel

# Create router
router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    If the user's password change is required, the response will include
    password_change_required=True.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "password_change_required": user.password_change_required
    }


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.

    This is an alias for /token for better API naming.
    If the user's password change is required, the response will include
    password_change_required=True.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "password_change_required": user.password_change_required
    }


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    """
    user_data = user.dict()
    new_user = create_user(user_data, db)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        is_active=new_user.is_active,
        is_superuser=new_user.is_superuser,
        roles=[role.name for role in new_user.roles],
    )


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get current user information.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        roles=[role.name for role in current_user.roles],
    )


@router.get("/users", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all users.
    """
    # Check permission
    if not check_permission(current_user, "users:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    users = get_users(skip, limit, db)

    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            roles=[role.name for role in user.roles],
        )
        for user in users
    ]


@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a user by ID.
    """
    # Check permission
    if not check_permission(current_user, "users:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        roles=[role.name for role in user.roles],
    )


@router.post("/change-password")
async def change_user_password(
    password_data: PasswordChange,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change the current user's password.
    """
    success = change_password(
        current_user,
        password_data.current_password,
        password_data.new_password,
        db
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    return {"message": "Password changed successfully"}


@router.post("/reset-password-request")
async def request_password_reset(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """
    Request a password reset.

    This endpoint checks if the username exists and returns a success message.
    In a real implementation, this would typically send an email with a reset link.
    """
    user = db.query(UserModel).filter(UserModel.username == reset_data.username).first()
    if not user:
        # Return success even if user doesn't exist to prevent username enumeration
        return {"message": "If the username exists, password reset instructions will be provided"}

    # In a real implementation, this would send an email with a reset link
    # For this implementation, we'll just return a success message
    return {"message": "If the username exists, password reset instructions will be provided"}


@router.post("/reset-password-verify")
async def verify_and_reset_password(
    reset_data: PasswordResetVerify,
    db: Session = Depends(get_db)
):
    """
    Verify local credentials and reset password.
    """
    success = reset_password_with_local_auth(
        reset_data.username,
        reset_data.local_username,
        reset_data.local_password,
        reset_data.new_password,
        db
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials or username",
        )

    return {"message": "Password reset successfully"}


@router.post("/logout")
async def logout():
    """
    Logout user.

    Note: With JWT, logout is typically handled client-side by removing the token.
    This endpoint is provided for API completeness.
    """
    return {"message": "Logout successful"}
