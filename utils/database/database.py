from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
