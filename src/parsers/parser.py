from pathlib import Path
from typing import List
from src.parsers.python import PythonParser
from src.storage import Symbol


class Parser:
    def __init__(self) -> None:
        self.__parsers = [PythonParser()]
        self.__ext_map = {}
        for parser in self.__parsers:
            for ext in parser.extensions:
                self.__ext_map[ext] = parser

    def parse_file(self, file_path: Path) -> List[Symbol]:
        ext = file_path.suffix.lower()
        parser = self.__ext_map.get(ext)

        if parser is None:
            return []

        return parser.parse_file(file_path)
