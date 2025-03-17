"""
User models for the DockerForge Web UI.

This module provides the SQLAlchemy models for user management.
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from .base import BaseModel, TimestampMixin, Base


# Association table for user-role many-to-many relationship
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('role_id', ForeignKey('roles.id'), primary_key=True)
)


class User(BaseModel, TimestampMixin):
    """
    User model for authentication and authorization.
    """
    __tablename__ = 'users'
    
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    password_change_required = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    
    # Proxies
    role_names = association_proxy('roles', 'name')
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class Role(BaseModel, TimestampMixin):
    """
    Role model for role-based access control.
    """
    __tablename__ = 'roles'
    
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=True)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    
    # Proxies
    permission_names = association_proxy('permissions', 'name')
    
    def __repr__(self):
        return f"<Role(name='{self.name}')>"


# Association table for role-permission many-to-many relationship
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', ForeignKey('permissions.id'), primary_key=True)
)


class Permission(BaseModel, TimestampMixin):
    """
    Permission model for fine-grained access control.
    """
    __tablename__ = 'permissions'
    
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=True)
    
    # Relationships
    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    
    def __repr__(self):
        return f"<Permission(name='{self.name}')>"
