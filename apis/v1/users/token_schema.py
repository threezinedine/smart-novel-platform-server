from pydantic import BaseModel
from enum import Enum


class Role(str, Enum):
    admin = "admin"
    user = "user"


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class TokenDataSchema(BaseModel):
    username: str = None
    role: Role = Role.user
