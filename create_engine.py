from config import initialize_config, get_config
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--dev",
    "-D",
    action="store_true",
    help="Run in development mode",
)

args = parser.parse_args()

initialize_config(args.dev)
config = get_config()

dbURL = config.Get("dbURL", "db.db")
print(f"Databases: {dbURL}")

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

# create admin user
from utils.database.database import SessionLocal
from apis.v1.users.token_handler import get_password_hash

db = SessionLocal()
admin = User(username="admin", role="admin", hashed_password=get_password_hash("admin"))
db.add(admin)

normal = User(
    username="threezinedine",
    role="user",
    hashed_password=get_password_hash("threezinedine"),
)

db.add(normal)

try:
    db.commit()
except Exception as e:
    db.rollback()
    print(e)
