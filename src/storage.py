import sqlite3
from dataclasses import dataclass
from typing import Dict, List
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
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_file ON symbols(file_path)"
        )

        # metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        # file_hashes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_hashes (
                file_path TEXT PRIMARY KEY,
                file_hash TEXT
            )
        """)

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

    def get_file_hashes(self) -> Dict[str, str]:
        cursor = self.__conn.cursor()
        cursor.execute("SELECT file_path, file_hash FROM file_hashes")
        return {row[0]: row[1] for row in cursor.fetchall()}

    def update_file(
        self, file_path: str, file_hash: str, symbols: List[Symbol]
    ) -> None:
        cursor = self.__conn.cursor()

        cursor.execute("DELETE FROM symbols WHERE file_path = ?", (file_path,))

        data = [
            (s.symbol_name, s.symbol_type, s.file_path, s.line_number)
            for s in symbols
        ]

        cursor.executemany("INSERT INTO symbols VALUES (?, ?, ?, ?)", data)

        cursor.execute(
            "INSERT OR REPLACE INTO file_hashes (file_path, file_hash) VALUES (?, ?)",
            (file_path, file_hash),
        )

        self.__conn.commit()

    def remove_file(self, file_path: str) -> None:
        cursor = self.__conn.cursor()
        cursor.execute("DELETE FROM symbols WHERE file_path = ?", (file_path,))
        cursor.execute(
            "DELETE FROM file_hashes WHERE file_path = ?", (file_path,)
        )
        self.__conn.commit()

    def get_all_symbols(self) -> List[Symbol]:
        cursor = self.__conn.cursor()
        cursor.execute("SELECT * FROM symbols")
        return [Symbol(*row) for row in cursor.fetchall()]

    def update_timestamp(self) -> None:
        now = datetime.now().isoformat()
        cursor = self.__conn.cursor()

        cursor.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            ("last_indexed", now),
        )

        self.__conn.commit()

    def clear_database(self) -> None:
        cursor = self.__conn.cursor()
        cursor.execute("DELETE FROM symbols")
        cursor.execute("DELETE FROM file_hashes")
        cursor.execute("DELETE FROM metadata")
        self.__conn.commit()

    def close(self) -> None:
        self.__conn.close()

    def __del__(self) -> None:
        self.close()
