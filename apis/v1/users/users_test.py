import unittest
from fastapi.testclient import TestClient
from main import app
from data.response_constant import *
from utils.database.database import SessionLocal
from .user_model import User
from .routes import *


class AuthenticateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app, base_url=f"http://test{USER_ROUTE}")
        cls.testUserJson = {"username": "test", "password": "test"}
        cls.registeredUser = cls.client.post(
            REGISTER_ROUTE,
            json=cls.testUserJson,
        ).json()

    def setUp(self):
        pass

    def _GetAuthorizationHeader(self, token: str):
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def _ClearDatabase():
        db = SessionLocal()
        db.query(User).delete()
        db.commit()
        db.close()

    @classmethod
    def tearDownClass(cls) -> None:
        AuthenticateTest._ClearDatabase()

    def test_GetUserInfoWithoutToken_ThenReturnsUnauthorized(self):
        # Act
        response = self.client.get(USER_INFO_ROUTE)

        # Assert
        self.assertEqual(response.status_code, HTTP_UNAUTHORIZED_401)

    def test_GivenARegisteredUser_WhenGetThatUserInfo_ThenReturnsUserInfo(self):
        # Act
        response = self.client.get(f'{self.registeredUser["id"]}')

        print(response.content)

        # Assert
        self.assertEqual(response.status_code, HTTP_OK_200)
        user = response.json()

        self.assertEqual(user["username"], self.registeredUser["username"])
        self.assertTrue(user["id"], self.registeredUser["id"])
        self.assertTrue("password" not in user)

    def test_WhenRegisterAUserWithExistedUsername_ThenReturnsConflict(self):
        # Act
        response = self.client.post(
            REGISTER_ROUTE,
            json=self.testUserJson,
        )

        # Assert
        self.assertEqual(response.status_code, HTTP_CONFLICT_409)

    def test_WhenGetUserWithNonExistedId_ThenReturnsNotFound(self):
        # Act
        response = self.client.get("/4365")

        # Assert
        self.assertEqual(response.status_code, HTTP_NOT_FOUND_404)

    def test_GivenAUserIsRegistered_WhenLogin_ThenReceiveToken(self):
        # Act
        response = self.client.post(
            LOGIN_ROUTE,
            json=self.testUserJson,
        )

        # Assert
        self.assertEqual(response.status_code, HTTP_OK_200)
        token = response.json()
        self.assertTrue(token is not None)
        res = self.client.get(
            USER_INFO_ROUTE,
            headers=self._GetAuthorizationHeader(token=token["access_token"]),
        )

        self.assertEqual(res.status_code, HTTP_OK_200)
        self.assertEqual(res.json()["username"], self.testUserJson["username"])

    def test_WhenLoginWithInvalidPassword_ThenReturnsUnauthorized(self):
        # Act
        response = self.client.post(
            LOGIN_ROUTE,
            json={
                "username": self.testUserJson["username"],
                "password": "invalid-password",
            },
        )

        # Assert
        self.assertEqual(response.status_code, HTTP_UNAUTHORIZED_401)

    def test_WhenLoginWithInvalidUsername_ThenReturnsNotFound(self):
        # Act
        response = self.client.post(
            LOGIN_ROUTE,
            json={
                "username": "invalid-username",
                "password": self.testUserJson["password"],
            },
        )

        # Assert
        self.assertEqual(response.status_code, HTTP_NOT_FOUND_404)

    def test_WhenQueryTheInfoWithInvalidToken_ThenReturnsUnauthorized(self):
        # Act
        response = self.client.get(
            USER_INFO_ROUTE,
            headers=self._GetAuthorizationHeader(token="invalid-token"),
        )

        # Assert
        self.assertEqual(response.status_code, HTTP_UNAUTHORIZED_401)
