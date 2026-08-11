# from datetime import datetime, timedelta, timezone
# from jose import jwt
# from backend.config import settings
# from backend import models

# def create_access_token(user: models.User):
#     expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

#     payload = {
#         "sub": user.email,
#         "user_id": user.user_id, 
#         "role_id": user.role_id,
#         "exp": expire
#     }

#     token = jwt.encode(
#         payload,
#         settings.JWT_SECRET,
#         algorithm=settings.JWT_ALGORITHM
#     )
#     return token

import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend import models


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    # bcrypt has a hard 72-byte limit on input length
    pw_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pw_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(pw_bytes, hashed_password.encode("utf-8"))


def create_access_token(data: dict):

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = data.copy()
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(models.User).filter(models.User.email == username).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify if user account is currently locked out
    if user.locked_until and user.locked_until > datetime.now():
        remaining = int((user.locked_until - datetime.now()).total_seconds() // 60) + 1
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account is currently locked. Try again in {remaining} minute(s)."
        )

    return user