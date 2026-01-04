from dataclasses import dataclass
import hashlib
import pathspec
from pathlib import Path
from typing import Dict, List, Set
from src.parsers.parser import Parser
from src.project import Project
from src.storage import Storage, Symbol


@dataclass
class FileDiff:
    added: Set[str]
    modified: Set[str]
    deleted: Set[str]
    current_hashes: Dict[str, str]


class Indexer:
    def __init__(self, project: Project) -> None:
        self.__project = project
        self.__parser = Parser()
        self.__storage = Storage(project)
        self.__ignore_spec = self.__load_ignore_spec()

    def index(self, fresh: bool = False) -> List[Symbol]:
        if fresh:
            self.__storage.clear_database()

        diff = self.diff_changes()

        for path in diff.deleted:
            self.__storage.remove_file(path)

        to_process = diff.added | diff.modified

        for path in to_process:
            file_hash = diff.current_hashes[path]
            symbols = self.__parser.parse_file(Path(path))
            self.__storage.update_file(path, file_hash, symbols)

        self.__storage.update_timestamp()
        return self.__storage.get_all_symbols()

    def diff_changes(self) -> FileDiff:
        current_files = self.__scan_disk()
        stored_files = self.__storage.get_file_hashes()

        current_paths = set(current_files.keys())
        stored_paths = set(stored_files.keys())

        added = current_paths - stored_paths
        deleted = stored_paths - current_paths
        modified = set()

        common_paths = current_paths.intersection(stored_paths)
        for path in common_paths:
            if current_files[path] != stored_files[path]:
                modified.add(path)

        return FileDiff(added, modified, deleted, current_files)

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
