from typing import List
from src.project import Project
from src.storage import Storage, Symbol


class Search:
    def __init__(self, project: Project) -> None:
        self.__storage = Storage(project)

    def find(self, query: str, partial: bool = False) -> List[Symbol]:
        symbols = self.__storage.load_index()

        results: List[Symbol] = []
        query_norm = query.lower() if partial else query
        for symbol in symbols:
            if partial:
                # case insensitive match
                if query_norm in symbol.symbol_name.lower():
                    results.append(symbol)
            else:
                # Exact match
                if symbol.symbol_name == query:
                    results.append(symbol)
        return results
