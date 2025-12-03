"""
Pydantic schemas for user authentication and workspace integration.

These schemas define the API request/response models for user
authentication, registration, and profile management in the
shared workspace environment.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    """Base schema for user with common fields"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters long"
    )
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserPasswordChange(BaseModel):
    """Schema for password change"""
    current_password: str
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password must be at least 8 characters long"
    )


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class UserResponse(UserBase):
    """
    Schema for user response (public profile).
    Excludes sensitive fields like hashed_password.
    """
    id: UUID
    is_active: bool
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    app_permissions: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(UserResponse):
    """
    Detailed user response with metadata.
    Used for admin endpoints or user profile page.
    """
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# TOKEN SCHEMAS
# ============================================================================

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until expiration
    user: UserResponse  # Include user info in token response


class TokenData(BaseModel):
    """Schema for decoded JWT token payload"""
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    app: Optional[str] = None  # Which app issued the token
    exp: Optional[int] = None  # Expiration timestamp
    iat: Optional[int] = None  # Issued at timestamp


class RefreshToken(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


# ============================================================================
# PERMISSION SCHEMAS
# ============================================================================

class PermissionUpdate(BaseModel):
    """Schema for updating user permissions for an app"""
    app_name: str = Field(..., description="Name of the app (e.g., 'nexus', 'synapse')")
    permissions: list[str] = Field(..., description="List of permissions to set")


class PermissionCheck(BaseModel):
    """Schema for checking user permissions"""
    app_name: str
    permission: str


class PermissionCheckResponse(BaseModel):
    """Response for permission check"""
    has_permission: bool
    user_permissions: list[str]  # All permissions user has for the app


# ============================================================================
# ADMIN SCHEMAS
# ============================================================================

class UserAdminUpdate(BaseModel):
    """Schema for admin user updates"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    app_permissions: Optional[Dict[str, Any]] = None


class UserListResponse(BaseModel):
    """Schema for paginated user list"""
    users: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
