import unittest
from utils.database.t_database import override_get_db, engine
from utils.database.database import get_db, Base
from fastapi.testclient import TestClient
from main import app
from apis.v1.users.user_model import User

app.dependency_overrides[get_db] = override_get_db

if __name__ == "__main__":
    unittest.main()
