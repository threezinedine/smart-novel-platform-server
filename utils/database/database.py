from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from config import get_config

config = get_config()

print("Data base URL: ", config.Get("dbURL", "sqlite:///./test-db.db"))
engine = create_engine(
    config.Get("dbURL", "db.db"),
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
