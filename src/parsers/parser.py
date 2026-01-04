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

    def get_supported_extensions(self) -> List[str]:
        return list(self.__ext_map.keys())

    def supports_file(self, file_path: Path) -> bool:
        ext = file_path.suffix.lower()
        return ext in self.__ext_map
