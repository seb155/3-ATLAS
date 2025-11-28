"""
User model for shared workspace authentication.

This model maps to the workspace_auth.users table in the shared
authentication database, enabling SSO-like functionality across
all workspace applications (Nexus, Synapse, etc.).

Database Location:
- Schema: workspace_auth (in postgres database)
- Table: users
- Created by: workspace/databases/postgres/init/04-nexus-init.sql
"""

from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from typing import List
import uuid
from ..database import AuthBase


class User(AuthBase):
    """
    Shared user model across workspace applications.

    This model is stored in the workspace_auth schema and shared
    between Nexus, Synapse, and other workspace apps for SSO authentication.

    Attributes:
        id: UUID primary key
        email: Unique email address (used for login)
        hashed_password: Bcrypt hashed password
        full_name: User's full name (optional)
        is_active: Whether user account is active
        is_superuser: Whether user has superuser privileges
        created_at: Timestamp of account creation
        updated_at: Timestamp of last update
        last_login_at: Timestamp of last successful login
        app_permissions: JSONB storing per-app permissions
        metadata: JSONB for extensibility

    Example app_permissions structure:
        {
            "nexus": ["editor", "admin"],
            "synapse": ["viewer"],
            "portal": ["viewer"]
        }
    """

    __tablename__ = "users"
    __table_args__ = {"schema": "workspace_auth"}

    # Primary key (UUID for cross-app compatibility)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))

    # Status fields
    is_active = Column(Boolean, default=True, index=True)
    is_superuser = Column(Boolean, default=False)

    # Timestamps (timezone-aware)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))

    # App-specific permissions (JSONB)
    # Example: {"nexus": ["editor", "admin"], "synapse": ["viewer"]}
    app_permissions = Column(JSON, default={})

    # Metadata for extensibility (JSONB)
    # Note: Column name is 'user_metadata' to avoid SQLAlchemy reserved 'metadata' attribute
    user_metadata = Column("metadata", JSON, default={})

    def has_permission(self, app_name: str, permission: str) -> bool:
        """
        Check if user has a specific permission for an app.

        Args:
            app_name: Name of the app (e.g., "nexus", "synapse")
            permission: Permission to check (e.g., "editor", "admin")

        Returns:
            bool: True if user has the permission, False otherwise

        Example:
            if user.has_permission("nexus", "editor"):
                # Allow editing
                pass
        """
        app_perms = self.app_permissions.get(app_name, [])
        return permission in app_perms or "admin" in app_perms

    def has_any_permission(self, app_name: str, permissions: List[str]) -> bool:
        """
        Check if user has any of the specified permissions for an app.

        Args:
            app_name: Name of the app
            permissions: List of permissions to check

        Returns:
            bool: True if user has any of the permissions
        """
        app_perms = self.app_permissions.get(app_name, [])
        return any(perm in app_perms for perm in permissions) or "admin" in app_perms

    def add_permission(self, app_name: str, permission: str) -> None:
        """
        Add a permission for an app.

        Args:
            app_name: Name of the app
            permission: Permission to add
        """
        if app_name not in self.app_permissions:
            self.app_permissions[app_name] = []

        if permission not in self.app_permissions[app_name]:
            self.app_permissions[app_name].append(permission)

    def remove_permission(self, app_name: str, permission: str) -> None:
        """
        Remove a permission for an app.

        Args:
            app_name: Name of the app
            permission: Permission to remove
        """
        if app_name in self.app_permissions:
            if permission in self.app_permissions[app_name]:
                self.app_permissions[app_name].remove(permission)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>"

    def __str__(self):
        return self.email or f"User {self.id}"
