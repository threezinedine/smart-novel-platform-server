from utils.database.database import Base, engine
from apis.v1.users.user_model import User

Base.metadata.create_all(bind=engine)
