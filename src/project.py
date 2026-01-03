from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import json


@dataclass
class ProjectMetadata:
    project_root: str
    last_indexed: Optional[str]


class Project:
    __METADATA_DIR = ".atlas"
    __METADATA_FILE = "metadata.json"
    __GITIGNORE_FILE = ".gitignore"

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.metadata_dir = self.root / self.__METADATA_DIR
        self.__metadata_file = self.metadata_dir / self.__METADATA_FILE

    @classmethod
    def init(cls, root: Path) -> None:
        project = cls(root)

        project.metadata_dir.mkdir(exist_ok=True)

        metadata = ProjectMetadata(
            project_root=str(project.root),
            last_indexed=None,
        )
        project.__save_metadata(metadata)
        project.__update_gitignore()

    @classmethod
    def load(cls, root: Path) -> "Project":
        project = cls(root)
        if not project.metadata_dir.exists():
            raise FileNotFoundError(f"atlas not initialized in {root}")
        return project

    def get_metadata(self) -> ProjectMetadata:
        with open(self.__metadata_file, "r") as f:
            data = json.load(f)
        return ProjectMetadata(**data)

    def update_indexed_timestamp(self) -> None:
        metadata = self.get_metadata()
        metadata.last_indexed = datetime.now().isoformat()
        self.__save_metadata(metadata)

    def __save_metadata(self, metadata: ProjectMetadata) -> None:
        with open(self.__metadata_file, "w") as f:
            json.dump(
                {
                    "project_root": metadata.project_root,
                    "last_indexed": metadata.last_indexed,
                },
                f,
                indent=4,
            )

    def __update_gitignore(self) -> None:
        gitignore_path = self.root / self.__GITIGNORE_FILE
        ignore_entry = ".atlas/"

        if gitignore_path.exists():
            content = gitignore_path.read_text()
            if ignore_entry not in content:
                prefix = "\n" if content and not content.endswith("\n") else ""
                with open(gitignore_path, "a") as f:
                    f.write(f"{prefix}{ignore_entry}\n")
        else:
            gitignore_path.write_text(f"{ignore_entry}\n")
