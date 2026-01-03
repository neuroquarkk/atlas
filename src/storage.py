import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List
from src.project import Project


@dataclass
class Symbol:
    symbol_name: str
    symbol_type: str  # function, class, method
    file_path: str
    line_number: int


class Storage:
    __INDEX_FILE = "index.json"

    def __init__(self, project: Project) -> None:
        self.__index_path = project.metadata_dir / self.__INDEX_FILE

    def save_index(self, symbols: List[Symbol]) -> None:
        data: List[Dict[str, Any]] = [asdict(s) for s in symbols]

        with open(self.__index_path, "w") as f:
            json.dump(data, f, indent=4)

    def load_index(self) -> List[Symbol]:
        if not self.__index_path.exists():
            raise FileNotFoundError("Index not found. Run 'atlas index' first")

        with open(self.__index_path, "r") as f:
            data = json.load(f)

        return [Symbol(**item) for item in data]
