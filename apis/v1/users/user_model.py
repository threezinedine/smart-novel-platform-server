import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from utils.database.database import Base
from .token_models import Role


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, index=True)
    role = Column(String(10), default=Role.user.value)
    hashed_password = Column(String(255))

    created_at = Column(DateTime, default=datetime.datetime.now)
    last_updated = Column(DateTime, default=datetime.datetime.now)

    profile = relationship("Profile", back_populates="user", uselist=False)
