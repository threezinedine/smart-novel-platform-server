from utils.database.database import Base
from utils.database.t_database import engine
from apis.v1.users.user_model import User

Base.metadata.create_all(bind=engine)
