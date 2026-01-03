from pathlib import Path
from typing import List
from src.parser import Parser
from src.project import Project
from src.storage import Storage, Symbol


class Indexer:
    def __init__(self, project: Project) -> None:
        self.__project = project
        self.__parser = Parser()
        self.__storage = Storage(project)

    def index(self) -> List[Symbol]:
        files = self.__find_py_files()
        symbols: List[Symbol] = []

        for file_path in files:
            file_symbols = self.__parser.parse_file(file_path)
            symbols.extend(file_symbols)

        self.__storage.save_index(symbols)
        self.__project.update_indexed_timestamp()

        return symbols

    def __find_py_files(self) -> List[Path]:
        files: List[Path] = []

        for path in self.__project.root.rglob("*.py"):
            if self.__should_index(path):
                files.append(path)

        return files

    def __should_index(self, path: Path) -> bool:
        # skip metadata directory
        try:
            path.relative_to(self.__project.metadata_dir)
            return False
        except ValueError:
            pass

        # skip common directories to ignore
        parts = path.parts
        ignored = {".git", ".venv", "venv", "__pycache__", "node_modules"}

        for part in parts:
            if part in ignored:
                return False

        return True
