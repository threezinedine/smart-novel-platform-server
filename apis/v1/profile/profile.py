from fastapi import APIRouter, HTTPException
from utils.database.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from apis.v1.users.token_handler import get_current_user
from apis.v1.users.user_model import User
from data.response_constant import *

from .profile_schemas import ProfileSchema
from .profile_model import Profile

router = APIRouter(
    prefix="/api/profiles",
    tags=["profile"],
)


@router.get(
    "/",
    response_model=ProfileSchema,
    status_code=HTTP_OK_200,
)
def read_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileSchema:
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()

    if profile is None:
        raise HTTPException(
            status_code=HTTP_NOT_FOUND_404,
            detail="Profile not found",
        )

    return profile


@router.put(
    "/",
    response_model=ProfileSchema,
    status_code=HTTP_OK_200,
)
def update_profile(
    profileInfo: ProfileSchema,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileSchema:
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()

    if profile is None:
        raise HTTPException(
            status_code=HTTP_NOT_FOUND_404,
            detail="Profile not found",
        )

    profile.email = profileInfo.email
    profile.first_name = profileInfo.first_name
    profile.last_name = profileInfo.last_name
    profile.phone = profileInfo.phone
    profile.address = profileInfo.address
    profile.avatar_url = profileInfo.avatar_url

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_INTERNAL_SERVER_ERROR_500,
            detail=str(e),
        )

    return profile


@router.get(
    "/validate-email",
    response_model=ProfileSchema,
    status_code=HTTP_OK_200,
)
def validate_email(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileSchema:
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    profile.email_verified = True

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_INTERNAL_SERVER_ERROR_500,
            detail=str(e),
        )

    return profile
