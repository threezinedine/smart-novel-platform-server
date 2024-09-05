from pydantic import BaseModel, ConfigDict


class ProfileSchema(BaseModel):
    email: str | None
    email_verified: bool
    first_name: str | None
    last_name: str | None
    phone: str | None
    address: str | None
    avatar_url: str | None

    model_config = ConfigDict(from_attributes=True)
