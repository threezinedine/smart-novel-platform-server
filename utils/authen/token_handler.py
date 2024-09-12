import jwt
from typing import Optional, Union
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from models import User
from fastapi import Depends, HTTPException
from data.response_constant import *
from sqlalchemy.orm import Session
from utils.database.database import get_db

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oath2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None]):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oath2_scheme)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("username")
        if username is None:
            raise HTTPException(
                status_code=HTTP_UNAUTHORIZED_401,
                detail="Token does not contain username",
            )

        expire_time = payload.get("exp")
        if expire_time is None:
            raise HTTPException(
                status_code=HTTP_UNAUTHORIZED_401,
                detail="Token does not contain expire time",
            )

    except Exception as e:
        raise HTTPException(status_code=HTTP_UNAUTHORIZED_401, detail=f"Error: {e}")
    user = get_user(db, username)
    if user is None:
        raise HTTPException(
            status_code=HTTP_UNAUTHORIZED_401,
            detail="User not found",
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
