from fastapi import APIRouter, HTTPException, Depends
from utils.database.database import get_db
from sqlalchemy.orm import Session
from utils.authen.token_handler import get_current_user
from models import *
from data.response_constant import *

from .profile_schemas import ProfileSchema
from routes import *

router = APIRouter(
    prefix=PROFLIE_BASE_ROUTE,
    tags=["profile"],
)


@router.get(
    GET_PROFILE_ROUTE,
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
    UPDATE_PROFILE_ROUTE,
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

    profile.Update(profileInfo)

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
    VALIDATE_EMAIL_ROUTE,
    response_model=ProfileSchema,
    status_code=HTTP_OK_200,
)
def validate_email(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileSchema:
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()

    profile.VerifyEmail()

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_INTERNAL_SERVER_ERROR_500,
            detail=str(e),
        )

    return profile
