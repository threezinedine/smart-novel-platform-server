import datetime
from pydantic import BaseModel


class TodoSchema(BaseModel):
    id: int
    title: str
    description: str
    date: datetime.date
    completed: bool = False
