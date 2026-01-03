import hashlib
from pathlib import Path
from typing import Dict, List
from src.parser import Parser
from src.project import Project
from src.storage import Storage, Symbol


class Indexer:
    def __init__(self, project: Project) -> None:
        self.__project = project
        self.__parser = Parser()
        self.__storage = Storage(project)

    def index(self) -> List[Symbol]:
        current_files = self.__scan_disk()
        stored_files = self.__storage.get_file_hashes()

        stored_paths = set(stored_files.keys())
        current_paths = set(current_files.keys())
        deleted_paths = stored_paths - current_paths

        for path in deleted_paths:
            self.__storage.remove_file(path)

        for path, current_hash in current_files.items():
            stored_hash = stored_files.get(path)
            if stored_hash != current_hash:
                symbols = self.__parser.parse_file(Path(path))
                self.__storage.update_file(path, current_hash, symbols)

        self.__storage.update_timestamp()
        return self.__storage.get_all_symbols()

    def __scan_disk(self) -> Dict[str, str]:
        file_map: Dict[str, str] = {}
        for path in self.__project.root.rglob("*.py"):
            if self.__should_index(path):
                file_map[str(path)] = self.__compute_hash(path)
        return file_map

    def __compute_hash(self, file_path: Path) -> str:
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

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
