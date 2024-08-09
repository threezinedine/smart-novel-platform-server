from utils.database.database import Base, engine
from apis.v1.authenticate.user import User

Base.metadata.create_all(bind=engine)
