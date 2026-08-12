import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

POSSIBLE_PATHS = [
    BASE_DIR / "data" / "company.db",
    BASE_DIR.parent / "data" / "company.db",
    Path.cwd() / "data" / "company.db",
    Path.cwd() / "backend" / "data" / "company.db",
]

DB_PATH = next(
    (path for path in POSSIBLE_PATHS if path.exists()),
    BASE_DIR / "data" / "company.db"
)

def get_connection():
    connection = sqlite3.connect(str(DB_PATH))
    connection.row_factory = sqlite3.Row
    return connection