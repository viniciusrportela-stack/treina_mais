import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "academia.db"


def conn():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    return conexao