from config import initialize_config, get_config
import os
import argparse
import datetime

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

if os.path.exists("db.db"):
    print("Main database exists, removing...")
    os.remove("db.db")

testDbURL = config.Get("testDbURL", "sqlite:///./test-db.db")

if os.path.exists("test_database.db"):
    print("Test database exists, removing...")
    os.remove("test_database.db")

from utils.database.database import Base, engine
from apis.v1.users.user_model import User
from apis.v1.profile.profile_model import Profile

print("Creating tables main database...")
Base.metadata.create_all(bind=engine)

from utils.database.t_database import engine

print("Creating tables test database...")
Base.metadata.create_all(bind=engine)

# create admin user
from utils.database.database import SessionLocal
from apis.v1.users.token_handler import get_password_hash

db = SessionLocal()
admin = User(
    username="admin",
    role="admin",
    hashed_password=get_password_hash("admin"),
)
admin_profile = Profile(
    user=admin,
    first_name="admin",
    last_name="admin",
    email="admin.three@gmail.com",
)
db.add(admin)
db.add(admin_profile)

normal = User(
    username="threezinedine",
    role="user",
    hashed_password=get_password_hash("threezinedine"),
)

normal_profile = Profile(
    user=normal,
    first_name="Zinedine",
    last_name="Zidane",
    email="threezinedine@gmail.com",
)

db.add(normal)
db.add(normal_profile)

try:
    db.commit()
except Exception as e:
    db.rollback()
    print(e)
