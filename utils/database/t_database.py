from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


SQL_BASE_URL = "sqlite:///./test-3.db"

engine = create_engine(SQL_BASE_URL, connect_args={"check_same_thread": False})

TessingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TessingSessionLocal()
    try:
        yield db
    finally:
        db.close()
