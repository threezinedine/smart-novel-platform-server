from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import get_config, initialize_config


initialize_config()
config = get_config()


engine = create_engine(
    config.Get("testDbURL", "sqlite:///./test-db.db"),
    connect_args={"check_same_thread": False},
)

TessingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TessingSessionLocal()
    try:
        yield db
    finally:
        db.close()
