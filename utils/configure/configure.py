from typing import Optional, TypeVar
import os
import json

T = TypeVar("T")


class Configure:
    def __init__(self, configFile: str) -> None:
        self.__configFile: str = configFile
        self.__overridenConfigure: Optional["Configure"] = None
        self.__data: dict = {}

    def Load(self) -> None:
        if not os.path.exists(self.__configFile):
            return

        with open(self.__configFile, "r") as file:
            self.__data = json.loads(file.read())

    def Get(self, key: str, defaut: Optional[T] = None) -> Optional[T]:
        return self[key] if self.Contains(key) else defaut

    def Contains(self, key: str) -> bool:
        return key in self.__data

    def __getitem__(self, key: str) -> Optional[object]:
        if self.__overridenConfigure and self.__overridenConfigure.Contains(key):
            return self.__overridenConfigure[key]
        return self.__data.get(key)

    def OverridenBy(self, overrideConfigure: "Configure") -> None:
        self.__overridenConfigure = overrideConfigure

    def IsOverriden(self) -> bool:
        return self.__overridenConfigure is not None

    def __repr__(self) -> str:
        return f"<Configure data={json.dumps(self.__data)} />"
