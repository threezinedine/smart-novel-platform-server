from datetime import date
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from routes import *
from models import *
from utils.database.database import *
from sqlalchemy.orm import Session
from sqlalchemy import delete
from utils.authen.token_handler import get_current_user
from data.response_constant import *

from .todo_schema import *
from .planned_todo_schema import *
from .todo_order_schema import *

router = APIRouter(
    prefix=TODO_BASE_ROUTE,
    tags=["todos"],
)


@router.get(GET_REMAIN_TODOS_ROUTE, response_model=List[TodoSchema])
def get_remain_todos(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TodoSchema]:
    today = datetime.datetime.today().date()

    todos = (
        db.query(Todo)
        .filter(
            Todo.completed == False,
            Todo.user_id == user.id,
            Todo.date <= today,
        )
        .all()
    )

    return todos


@router.get(GET_ALL_PLANNED_TODOS_ROUTE, response_model=List[PlannedTodoSchema])
def get_all_planned_todos(
    user: User = Depends(get_current_user),
) -> List[TodoSchema]:
    return user.plannedTodos


@router.post(ADD_PLANNED_TODO_ROUTE, response_model=PlannedTodoSchema)
def add_planned_todo(
    planned_todo_info: PlannedTodoSchema,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TodoSchema:
    planned_todo = PlannedTodo.Create(user.id, planned_todo_info)
    db.add(planned_todo)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_INTERNAL_SERVER_ERROR_500,
            detail=str(e),
        )
    return planned_todo


