from utils.database.database import Base, engine, SessionLocal
from apis.v1.users.user_model import User

Base.metadata.create_all(bind=engine)
