from typing import List
from pydantic import BaseModel


class TodoOrderSchema(BaseModel):
    orders: List[int]
