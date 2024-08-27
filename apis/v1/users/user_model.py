from sqlalchemy import Column, Integer, String, Boolean
from utils.database.database import Base
from .token_models import Role


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, index=True)
    role = Column(String(10), default=Role.user.value)
    hashed_password = Column(String(255))
