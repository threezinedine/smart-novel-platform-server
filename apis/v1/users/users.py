from fastapi.responses import JSONResponse
from fastapi import Depends
from sqlalchemy.orm import Session
from data.response_constant import *
from .request_user_model import RegisterUser
from .user_info_model import UserInfo
from .user_model import User
from utils.database.database import get_db
from .token_handler import *
from .token_models import Token, TokenData
from fastapi import APIRouter
from .routes import *
from config import get_config
from utils.configure.configure import Configure
from .token_models import Role

router = APIRouter(
    prefix=USER_ROUTE,
    tags=["users"],
)


@router.get(
    USER_INFO_ROUTE,
    response_model=TokenData,
    status_code=HTTP_OK_200,
)
def get_user(
    current_user=Depends(get_current_user),
):
    return current_user


@router.post(
    REGISTER_ROUTE,
    response_model=UserInfo,
    status_code=HTTP_CREATED_201,
)
def register_user(
    user_info: RegisterUser,
    db: Session = Depends(get_db),
) -> UserInfo:
    existedUser = db.query(User).filter(User.username == user_info.username).first()

    if existedUser is not None:
        return JSONResponse(
            status_code=HTTP_CONFLICT_409,
            content={"message": "Username is already taken"},
        )

    returned_user = User(
        username=user_info.username,
        hashed_password=get_password_hash(user_info.password),
    )

    db.add(returned_user)

    try:
        db.commit()
        db.refresh(returned_user)
        return returned_user
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=HTTP_BAD_REQUEST_400,
            content={"message": e},
        )


@router.get(
    "/{user_id}",
    response_model=UserInfo,
    status_code=HTTP_OK_200,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserInfo:
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        return JSONResponse(
            status_code=HTTP_NOT_FOUND_404, content={"message": "User not found"}
        )
    return user


@router.post(
    LOGIN_ROUTE,
    response_model=Token,
    status_code=HTTP_OK_200,
)
def login(
    userInfo: RegisterUser,
    db: Session = Depends(get_db),
    config: Configure = Depends(get_config),
):
    user = db.query(User).where(User.username == userInfo.username).first()

    if user is None:
        return JSONResponse(
            status_code=HTTP_NOT_FOUND_404,
            content={"message": "User not found"},
        )

    if not verify_password(userInfo.password, user.hashed_password):
        return JSONResponse(
            status_code=HTTP_UNAUTHORIZED_401,
            content={"message": "Incorrect password"},
        )

    access_token_expires = timedelta(minutes=config.Get("expiresMinutes", 15))
    access_token = create_access_token(
        data={"username": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )


@router.post(
    EXPIRES_TOKEN_ROUTE,
    response_model=Token,
    status_code=HTTP_OK_200,
)
def get_expires_token(userInfo: RegisterUser):
    access_token = create_access_token(
        data={"username": userInfo.username}, expires_delta=timedelta(minutes=-1)
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
    )


@router.post(
    REGISTER_ADMIN_ROUTE,
    response_model=UserInfo,
    status_code=HTTP_CREATED_201,
)
def register_admin_user(
    userInfo: RegisterUser,
    db: Session = Depends(get_db),
    config: Configure = Depends(get_config),
):
    if not config.IsOverriden():
        return JSONResponse(
            status_code=HTTP_FORBIDDEN_403,
            content={"message": "Cannot use this route in production mode"},
        )

    returned_user = User(
        username=userInfo.username,
        hashed_password=get_password_hash(userInfo.password),
        role=Role.admin,
    )

    db.add(returned_user)

    try:
        db.commit()
        db.refresh(returned_user)
        return returned_user
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=HTTP_BAD_REQUEST_400,
            content={"message": e},
        )
