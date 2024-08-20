from config import initialize_config, get_config
import os

initialize_config()
config = get_config()

dbURL = config.Get("dbURL", "db.db")

if os.path.exists(dbURL):
    print("Main database exists, removing...")
    os.remove(dbURL)

testDbURL = config.Get("testDbURL", "sqlite:///./test-db.db")

if os.path.exists(testDbURL):
    print("Test database exists, removing...")
    os.remove(testDbURL)

from utils.database.database import Base, engine
from apis.v1.users.user_model import User

print("Creating tables main database...")
Base.metadata.create_all(bind=engine)

from utils.database.t_database import engine

print("Creating tables test database...")
Base.metadata.create_all(bind=engine)

import requests

print("Initializing admin user...")
host = config.Get("host", "localhost")
port = config.Get("port", 8888)
response = requests.post(
    f"http://{host}:{port}/users/register",
    json={"username": "admin", "password": "admin"},
)
