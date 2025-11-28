from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.security import ALGORITHM, SECRET_KEY
from app.models.auth import Project, User
from app.schemas.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception from None

    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_active_user)):
    # We need to import UserRole here or compare string
    if current_user.role != "ADMIN":  # Assuming Enum string comparison works, or import Enum
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user


def verify_project_access(
    project_id: str = Header(..., alias="X-Project-ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> str:
    """
    Verify that the project exists and user has access to it.
    Returns the validated project_id.
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise NotFoundError("Project", project_id)

    # Check if user has access to this project
    # Admin users have access to all projects
    if current_user.role == "ADMIN":
        return project_id

    # Check if user is the owner or has explicit access
    if project.owner_id and project.owner_id != current_user.id:
        # Check if user's client matches the project's client
        if project.client_id and current_user.client_id != project.client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this project",
            )

    return project_id
