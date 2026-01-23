import ast
import pathspec
from typing import List, Set
from pathlib import Path
from src.project import Project
from src.storage import Symbol, Storage


class Analyzer:
    def __init__(self, project: Project) -> None:
        self.__project = project
        self.__storage = Storage(project)
        self.__ignore_spec = self.__load_ignore_spec()

    def find_unused_symbols(self) -> List[Symbol]:
        all_symbols = self.__storage.get_all_symbols()
        if not all_symbols:
            return []

        defined_names = {s.symbol_name for s in all_symbols}
        used_names: Set[str] = set()

        for file_path in self.__project.root.rglob("*.py"):
            if not self.__should_scan(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Name):
                            if node.id in defined_names:
                                used_names.add(node.id)
                        elif isinstance(node, ast.Attribute):
                            if node.attr in defined_names:
                                used_names.add(node.attr)
            except Exception:
                continue

        unused = [
            s
            for s in all_symbols
            if s.symbol_name not in used_names
            and not s.symbol_name.startswith("__")
        ]

        return unused

    def __should_scan(self, path: Path) -> bool:
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
