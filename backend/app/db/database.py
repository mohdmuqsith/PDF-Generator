import sqlite3

from app.core.config import DATABASE_PATH


def get_connection():
    return sqlite3.connect(DATABASE_PATH)
