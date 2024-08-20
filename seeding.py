import requests
from config import initialize_config, get_config
from apis.v1.users.routes import *

initialize_config()
config = get_config()

host = config.Get("host", "localhost")
port = config.Get("port", 8888)

requests.post(
    f"http://{host}:{port}/users/register",
    json={"username": "admin", "password": "admin"},
)
