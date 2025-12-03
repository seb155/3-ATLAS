"""
Authentication service for workspace SSO.

Provides JWT token creation/validation, password hashing,
and user authentication across workspace applications.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user import User
from app.config import get_settings

settings = get_settings()

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """
    Shared authentication service for workspace apps.
    Uses workspace_auth.users table for SSO-like experience.
    """

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against bcrypt hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.
        Token is valid across all workspace apps (shared SECRET_KEY).

        Args:
            data: Payload data to encode in the token
            expires_delta: Optional custom expiration time

        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.access_token_expire_minutes
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": "nexus",  # Issuer (which app created this token)
        })

        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """
        Decode and validate JWT token.

        Args:
            token: JWT token string

        Returns:
            dict: Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            return payload
        except JWTError:
            return None

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate user by email and password.

        Args:
            db: Database session (auth database)
            email: User email
            password: Plain text password

        Returns:
            User: User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        if not AuthService.verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    @staticmethod
    def get_current_user(db: Session, token: str) -> Optional[User]:
        """
        Get current user from JWT token.

        Args:
            db: Database session (auth database)
            token: JWT token string

        Returns:
            User: User object if token valid, None otherwise
        """
        payload = AuthService.decode_token(token)

        if payload is None:
            return None

        user_id: str = payload.get("sub")
        if user_id is None:
            return None

        user = db.query(User).filter(User.id == UUID(user_id)).first()
        return user

    @staticmethod
    def register_user(
        db: Session,
        email: str,
        password: str,
        full_name: Optional[str] = None
    ) -> User:
        """
        Register a new user in workspace_auth.users.

        Args:
            db: Database session (auth database)
            email: User email
            password: Plain text password
            full_name: User's full name (optional)

        Returns:
            User: Newly created user object

        Raises:
            ValueError: If user with email already exists
        """
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        hashed_password = AuthService.get_password_hash(password)

        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            app_permissions={"nexus": ["editor"]},  # Default permission
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def update_last_login(db: Session, user: User) -> None:
        """
        Update user's last login timestamp.

        Args:
            db: Database session
            user: User object
        """
        user.last_login_at = datetime.utcnow()
        db.commit()
