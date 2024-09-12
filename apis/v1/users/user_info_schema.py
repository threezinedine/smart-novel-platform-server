from pydantic import BaseModel


class UserInfoSchema(BaseModel):
    id: int
    username: str
