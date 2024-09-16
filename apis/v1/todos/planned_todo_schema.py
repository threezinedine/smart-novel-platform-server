from pydantic import BaseModel


class PlannedTodoSchema(BaseModel):
    id: int
    title: str
    description: str
    weekdays: str = "Mon"
    gapWeek: int = 1
    numTodos: int = 1
