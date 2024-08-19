import unittest
from test import app
from fastapi.testclient import TestClient
from utils.database.t_database import TessingSessionLocal as SessionLocal
from .user_model import User
from .routes import *
from data.response_constant import *


class RegisterTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app, base_url=f"http://test{USER_ROUTE}")
        self.testUserJson = {"username": "test", "password": "test"}

    def _GetAuthorizationHeader(self, token: str):
        return {"Authorization": f"Bearer {token}"}

    def tearDown(self) -> None:
        db = SessionLocal()
        db.query(User).delete()
        db.commit()
        db.close()

    def test_RegisterAUser_ThenReturnsCreated(self):
        # Act
        response = self.client.post(REGISTER_ROUTE, json=self.testUserJson)

        # Assert
        self.assertEqual(response.status_code, HTTP_CREATED_201)
        user = response.json()

        self.assertEqual(user["username"], "test")
        self.assertTrue("id" in user)
        self.assertTrue("password" not in user)
