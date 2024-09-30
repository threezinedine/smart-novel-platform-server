from typing import List
from datetime import timedelta, datetime
import unittest
from routes import *
from fastapi.testclient import TestClient
from test_app import app
from utils.database.t_database import TessingSessionLocal as SessionLocal
from models import *
from data import *


class TodoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app, base_url=f"http://test")
        cls.userInfo = {"username": "test", "password": "test"}

        cls.client.post(
            f"{USER_BASE_ROUTE}{REGISTER_ROUTE}",
            json=cls.userInfo,
        )

        cls.token = cls.client.post(
            f"{USER_BASE_ROUTE}{LOGIN_ROUTE}",
            json=cls.userInfo,
        ).json()["access_token"]

        cls.client.post(
            f"{USER_BASE_ROUTE}{REGISTER_ROUTE}",
            json={"username": "test2", "password": "test2"},
        )

        cls.token2 = cls.client.post(
            f"{USER_BASE_ROUTE}{LOGIN_ROUTE}",
            json={"username": "test2", "password": "test2"},
        ).json()["access_token"]

    def _GetHeader(self, token: Optional[str] = None) -> dict:
        headers = {}

        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _Get(self, route: str, token: Optional[str] = None):
        return self.client.get(
            route,
            headers=self._GetHeader(self.token if token is None else token),
        )

    def _Post(self, route: str, data: dict):
        return self.client.post(
            route,
            json=data,
            headers=self._GetHeader(self.token),
        )

    def _Put(self, route: str, data: dict = {}, token: Optional[str] = None):
        return self.client.put(
            route,
            json=data,
            headers=self._GetHeader(self.token if token is None else token),
        )

    def _Delete(self, route: str, token: Optional[str] = None):
        return self.client.delete(
            route,
            headers=self._GetHeader(self.token if token is None else token),
        )

    def _AssertTodo(self, todo: dict, other: dict):
        self.assertEqual(todo["title"], other["title"])
        self.assertEqual(todo["description"], other["description"])
        self.assertEqual(todo["date"], other["date"])

    def _AssertPlannedTodo(self, plannedTodo: dict, other: dict):
        self.assertEqual(plannedTodo["title"], other["title"])
        self.assertEqual(plannedTodo["description"], other["description"])
        self.assertEqual(plannedTodo["weekdays"], other["weekdays"])
        self.assertEqual(plannedTodo["gapWeek"], other["gapWeek"])

    def _AssertContains(self, todos: List[dict], todo_id: int):
        existedTodo = list(filter(lambda x: x["id"] == todo_id, todos))
        self.assertEqual(len(existedTodo), 1)

    def _AssertNotContains(self, todos: List[dict], todo_id: int):
        existedTodo = list(filter(lambda x: x["id"] == todo_id, todos))
        self.assertEqual(len(existedTodo), 0)

    def _AssertContainsByTitle(self, todos: List[dict], title: str, num: int = 1):
        existedTodo = list(filter(lambda x: x["title"] == title, todos))
        self.assertEqual(len(existedTodo), num)

    def _AssertNotContainsByTitle(self, todos: List[dict], title: str):
        existedTodo = list(filter(lambda x: x["title"] == title, todos))
        self.assertEqual(len(existedTodo), 0)

    @classmethod
    def tearDownClass(self) -> None:
        db = SessionLocal()
        db.query(User).delete()
        db.query(Profile).delete()
        db.query(Todo).delete()
        db.query(PlannedTodo).delete()
        db.query(PlannedTodoCreated).delete()
        db.query(TodoOrder).delete()
        db.commit()
        db.close()

    def tearDown(self) -> None:
        db = SessionLocal()
        db.query(Todo).delete()
        db.query(PlannedTodo).delete()
        db.query(PlannedTodoCreated).delete()
        db.commit()
        db.close()

    def test_TokenRetrieveById(self) -> None:
        # Act
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_TODO_INFO_ROUTE.format(id=34)}",
        )

        # Assert
        self.assertEqual(response.status_code, HTTP_NOT_FOUND_404)

    def test_CreateTodo(self) -> None:
        # Register the todo
        testTodo = {
            "id": 0,
            "title": "test",
            "description": "test",
            "date": "2022-01-01",
            "complete": True,
        }

        response = self._Post(
            f"{TODO_BASE_ROUTE}{ADD_TODO_ROUTE}",
            data=testTodo,
        )

        # Retrieve the todo
        self.assertEqual(response.status_code, HTTP_OK_200)
        todo = response.json()
        self._AssertTodo(todo, testTodo)
        self.assertFalse(todo["completed"])

        response = self._Get(
            f'{TODO_BASE_ROUTE}/{todo["id"]}',
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self._AssertTodo(response.json(), testTodo)

        # Get todo by other user
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_TODO_INFO_ROUTE.format(id=todo['id'])}",
            self.token2,
        )

        self.assertEqual(response.status_code, HTTP_FORBIDDEN_403)

        # Get all todos by date
        response = self._Get(
            (f"{TODO_BASE_ROUTE}{GET_TODOS_BY_DATE_ROUTE}").format(
                date=testTodo["date"]
            ),
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self._AssertContains(response.json(), todo["id"])

        # other user cannot get the todo
        response = self._Get(
            (f"{TODO_BASE_ROUTE}{GET_TODOS_BY_DATE_ROUTE}").format(
                date=testTodo["date"]
            ),
            self.token2,
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self._AssertNotContains(response.json(), todo["id"])

        # get remain todos then the todo should be included
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_REMAIN_TODOS_ROUTE}",
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self._AssertContains(response.json(), todo["id"])

        # get remain todos by other user then the todo should not be included
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_REMAIN_TODOS_ROUTE}",
            self.token2,
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self._AssertNotContains(response.json(), todo["id"])

        # complete todo with other, nothing has changed
        response = self._Put(
            f"{TODO_BASE_ROUTE}{COMPLETE_TODO_ROUTE.format(id=todo['id'])}",
            {},
            self.token2,
        )

        self.assertEqual(response.status_code, HTTP_FORBIDDEN_403)

        # complete todo then the todo should not be included
        response = self._Put(
            f"{TODO_BASE_ROUTE}{COMPLETE_TODO_ROUTE.format(id=todo['id'])}",
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self.assertTrue(response.json()["completed"])

        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_REMAIN_TODOS_ROUTE}",
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self._AssertNotContains(response.json(), todo["id"])

        # complete not existed todo
        response = self._Put(
            f"{TODO_BASE_ROUTE}{COMPLETE_TODO_ROUTE.format(id=34)}",
        )

        self.assertEqual(response.status_code, HTTP_NOT_FOUND_404)

        # uncomplete todo by other, nothing has changed
        response = self._Put(
            f"{TODO_BASE_ROUTE}{UNCOMPLETE_TODO_ROUTE.format(id=todo['id'])}",
            {},
            self.token2,
        )

        self.assertEqual(response.status_code, HTTP_FORBIDDEN_403)

        # uncomplete todo then the todo should be included
        response = self._Put(
            f"{TODO_BASE_ROUTE}{UNCOMPLETE_TODO_ROUTE.format(id=todo['id'])}",
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self.assertFalse(response.json()["completed"])

        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_REMAIN_TODOS_ROUTE}",
        )
        self._AssertContains(response.json(), todo["id"])

        # uncomplete not existed todo
        response = self._Put(
            f"{TODO_BASE_ROUTE}{UNCOMPLETE_TODO_ROUTE.format(id=32)}",
        )

        self.assertEqual(response.status_code, HTTP_NOT_FOUND_404)

        # delete todo by other, nothing has changed
        response = self._Delete(
            f"{TODO_BASE_ROUTE}{GET_TODO_INFO_ROUTE.format(id=todo['id'])}",
            self.token2,
        )

        self.assertEqual(response.status_code, HTTP_FORBIDDEN_403)
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_TODO_INFO_ROUTE.format(id=todo['id'])}",
        )
        self.assertEqual(response.status_code, HTTP_OK_200)

        newTodoTest = testTodo.copy()
        newTodoTest["title"] = "test2"
        newTodoTest["completed"] = True

        # update todo by other, nothing has changed
        response = self._Put(
            f"{TODO_BASE_ROUTE}{GET_TODO_INFO_ROUTE.format(id=todo['id'])}",
            newTodoTest,
            self.token2,
        )

        self.assertEqual(response.status_code, HTTP_FORBIDDEN_403)
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_TODO_INFO_ROUTE.format(id=todo['id'])}",
        )
        self._AssertTodo(response.json(), testTodo)

        # update todo then the todo should be updated
        response = self._Put(
            f"{TODO_BASE_ROUTE}{GET_TODO_INFO_ROUTE.format(id=todo['id'])}",
            newTodoTest,
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self._AssertTodo(response.json(), newTodoTest)
        self.assertFalse(response.json()["completed"])

        # update non existed todo
        response = self._Put(
            f"{TODO_BASE_ROUTE}{GET_TODO_INFO_ROUTE.format(id=34)}",
            newTodoTest,
        )

        self.assertEqual(response.status_code, HTTP_NOT_FOUND_404)

        # delete todo then the todo should not be included
        response = self._Delete(
            f"{TODO_BASE_ROUTE}{GET_TODO_INFO_ROUTE.format(id=todo['id'])}",
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_TODO_INFO_ROUTE.format(id=todo['id'])}",
        )

        self.assertEqual(response.status_code, HTTP_NOT_FOUND_404)

        # delete not existed todo
        response = self._Delete(
            f"{TODO_BASE_ROUTE}{GET_TODO_INFO_ROUTE.format(id=34)}",
        )

        self.assertEqual(response.status_code, HTTP_NOT_FOUND_404)

    def test_plannedTodo(self) -> None:
        # get all planned todos
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_ALL_PLANNED_TODOS_ROUTE}",
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self.assertEqual(len(response.json()), 0)

        # add planned todo
        testPlannedTodo = {
            "id": 0,
            "title": "test",
            "description": "test",
            "weekdays": ",".join([WEEK_MONDAY, WEEK_WEDNESDAY]),
            "gapWeek": 1,
        }

        response = self._Post(
            f"{TODO_BASE_ROUTE}{ADD_PLANNED_TODO_ROUTE}",
            testPlannedTodo,
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        plannedTodo = response.json()
        self._AssertPlannedTodo(plannedTodo, testPlannedTodo)

        # get that planned todo info
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_PLANNED_TODO_ROUTE.format(id=plannedTodo['id'])}",
        )

        self.assertEqual(response.status_code, HTTP_OK_200)

        # get all planned todos
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_ALL_PLANNED_TODOS_ROUTE}",
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self.assertEqual(len(response.json()), 1)

        # get all planneds todo by other user
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_ALL_PLANNED_TODOS_ROUTE}",
            self.token2,
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self.assertEqual(len(response.json()), 0)

        # get planned todo by other user
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_PLANNED_TODO_ROUTE.format(id=plannedTodo['id'])}",
            self.token2,
        )

        self.assertEqual(response.status_code, HTTP_FORBIDDEN_403)

        newPlannedTodo = testPlannedTodo.copy()
        newPlannedTodo["title"] = "test2"
        newPlannedTodo["weekdays"] = ",".join([WEEK_TUESDAY, WEEK_THURSDAY])

        # update planned todo by other user then nothing has changed
        response = self._Put(
            f"{TODO_BASE_ROUTE}{UPDATE_PLANNED_TODO_ROUTE.format(id=plannedTodo['id'])}",
            testPlannedTodo,
            self.token2,
        )

        self.assertEqual(response.status_code, HTTP_FORBIDDEN_403)

        # update planned todo then the planned todo should be updated
        response = self._Put(
            f"{TODO_BASE_ROUTE}{UPDATE_PLANNED_TODO_ROUTE.format(id=plannedTodo['id'])}",
            newPlannedTodo,
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self._AssertPlannedTodo(response.json(), newPlannedTodo)

        # delete planned todo by other user then nothing has changed
        response = self._Delete(
            f"{TODO_BASE_ROUTE}{GET_PLANNED_TODO_ROUTE.format(id=plannedTodo['id'])}",
            self.token2,
        )

        self.assertEqual(response.status_code, HTTP_FORBIDDEN_403)

        # delete planned todo then the planned todo should not be included
        response = self._Delete(
            f"{TODO_BASE_ROUTE}{GET_PLANNED_TODO_ROUTE.format(id=plannedTodo['id'])}",
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_PLANNED_TODO_ROUTE.format(id=plannedTodo['id'])}",
        )

        self.assertEqual(response.status_code, HTTP_NOT_FOUND_404)

    def test_TodayTodosContainsTheInstanceOfPlannedTodo(self):
        today = datetime.datetime.now().date().strftime("%Y-%m-%d")
        newPlannedTodo = {
            "id": 0,
            "title": "test-planned",
            "description": "test-planned",
            "weekdays": ",".join(
                [
                    WEEK_MONDAY,
                    WEEK_TUESDAY,
                    WEEK_WEDNESDAY,
                    WEEK_SATURDAY,
                    WEEK_SUNDAY,
                ]
            ),
            "gapWeek": 1,
            "numTodos": 2,
        }

        newPlannedTodo["id"] = self._Post(
            f"{TODO_BASE_ROUTE}{ADD_PLANNED_TODO_ROUTE}",
            newPlannedTodo,
        ).json()["id"]

        # get today todos include the planned todo
        response = self._Get(
            (f"{TODO_BASE_ROUTE}{GET_TODOS_BY_DATE_ROUTE}").format(date=today),
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self._AssertContainsByTitle(
            response.json(),
            newPlannedTodo["title"],
            num=newPlannedTodo["numTodos"],
        )

        response = self._Get(
            (f"{TODO_BASE_ROUTE}{GET_TODOS_BY_DATE_ROUTE}").format(
                date=(datetime.datetime.now().date() - timedelta(days=1)).strftime(
                    "%Y-%m-%d"
                )
            ),
        )

        self._AssertNotContainsByTitle(response.json(), newPlannedTodo["title"])

        # this weekday at the next week should have planned todo
        today = datetime.datetime.now().date()
        nextWeek = today + timedelta(days=7)

        response = self._Get(
            (f"{TODO_BASE_ROUTE}{GET_TODOS_BY_DATE_ROUTE}").format(date=nextWeek),
        )

        self._AssertContainsByTitle(
            response.json(),
            newPlannedTodo["title"],
            num=newPlannedTodo["numTodos"],
        )

        # next third day should not have the planned todo
        nextThirsday = today

        while nextThirsday == today or nextThirsday.strftime("%a") != "Thu":
            nextThirsday += timedelta(days=1)

        response = self._Get(
            (f"{TODO_BASE_ROUTE}{GET_TODOS_BY_DATE_ROUTE}").format(date=nextThirsday),
        )

        self._AssertNotContainsByTitle(response.json(), newPlannedTodo["title"])

        # next sunday should have the planned todo (checking twice, no duplicate)
        nextSunday = today

        while nextSunday == today or nextSunday.strftime("%a") != "Sun":
            nextSunday += timedelta(days=1)

        response = self._Get(
            (f"{TODO_BASE_ROUTE}{GET_TODOS_BY_DATE_ROUTE}").format(date=nextSunday),
        )

        self._AssertContainsByTitle(
            response.json(), newPlannedTodo["title"], num=newPlannedTodo["numTodos"]
        )

        response = self._Get(
            (f"{TODO_BASE_ROUTE}{GET_TODOS_BY_DATE_ROUTE}").format(date=nextSunday),
        )

        self._AssertContainsByTitle(
            response.json(), newPlannedTodo["title"], num=newPlannedTodo["numTodos"]
        )

        # get remain todos
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_REMAIN_TODOS_ROUTE}",
        )

        # only today and before uncompleted todos are included
        self._AssertContainsByTitle(
            response.json(), newPlannedTodo["title"], num=newPlannedTodo["numTodos"]
        )

        # when gap week is changed, all created todos which has the
        # same id and date >= today are deleted

        newPlannedTodo["gapWeek"] = 2
        # print(
        self._Put(
            f"{TODO_BASE_ROUTE}{UPDATE_PLANNED_TODO_ROUTE.format(id=newPlannedTodo['id'])}",
            newPlannedTodo,
        ).json()
        # )

        nextWeek = today + timedelta(days=7)

        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_TODOS_BY_DATE_ROUTE.format(date=nextWeek)}",
        )

        self._AssertNotContainsByTitle(response.json(), newPlannedTodo["title"])

        # todo order with the planned todo is earlier than the user created todo
        test_id = self._Post(
            f"{TODO_BASE_ROUTE}{ADD_TODO_ROUTE}",
            {
                "id": 0,
                "title": "test",
                "description": "test",
                "date": f"{today}",
                "complete": True,
            },
        ).json()["id"]

        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_TODOS_ORDER_ROUTE_BY_DATE.format(date=today)}",
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        todoIds = response.json()["orders"]

        if len(todoIds) > 0:
            response = self._Get(
                f"{TODO_BASE_ROUTE}{GET_TODO_INFO_ROUTE.format(id=todoIds[-1])}",
            )

        self.assertEqual(response.json()["id"], test_id)

        # get todo order with other user
        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_TODOS_ORDER_ROUTE_BY_DATE.format(date=today)}",
            self.token2,
        )

        if len(response.json()["orders"]) > 0:
            self.assertNotEqual(response.json()["orders"][-1], test_id)

        # update todo order with other user
        temp = todoIds[0]
        newIds = todoIds.copy()
        newIds[0] = newIds[-1]
        newIds[-1] = temp

        self._Put(
            f"{TODO_BASE_ROUTE}{UPDATE_TODOS_ORDER_ROUTE.format(date=today)}",
            {"orders": newIds},
            self.token2,
        )

        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_TODOS_ORDER_ROUTE_BY_DATE.format(date=today)}",
        )

        print(response.json())
        self.assertEqual(response.json()["orders"], todoIds)

        # update todo order
        response = self._Put(
            f"{TODO_BASE_ROUTE}{UPDATE_TODOS_ORDER_ROUTE.format(date=today)}",
            {"orders": newIds},
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self.assertEqual(response.json()["orders"], newIds)

        # delete all todos by date with wrong people
        self._Delete(
            f"{TODO_BASE_ROUTE}{CLEAN_TODOS_BY_DATE_ROUTE.format(date=today)}",
            self.token2,
        )

        self.assertNotEqual(
            self._Get(
                f"{TODO_BASE_ROUTE}{GET_TODOS_BY_DATE_ROUTE.format(date=today)}",
            ).json(),
            [],
        )

        # delete all todos by date
        self._Post(
            f"{TODO_BASE_ROUTE}{ADD_TODO_ROUTE}",
            {
                "id": 0,
                "title": "test",
                "description": "test",
                "date": f"{today}",
                "complete": True,
            },
        )

        response = self._Delete(
            f"{TODO_BASE_ROUTE}{CLEAN_TODOS_BY_DATE_ROUTE.format(date=today)}"
        )

        self.assertEqual(response.status_code, HTTP_OK_200)
        self.assertEqual(response.json(), {})

        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_TODOS_BY_DATE_ROUTE.format(date=today)}"
        )

        self.assertEqual(response.json(), [])

        # when the planned todo is deleted, then it will not be created again
        test_id = self._Post(
            f"{TODO_BASE_ROUTE}{ADD_TODO_ROUTE}",
            {
                "id": 0,
                "title": "test",
                "description": "test",
                "date": f"{today}",
                "complete": True,
            },
        ).json()["id"]

        response = self._Get(
            f"{TODO_BASE_ROUTE}{GET_TODOS_BY_DATE_ROUTE.format(date=today)}",
        )

        self.assertEqual(response.json()[0]["id"], test_id)
        self.assertEqual(len(response.json()), 1)
