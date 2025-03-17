"""
Authentication service for the DockerForge Web UI.

This module provides the authentication services for the DockerForge Web UI.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import jwt, JWTError
from passlib.context import CryptContext
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User as UserModel, Role
from ..schemas.auth import User, UserInDB, TokenData

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "development_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    """
    return pwd_context.hash(password)


def get_user(username: str, db: Session) -> Optional[UserModel]:
    """
    Get a user by username.
    """
    return db.query(UserModel).filter(UserModel.username == username).first()


def get_user_by_id(user_id: int, db: Session) -> Optional[UserModel]:
    """
    Get a user by ID.
    """
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def get_users(skip: int = 0, limit: int = 100, db: Session = None) -> List[UserModel]:
    """
    Get all users.
    """
    return db.query(UserModel).offset(skip).limit(limit).all()


def create_user(user_data: dict, db: Session) -> UserModel:
    """
    Create a new user.
    """
    # Check if user already exists
    existing_user = get_user(user_data["username"], db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data["password"])
    
    # Create user
    user = UserModel(
        username=user_data["username"],
        email=user_data["email"],
        full_name=user_data.get("full_name"),
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False,
    )
    
    # Add user role
    user_role = db.query(Role).filter(Role.name == "user").first()
    if user_role:
        user.roles = [user_role]
    
    # Add to database
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


def authenticate_user(username: str, password: str, db: Session) -> Optional[UserModel]:
    """
    Authenticate a user.
    """
    user = get_user(username, db)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    
    return user


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserModel:
    """
    Get the current user from the JWT token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = get_user(token_data.username, db)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def check_permission(user: UserModel, permission: str) -> bool:
    """
    Check if a user has a specific permission.
    """
    # Superusers have all permissions
    if user.is_superuser:
        return True
    
    # Check user roles for the permission
    for role in user.roles:
        for perm in role.permissions:
            if perm.name == permission:
                return True
    
    return False


async def get_current_active_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """
    Get the current active user.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
