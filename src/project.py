from pathlib import Path


class Project:
    __METADATA_DIR = ".atlas"
    __GITIGNORE_FILE = ".gitignore"

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.metadata_dir = self.root / self.__METADATA_DIR

    @classmethod
    def init(cls, root: Path) -> None:
        project = cls(root)
        project.metadata_dir.mkdir(exist_ok=True)
        project.__update_gitignore()

    @classmethod
    def load(cls, root: Path) -> "Project":
        project = cls(root)
        if not project.metadata_dir.exists():
            raise FileNotFoundError(f"atlas not initialized in {root}")
        return project

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
