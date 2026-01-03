from typing import List
from src.project import Project
from src.storage import Storage, Symbol


class Search:
    def __init__(self, project: Project) -> None:
        self.__storage = Storage(project)

    def find(self, query: str) -> List[Symbol]:
        symbols = self.__storage.load_index()

        results: List[Symbol] = []
        for symbol in symbols:
            if symbol.symbol_name == query:
                results.append(symbol)
        return results
