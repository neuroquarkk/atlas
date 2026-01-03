from typing import List
from src.project import Project
from src.storage import Storage, Symbol


class Search:
    def __init__(self, project: Project) -> None:
        self.__storage = Storage(project)

    def find(self, query: str, partial: bool = False) -> List[Symbol]:
        return self.__storage.find(query, partial=partial)
