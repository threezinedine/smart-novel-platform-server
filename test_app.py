from utils.database.t_database import override_get_db, engine
from utils.database.database import get_db
from main import app

app.dependency_overrides[get_db] = override_get_db
