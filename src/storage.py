import sqlite3
from dataclasses import dataclass
from typing import List
from src.project import Project
from datetime import datetime


@dataclass
class Symbol:
    symbol_name: str
    symbol_type: str  # function, class, method
    file_path: str
    line_number: int


class Storage:
    __DB_FILE = "index.db"

    def __init__(self, project: Project) -> None:
        self.__db_path = project.metadata_dir / self.__DB_FILE
        self.__conn = sqlite3.connect(self.__db_path)
        self.__create_schema()

    def __create_schema(self) -> None:
        cursor = self.__conn.cursor()

        # symbols table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS symbols (
                name TEXT,
                type TEXT,
                file_path TEXT,
                line_number INTEGER
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_name ON symbols(name)")

        # metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        self.__conn.commit()

    def save_index(
        self, symbols: List[Symbol], update_timestamp: bool = False
    ) -> None:
        cursor = self.__conn.cursor()

        # clear existing index (full re-index)
        cursor.execute("DELETE FROM symbols")

        data = [
            (s.symbol_name, s.symbol_type, s.file_path, s.line_number)
            for s in symbols
        ]

        cursor.executemany("INSERT INTO symbols VALUES (?, ?, ?, ?)", data)

        if update_timestamp:
            self.__update_timestamp()

        self.__conn.commit()

    def find(self, query: str, partial: bool = False) -> List[Symbol]:
        cursor = self.__conn.cursor()

        if partial:
            # sqlite LIKE is case-insensitive by default
            sql = "SELECT * FROM symbols WHERE name LIKE ?"
            cursor.execute(sql, (f"%{query}%",))
        else:
            sql = "SELECT * FROM symbols WHERE name = ?"
            cursor.execute(sql, (query,))

        return [Symbol(*row) for row in cursor.fetchall()]

    def __update_timestamp(self) -> None:
        now = datetime.now().isoformat()
        cursor = self.__conn.cursor()

        cursor.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            ("last_indexed", now),
        )

        self.__conn.commit()

    def get_last_indexed(self) -> str:
        cursor = self.__conn.cursor()
        cursor.execute("SELECT value FROM metadata WHERE key = 'last_indexed'")
        row = cursor.fetchone()
        return row[0] if row else "Never"

    def close(self) -> None:
        self.__conn.close()

    def __del__(self) -> None:
        self.close()
