import unittest
from fastapi.testclient import TestClient
from main import app
from data.response_constant import *


class AuthenticateTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_GetUserInfoWithoutToken_ThenReturnsUnauthorized(self):
        # Act
        response = self.client.get("/user-info")

        # Assert
        self.assertEqual(response.status_code, HTTP_UNAUTHORIZED_401)

    def test_RegisterAUser_ThenReturnsCreated(self):
        # Act
        response = self.client.post(
            "/register", json={"username": "test", "password": "test"}
        )

        # Assert
        self.assertEqual(response.status_code, HTTP_CREATED_201)
        user = response.json()

        self.assertEqual(user["username"], "test")
        self.assertTrue("id" in user)
        self.assertTrue("password" not in user)

    def test_GivenARegisteredUser_WhenGetThatUserInfo_ThenReturnsUserInfo(self):
        # Arrange
        response = self.client.post(
            "/register", json={"username": "test-registered-user", "password": "test"}
        )
        registeredUser = response.json()

        # Act
        response = self.client.get(f'/users/{registeredUser["id"]}')

        # Assert
        self.assertEqual(response.status_code, HTTP_OK_200)
        user = response.json()

        self.assertEqual(user["username"], registeredUser["username"])
        self.assertTrue(user["id"], registeredUser["id"])
        self.assertTrue("password" not in user)