@router.get(GET_PLANNED_TODO_ROUTE, response_model=PlannedTodoSchema)
def get_planned_todo(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PlannedTodoSchema:
    planned_todo = db.query(PlannedTodo).filter(PlannedTodo.id == id).first()

    if planned_todo is None:
        raise HTTPException(
            status_code=HTTP_NOT_FOUND_404,
            detail="Planned todo not found",
        )

    if planned_todo.user_id != user.id:
        raise HTTPException(
            status_code=HTTP_FORBIDDEN_403,
            detail="You are not authorized to access this planned todo",
        )

    return planned_todo


@router.put(UPDATE_PLANNED_TODO_ROUTE, response_model=PlannedTodoSchema)
def update_planned_todo(
    id: int,
    planned_todo_info: PlannedTodoSchema,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    planned_todo = db.query(PlannedTodo).filter(PlannedTodo.id == id).first()

    if planned_todo is None:
        raise HTTPException(
            status_code=HTTP_NOT_FOUND_404,
            detail="Planned todo not found",
        )

    if planned_todo.user_id != user.id:
        raise HTTPException(
            status_code=HTTP_FORBIDDEN_403,
            detail="You are not authorized to access this planned todo",
        )

    planned_todo.Update(planned_todo_info)

    # delete all planned todo created which the date is not today
    for todo_created in planned_todo.todo_created:
        if todo_created.date > datetime.datetime.today().date():
            db.delete(todo_created.todo)
            db.delete(todo_created)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_INTERNAL_SERVER_ERROR_500,
            detail=str(e),
        )

    return planned_todo


@router.delete(DELETE_PLANNED_TODO_ROUTE)
def delete_planned_todo(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    planned_todo = db.query(PlannedTodo).filter(PlannedTodo.id == id).first()

    if planned_todo is None:
        raise HTTPException(
            status_code=HTTP_NOT_FOUND_404,
            detail="Planned todo not found",
        )

    if planned_todo.user_id != user.id:
        raise HTTPException(
            status_code=HTTP_FORBIDDEN_403,
            detail="You are not authorized to access this planned todo",
        )

    db.delete(planned_todo)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_INTERNAL_SERVER_ERROR_500,
            detail=str(e),
        )

    return {"message": "Planned todo deleted successfully"}


@router.get(GET_TODO_INFO_ROUTE, response_model=TodoSchema)
def get_todo_info(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TodoSchema:
    todo = db.query(Todo).filter(Todo.id == id).first()

    if todo is None:
        raise HTTPException(
            status_code=HTTP_NOT_FOUND_404,
            detail="Todo not found",
        )

    if todo.user_id != user.id:
        raise HTTPException(
            status_code=HTTP_FORBIDDEN_403,
            detail="You are not authorized to access this todo",
        )

    return todo


@router.post(ADD_TODO_ROUTE, response_model=TodoSchema)
def add_todo(
    todo_info: TodoSchema,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TodoSchema:
    todo = Todo.Create(user.id, todo_info)
    db.add(todo)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_INTERNAL_SERVER_ERROR_500,
            detail=str(e),
        )
    return todo


@router.get(GET_TODOS_BY_DATE_ROUTE, response_model=List[TodoSchema])
def get_todo_by_date(
    date: date,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TodoSchema]:
    planned_tods: List[PlannedTodo] = user.plannedTodos

    for planned_todo in planned_tods:
        numCreated = planned_todo.NeedCreated(date)

        if numCreated == -1:
            continue

        for _ in range(numCreated):
            todoInfo = TodoSchema(
                id=0,
                title=planned_todo.title,
                description=planned_todo.description,
                date=date,
            )
            todo = Todo.Create(user.id, todoInfo)
            db.add(todo)
            todoCreated = PlannedTodoCreated.Create(planned_todo, todo, date)
            db.add(todoCreated)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_INTERNAL_SERVER_ERROR_500,
            detail=str(e),
        )

    todos = db.query(Todo).filter(Todo.date == date, Todo.user_id == user.id).all()

    return todos


@router.put(UPDATE_TODO_ROUTE, response_model=TodoSchema)
def update_todo(
    id: int,
    todo_info: TodoSchema,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    todo = db.query(Todo).filter(Todo.id == id).first()

    if todo is None:
        raise HTTPException(
            status_code=HTTP_NOT_FOUND_404,
            detail="Todo not found",
        )

    if todo.user_id != user.id:
        raise HTTPException(
            status_code=HTTP_FORBIDDEN_403,
            detail="You are not authorized to access this todo",
        )

    todo.Update(todo_info)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_INTERNAL_SERVER_ERROR_500,
            detail=str(e),
        )

    return todo


@router.put(COMPLETE_TODO_ROUTE, response_model=TodoSchema)
def complete_todo(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TodoSchema:
    todo = db.query(Todo).filter(Todo.id == id).first()

    if todo is None:
        raise HTTPException(
            status_code=HTTP_NOT_FOUND_404,
            detail="Todo not found",
        )

    if todo.user_id != user.id:
        raise HTTPException(
            status_code=HTTP_FORBIDDEN_403,
            detail="You are not authorized to access this todo",
        )

    todo.Complete()

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_INTERNAL_SERVER_ERROR_500,
            detail=str(e),
        )

    return todo


@router.put(UNCOMPLETE_TODO_ROUTE, response_model=TodoSchema)
def uncomplete_todo(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TodoSchema:
    todo = db.query(Todo).filter(Todo.id == id).first()

    if todo is None:
        raise HTTPException(
            status_code=HTTP_NOT_FOUND_404,
            detail="Todo not found",
        )

    if todo.user_id != user.id:
        raise HTTPException(
            status_code=HTTP_FORBIDDEN_403,
            detail="You are not authorized to access this todo",
        )

    todo.Uncomplete()

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_INTERNAL_SERVER_ERROR_500,
            detail=str(e),
        )

    return todo


@router.delete(DELETE_TODO_ROUTE)
def delete_todo(
    id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    todo = db.query(Todo).filter(Todo.id == id).first()

    if todo is None:
        raise HTTPException(
            status_code=HTTP_NOT_FOUND_404,
            detail="Todo not found",
        )

    if todo.user_id != user.id:
        raise HTTPException(
            status_code=HTTP_FORBIDDEN_403,
            detail="You are not authorized to access this todo",
        )

    db.delete(todo)
    db.commit()

    return {"message": "Todo deleted successfully"}


@router.delete(CLEAN_TODOS_BY_DATE_ROUTE)
def clean_todos_by_date(
    date: date,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = delete(Todo).where(Todo.date == date, Todo.user_id == user.id)

    try:
        db.execute(stmt)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_INTERNAL_SERVER_ERROR_500,
            detail=str(e),
        )

    return {}


@router.get(GET_TODOS_ORDER_ROUTE_BY_DATE, response_model=TodoOrderSchema)
def get_todo_orders(
    date: date,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    todo_order = (
        db.query(TodoOrder)
        .filter(TodoOrder.date == date, TodoOrder.user_id == user.id)
        .first()
    )

    if todo_order is None:
        todos = db.query(Todo).filter(Todo.date == date, Todo.user_id == user.id).all()
        return TodoOrderSchema(orders=[todo.id for todo in todos])
    else:
        return TodoOrderSchema(orders=[int(id) for id in todo_order.order.split(",")])


@router.put(UPDATE_TODOS_ORDER_ROUTE, response_model=TodoOrderSchema)
def update_todo_orders(
    date: date,
    orderSchema: TodoOrderSchema,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    todo_order = (
        db.query(TodoOrder)
        .filter(TodoOrder.date == date, TodoOrder.user_id == user.id)
        .first()
    )

    if todo_order is None:
        todo_order = TodoOrder.Create(user, date, orderSchema.orders)
        db.add(todo_order)
    else:
        todo_order.Update(orderSchema.orders)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=HTTP_INTERNAL_SERVER_ERROR_500,
            detail=str(e),
        )

    return orderSchema
