import datetime
from typing import Optional
from utils.database.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Date, DateTime
from sqlalchemy.orm import relationship
from apis.v1.todos.todo_schema import TodoSchema
from apis.v1.todos.planned_todo_schema import PlannedTodoSchema

from utils.date.date_utils import *


class PlannedTodo(Base):
    __tablename__ = "plannedTodos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(100))
    description = Column(String(1000), nullable=True)
    weekdays = Column(
        String(100), nullable=True
    )  # "Mon,Wed,Fri,Sat,Sun" means every Mon, Wed, Fri, Sat, Sun,
    # "Mon,Wed" means every Mon, Wed. Only "Mon", "Tue", "Wed",
    # #"Thu", "Fri", "Sat", "Sun" are valid.
    gapWeek = Column(
        Integer, default=1
    )  # gapWeek = 1 means every week; gapWeek = 2 means every 2 weeks
    numTodos = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)
    last_updated = Column(DateTime, default=datetime.datetime.now)

    user = relationship("User", back_populates="plannedTodos", uselist=False)
    todo_created = relationship(
        "PlannedTodoCreated",
        back_populates="plannedTodo",
        uselist=True,
    )

    @staticmethod
    def Create(user_id: int, planned_todo: PlannedTodoSchema) -> "PlannedTodo":
        return PlannedTodo(
            user_id=user_id,
            title=planned_todo.title,
            description=planned_todo.description,
            weekdays=planned_todo.weekdays,
            gapWeek=planned_todo.gapWeek,
            numTodos=planned_todo.numTodos,
        )

    def Update(self, planned_todo: PlannedTodoSchema):
        self.title = planned_todo.title
        self.description = planned_todo.description
        self.weekdays = planned_todo.weekdays
        self.gapWeek = planned_todo.gapWeek
        self.numTodos = planned_todo.numTodos
        self.last_updated = datetime.datetime.now()

    def NeedCreated(self, date: datetime.date) -> int:
        checkGapWeek = CheckNumberGapWeek(self.created_at.date(), date)

        if checkGapWeek < 0:
            return 0

        if checkGapWeek % self.gapWeek != 0:
            return 0

        if date.strftime("%a") not in self.weekdays:
            return 0

        num_date_created_todos = len(
            [todo for todo in self.todo_created if todo.date == date]
        )

        if num_date_created_todos >= self.numTodos:
            return 0

        return self.numTodos - num_date_created_todos

    def __repr__(self):
        return f"<PlannedTodo {self.title} />"


class PlannedTodoCreated(Base):
    __tablename__ = "plannedTodo_created"

    id = Column(Integer, primary_key=True, index=True)
    todo_id = Column(Integer, ForeignKey("todos.id"))
    planned_todo_id = Column(Integer, ForeignKey("plannedTodos.id"))
    date = Column(Date, default=datetime.datetime.now)

    plannedTodo = relationship(
        "PlannedTodo",
        back_populates="todo_created",
        uselist=False,
    )
    todo = relationship("Todo", back_populates="created_todo", uselist=False)

    @staticmethod
    def Create(
        plannedTodo: PlannedTodo, todo: "Todo", date: datetime.date
    ) -> "PlannedTodoCreated":
        return PlannedTodoCreated(
            date=date,
            todo=todo,
            plannedTodo=plannedTodo,
        )

    def __repr__(self):
        return f"<PlannedTodoCreated {self.planned_todo_id} date={self.date} />"


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(100))
    description = Column(String(1000), nullable=True)
    date = Column(Date, default=datetime.datetime.now)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    last_updated = Column(DateTime, default=datetime.datetime.now)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="todos", uselist=False)
    created_todo = relationship(
        "PlannedTodoCreated",
        back_populates="todo",
        uselist=False,
    )

    @staticmethod
    def Create(
        user_id: int,
        todo: TodoSchema,
    ) -> "Todo":
        return Todo(
            user_id=user_id,
            title=todo.title,
            description=todo.description,
            date=todo.date,
            completed=False,
        )

    def Update(self, todo: TodoSchema):
        self.title = todo.title
        self.description = todo.description
        self.date = todo.date
        self.last_updated = datetime.datetime.now()

    def Complete(self):
        self.completed = True
        self.completed_at = datetime.datetime.now()

    def Uncomplete(self):
        self.completed = False
        self.completed_at = None

    def __repr__(self):
        return f"<Todo {self.title} due={self.date} />"
