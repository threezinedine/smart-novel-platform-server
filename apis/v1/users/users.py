from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from data.response_constant import *
from models import *
from utils.database.database import get_db
from config import get_config, Configure

from .token_schema import Role
from routes import *
from .request_user_schema import RegisterUserSchema
from .user_info_schema import UserInfoSchema
from utils.authen.token_handler import *
from .token_schema import TokenSchema, TokenDataSchema

router = APIRouter(
    prefix=USER_BASE_ROUTE,
    tags=["users"],
)


@router.get(
    GET_USER_INFO_ROUTE,
    response_model=TokenDataSchema,
    status_code=HTTP_OK_200,
)
def get_user(
    current_user=Depends(get_current_user),
):
    return current_user


@router.post(
    REGISTER_ROUTE,
    response_model=UserInfoSchema,
    status_code=HTTP_CREATED_201,
)
def register_user(
    user_info: RegisterUserSchema,
    db: Session = Depends(get_db),
) -> UserInfoSchema:
    existedUser = db.query(User).filter(User.username == user_info.username).first()

    if existedUser is not None:
        raise HTTPException(
            status_code=HTTP_CONFLICT_409,
            detail={"message": "Username is already taken"},
        )

    returned_user = User(
        username=user_info.username,
        hashed_password=get_password_hash(user_info.password),
    )

    profile = Profile(user=returned_user)

    db.add(returned_user)
    db.add(profile)

    try:
        db.commit()
        db.refresh(returned_user)
        return returned_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_BAD_REQUEST_400,
            detail={"message": e},
        )


@router.get(
    "/{user_id}",
    response_model=UserInfoSchema,
    status_code=HTTP_OK_200,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
) -> UserInfoSchema:
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=HTTP_NOT_FOUND_404,
            detail={"message": "User not found"},
        )
    return user


@router.post(
    LOGIN_ROUTE,
    response_model=TokenSchema,
    status_code=HTTP_OK_200,
)
def login(
    userInfo: RegisterUserSchema,
    db: Session = Depends(get_db),
    config: Configure = Depends(get_config),
):
    user = db.query(User).where(User.username == userInfo.username).first()

    if user is None:
        raise HTTPException(
            status_code=HTTP_NOT_FOUND_404,
            detail={"message": "User not found"},
        )

    if not verify_password(userInfo.password, user.hashed_password):
        raise HTTPException(
            status_code=HTTP_UNAUTHORIZED_401,
            detail={"message": "Incorrect password"},
        )

    access_token_expires = timedelta(minutes=config.Get("expiresMinutes", 15))
    access_token = create_access_token(
        data={"username": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )

    return TokenSchema(
        access_token=access_token,
        token_type="bearer",
    )


@router.post(
    GET_USER_INFO_ROUTE,
    response_model=TokenSchema,
    status_code=HTTP_OK_200,
)
def get_expires_token(userInfo: RegisterUserSchema):
    access_token = create_access_token(
        data={"username": userInfo.username}, expires_delta=timedelta(minutes=-1)
    )

    return TokenSchema(
        access_token=access_token,
        token_type="bearer",
    )


@router.post(
    REGISTER_ADMIN_ROUTE,
    response_model=UserInfoSchema,
    status_code=HTTP_CREATED_201,
)
def register_admin_user(
    userInfo: RegisterUserSchema,
    db: Session = Depends(get_db),
    config: Configure = Depends(get_config),
):
    if not config.IsOverriden():
        raise HTTPException(
            status_code=HTTP_FORBIDDEN_403,
            detail={"message": "Cannot use this route in production mode"},
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
        raise HTTPException(
            status_code=HTTP_BAD_REQUEST_400,
            detail={"message": e},
        )
