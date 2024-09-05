import datetime
from utils.database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    email = Column(String(100), nullable=True)
    email_verified = Column(Boolean, default=False)

    first_name = Column(String(40), nullable=True)
    last_name = Column(String(40), nullable=True)
    phone = Column(String(10), nullable=True)
    address = Column(String(100), nullable=True)
    avatar_url = Column(String(1000), nullable=True)

    last_updated_at = Column(DateTime, default=datetime.datetime.now)

    user = relationship("User", back_populates="profile")
