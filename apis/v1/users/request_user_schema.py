from pydantic import BaseModel


class RegisterUserSchema(BaseModel):
    username: str
    password: str
