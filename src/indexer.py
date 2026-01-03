import hashlib
import pathspec
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
        self.__ignore_spec = self.__load_ignore_spec()

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
        try:
            rel_path = path.relative_to(self.__project.root)

            if self.__ignore_spec.match_file(str(rel_path)):
                return False
            return True
        except ValueError:
            return False

    def __load_ignore_spec(self) -> pathspec.PathSpec:
        patterns = [
            ".git",
            ".atlas",
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
            "*.pyc",
            ".DS_Store",
        ]

        gitignore_path = self.__project.root / ".gitignore"
        if gitignore_path.exists():
            try:
                with open(gitignore_path, "r") as f:
                    patterns.extend(f.read().splitlines())
            except Exception:
                pass

        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
