"""
Authentication router for workspace SSO.

Provides endpoints for user registration, login, and profile management
using shared workspace_auth database.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime

from app.database import get_auth_db
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth_service import AuthService
from app.models.user import User
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_auth_db)
) -> User:
    """Dependency to get current authenticated user from JWT token"""
    user = AuthService.get_current_user(db, token)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_auth_db)):
    """
    Register a new user in workspace_auth.users.
    User will be able to access Nexus and other workspace apps.
    """
    try:
        new_user = AuthService.register_user(
            db=db,
            email=user.email,
            password=user.password,
            full_name=user.full_name
        )
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_auth_db)
):
    """
    Login with email and password.
    Returns JWT access token valid across all workspace apps.
    """
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "email": user.email, "app": "nexus"},
        expires_delta=access_token_expires
    )

    # Update last login
    AuthService.update_last_login(db, user)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
        "user": user
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user.
    Token can be issued by Nexus or any other workspace app.
    """
    return current_user


@router.get("/health")
def health_check():
    """Health check endpoint for authentication service"""
    return {
        "status": "healthy",
        "service": "nexus-auth",
        "timestamp": datetime.utcnow().isoformat()
    }
