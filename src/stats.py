from dataclasses import dataclass
from typing import Dict, List, Tuple

from src.project import Project
from src.storage import Storage


@dataclass
class CodebaseStats:
    total_files: int
    total_symbols: int
    docstring_coverage: float
    type_distribution: Dict[str, int]
    top_files: List[Tuple[str, int]]


class Stats:
    def __init__(self, project: Project) -> None:
        self.__storage = Storage(project)

    def generate(self, limit: int = 5) -> CodebaseStats:
        return CodebaseStats(
            total_files=self.__storage.get_file_count(),
            total_symbols=self.__storage.get_total_symbol_count(),
            docstring_coverage=self.__calculate_coverage(),
            type_distribution=self.__storage.get_symbol_counts_by_type(),
            top_files=self.__storage.get_top_files_by_symbol_count(limit),
        )

    def __calculate_coverage(self) -> float:
        total = self.__storage.get_total_symbol_count()
        if total == 0:
            return 0.0

        documented = self.__storage.get_documented_symbol_count()
        return round((documented / total) * 100, 1)
