import unittest
from apis.v1.profile.profile_schemas import ProfileSchema
from test_app import app
from fastapi.testclient import TestClient
from utils.database.t_database import TessingSessionLocal as SessionLocal
from apis.v1.profile.profile_model import Profile
from apis.v1.users.user_model import User

from data.response_constant import *


class ProfileTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app, base_url=f"http://test/api")

        self.client.post(
            "/users/register",
            json={"username": "test", "password": "test"},
        )

        self.token = self.client.post(
            "/users/login",
            json={"username": "test", "password": "test"},
        ).json()["access_token"]

    def _Get(self, url: str, **kwargs):
        return self.client.get(
            url,
            headers={"Authorization": f"Bearer {self.token}"},
            **kwargs,
        )

    def _Put(self, url: str, **kwargs):
        return self.client.put(
            url,
            headers={"Authorization": f"Bearer {self.token}"},
            **kwargs,
        )

    def tearDown(self) -> None:
        db = SessionLocal()
        db.query(User).delete()
        db.query(Profile).delete()
        db.commit()
        db.close()

    def _AssertProfileSchemaEqual(self, srcProfile, expectedProfile: ProfileSchema):
        self.assertEqual(srcProfile["email"], expectedProfile.email)
        self.assertEqual(srcProfile["email_verified"], expectedProfile.email_verified)
        self.assertEqual(srcProfile["first_name"], expectedProfile.first_name)
        self.assertEqual(srcProfile["last_name"], expectedProfile.last_name)
        self.assertEqual(srcProfile["phone"], expectedProfile.phone)
        self.assertEqual(srcProfile["address"], expectedProfile.address)
        self.assertEqual(srcProfile["avatar_url"], expectedProfile.avatar_url)

    def test_GetClientProfile(self):
        # Act
        response = self._Get("/profiles")
        print(response)

        # Assert
        self.assertEqual(response.status_code, 200)
        profile = response.json()
        self._AssertProfileSchemaEqual(
            profile,
            Profile(
                email=None,
                email_verified=False,
                first_name=None,
                last_name=None,
                phone=None,
                address=None,
            ),
        )

    def test_UpdateProfile(self):
        # Arrange
        newProfile = {
            "email": "threezinedine@gmail.com",
            "first_name": "Zinedine",
            "last_name": "Zidane",
            "email_verified": True,
            "phone": "1234567890",
            "address": "1234 Main St",
            "avatar_url": "testing",
        }

        # Act
        response = self._Put("/profiles", json=newProfile)

        # Assert
        self.assertEqual(response.status_code, HTTP_OK_200)
        newProfile = response.json()
        expectedProfile = newProfile.copy()
        expectedProfile["email_verified"] = False
        self._AssertProfileSchemaEqual(
            newProfile,
            ProfileSchema(**expectedProfile),
        )

        profile = self._Get("/profiles").json()
        self._AssertProfileSchemaEqual(
            profile,
            ProfileSchema(**expectedProfile),
        )

    def test_ValidateTheEmail(self):
        # Act
        response = self._Get("/profiles/validate-email")

        # Assert
        self.assertEqual(response.status_code, HTTP_OK_200)
        profile = self._Get("/profiles").json()
        self.assertTrue(profile["email_verified"])
