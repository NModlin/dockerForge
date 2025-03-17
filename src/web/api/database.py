"""
Database configuration for the DockerForge Web UI.

This module provides the database configuration and session management.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

from .models import Base

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://dockerforge:dockerforge@db:5432/dockerforge")

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Check connection before using it
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False,          # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create scoped session for thread safety
db_session = scoped_session(SessionLocal)


def get_db():
    """
    Get database session.
    
    This function is used as a dependency in FastAPI endpoints.
    """
    db = db_session()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Get database session as a context manager.
    
    This function is used for scripts and background tasks.
    """
    db = db_session()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database.
    
    This function creates all tables in the database.
    """
    # Import all models to ensure they are registered with Base
    from .models import __all__
    
    # Create tables
    Base.metadata.create_all(bind=engine)


def drop_db():
    """
    Drop all tables in the database.
    
    This function is used for testing and development.
    """
    Base.metadata.drop_all(bind=engine)


def create_initial_data():
    """
    Create initial data in the database.
    
    This function is used to populate the database with initial data.
    """
    from .models import User, Role, Permission
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    with get_db_context() as db:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            return
        
        # Create admin role
        admin_role = Role(name="admin", description="Administrator role with full access")
        db.add(admin_role)
        
        # Create user role
        user_role = Role(name="user", description="Regular user role with limited access")
        db.add(user_role)
        
        # Create permissions
        permissions = [
            Permission(name="users:read", description="Read users"),
            Permission(name="users:write", description="Create and update users"),
            Permission(name="users:delete", description="Delete users"),
            Permission(name="containers:read", description="Read containers"),
            Permission(name="containers:write", description="Create and update containers"),
            Permission(name="containers:delete", description="Delete containers"),
            Permission(name="images:read", description="Read images"),
            Permission(name="images:write", description="Create and update images"),
            Permission(name="images:delete", description="Delete images"),
            Permission(name="volumes:read", description="Read volumes"),
            Permission(name="volumes:write", description="Create and update volumes"),
            Permission(name="volumes:delete", description="Delete volumes"),
            Permission(name="networks:read", description="Read networks"),
            Permission(name="networks:write", description="Create and update networks"),
            Permission(name="networks:delete", description="Delete networks"),
            Permission(name="compose:read", description="Read compose projects"),
            Permission(name="compose:write", description="Create and update compose projects"),
            Permission(name="compose:delete", description="Delete compose projects"),
            Permission(name="security:read", description="Read security scans"),
            Permission(name="security:write", description="Create and update security scans"),
            Permission(name="backup:read", description="Read backups"),
            Permission(name="backup:write", description="Create and update backups"),
            Permission(name="backup:delete", description="Delete backups"),
            Permission(name="monitoring:read", description="Read monitoring data"),
            Permission(name="monitoring:write", description="Create and update monitoring data"),
            Permission(name="settings:read", description="Read settings"),
            Permission(name="settings:write", description="Update settings"),
        ]
        
        for permission in permissions:
            db.add(permission)
        
        # Flush to get IDs
        db.flush()
        
        # Add all permissions to admin role
        admin_role.permissions = permissions
        
        # Add read permissions to user role
        user_role.permissions = [p for p in permissions if p.name.endswith(":read")]
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=pwd_context.hash("admin"),
            is_active=True,
            is_superuser=True,
            password_change_required=True,
        )
        admin_user.roles = [admin_role]
        db.add(admin_user)
        
        # Create regular user
        regular_user = User(
            username="user",
            email="user@example.com",
            full_name="Regular User",
            hashed_password=pwd_context.hash("user"),
            is_active=True,
            is_superuser=False,
            password_change_required=True,
        )
        regular_user.roles = [user_role]
        db.add(regular_user)
        
        # Commit changes
        db.commit()
