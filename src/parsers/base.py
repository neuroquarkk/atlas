from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
from src.storage import Symbol


class BaseParser(ABC):
    @abstractmethod
    def parse_file(self, file_path: Path) -> List[Symbol]:
        pass

    @property
    @abstractmethod
    def extensions(self) -> List[str]:
        pass
