from .routes import *

TODO_BASE_ROUTE = f"{BASE_ROUTE}/todos"

# todo retrieval (both instance of the regular todo is included)
GET_TODOS_BY_DATE_ROUTE = "/date/{date}"
GET_REMAIN_TODOS_ROUTE = "/remain"

# todo crud
GET_TODO_INFO_ROUTE = "/{id}"
ADD_TODO_ROUTE = "/"
UPDATE_TODO_ROUTE = "/{id}"  # change the information only, not complete status
COMPLETE_TODO_ROUTE = "/{id}/complete"
UNCOMPLETE_TODO_ROUTE = "/{id}/uncomplete"
DELETE_TODO_ROUTE = "/{id}"

# planned todos crud, which is automatically created each day
GET_ALL_PLANNED_TODOS_ROUTE = "/planned"
GET_PLANNED_TODO_ROUTE = "/planned/{id}"

ADD_PLANNED_TODO_ROUTE = "/planned"
UPDATE_PLANNED_TODO_ROUTE = "/planned/{id}"
DELETE_PLANNED_TODO_ROUTE = "/planned/{id}"

# clean remaining todos
CLEAN_TODOS_BY_DATE_ROUTE = "/clean/{date}"

# todo order routes
GET_TODOS_ORDER_ROUTE_BY_DATE = "/order/{date}"  # return ids of todos in order

UPDATE_TODOS_ORDER_ROUTE = "/order/{date}"  # param: order: [id1, id2, ...]
