import unittest
from utils.configure.configure import Configure
import os
import json


class ConfigureTest(unittest.TestCase):
    testConfigFile = "test-config.json"
    testConfigData = {
        "host": "localhost",
        "port": 8080,
    }
    nonExistedConfigFile = "non-existed-config.json"

    testOverideConfigFile = "test-override-config.json"
    testOverrideConfigData = {"host": "0.0.0.0"}

    def setUp(self) -> None:
        with open(self.testConfigFile, "w") as file:
            json.dump(self.testConfigData, file)

        with open(self.testOverideConfigFile, "w") as file:
            json.dump(self.testOverrideConfigData, file)

        self.validConfigure = Configure(self.testConfigFile)
        self.validConfigure.Load()

        self.overrideConfigure = Configure(self.testOverideConfigFile)
        self.overrideConfigure.Load()

    def tearDown(self) -> None:
        if os.path.exists(self.testConfigFile):
            os.remove(self.testConfigFile)

        if os.path.exists(self.testOverideConfigFile):
            os.remove(self.testOverideConfigFile)

    def test_GivenConfigure_WhenLoadThatConfigure_ThenTheConfigureIsLoaded(self):
        # Act
        self.validConfigure.Load()

        # Assert
        self.assertEqual(self.validConfigure["host"], self.testConfigData["host"])
        self.assertEqual(self.validConfigure["port"], self.testConfigData["port"])
        self.assertIsNone(self.validConfigure["non-existed-key"])
        self.assertFalse(self.validConfigure.IsOverriden())

    def test_GivenConfigure_WhenGetItem_ThenReturnTheValue(self):
        # Arrange
        # Act
        host = self.validConfigure.Get("host")

        # Assert
        self.assertEqual(host, self.testConfigData["host"])

    def test_GivenConfigure_WhenGetNonExistedItemWithDefaultValue_ThenReturnTheDefaultValue(
        self,
    ) -> None:
        # Arrange
        defaultValue = "default-value"

        # Act
        nonExistedItem = self.validConfigure.Get("non-existed-item", defaultValue)

        # Assert
        self.assertEqual(nonExistedItem, defaultValue)

    def test_GivenConfigure_WhenIsOverridenByAnotherConfigure_ThenTheValueIsOverridden(
        self,
    ):
        # Act
        self.validConfigure.OverridenBy(self.overrideConfigure)

        # Assert
        self.assertEqual(
            self.validConfigure["host"], self.testOverrideConfigData["host"]
        )
        self.assertEqual(self.validConfigure["port"], self.testConfigData["port"])
        self.assertTrue(self.validConfigure.IsOverriden())
