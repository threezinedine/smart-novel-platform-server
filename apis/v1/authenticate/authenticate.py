from main import app
from fastapi.responses import JSONResponse
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from data.response_constant import *
from .request_user_model import RegisterUser
from .user_info_model import UserInfo
from .user import User
from utils.database.database import get_db


@app.get("/user-info")
async def get_user():
    return JSONResponse(status_code=401, content={"message": "Unauthorized"})


@app.post("/register", response_model=UserInfo, status_code=HTTP_CREATED_201)
def register_user(user_info: RegisterUser, db: Session = Depends(get_db)) -> UserInfo:
    returned_user = User(username=user_info.username)

    db.add(returned_user)

    try:
        db.commit()
        db.refresh(returned_user)
        return returned_user
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=HTTP_BAD_REQUEST_400, content={"message": e})


@app.get("/users/{user_id}", response_model=UserInfo, status_code=HTTP_OK_200)
def get_user(user_id: str, db: Session = Depends(get_db)) -> UserInfo:
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        return JSONResponse(
            status_code=HTTP_NOT_FOUND_404, content={"message": "User not found"}
        )
    return user
