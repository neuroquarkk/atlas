import json
import os
import platform
import shutil
import sys
import tempfile
from typing import List, Optional, Tuple
import urllib.request
from pathlib import Path
from src.ui import UI


class Updater:
    GITHUB_REPO = "neuroquarkk/atlas"

    def __init__(self, current_version: str, ui: UI) -> None:
        self.__current_version = current_version
        self.__ui = ui
        self.__api = (
            f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"
        )

    def update(self) -> None:
        if not getattr(sys, "frozen", False):
            self.__ui.print_warning("Running from source")
            return

        try:
            latest_tag, assets = self.__get_latest_release()

            if (
                latest_tag == f"v{self.__current_version}"
                or latest_tag == self.__current_version
            ):
                self.__ui.print_success("atlas is already up to date")
                return

            self.__ui.console.print(
                f"[bold]New version available: {latest_tag}[/bold]"
            )
            asset_url, asset_name = self.__find_asset(assets)

            if not asset_url or not asset_name:
                self.__ui.print_error(
                    f"No compatible binary found for {sys.platform} in release {
                        latest_tag
                    }"
                )
                return

            self.__install_update(asset_url, asset_name, latest_tag)

        except Exception as e:
            self.__ui.print_error(f"Update failed: {e}")

    def __get_latest_release(self) -> Tuple[str, list]:
        req = urllib.request.Request(self.__api)
        req.add_header("User-Agent", "atlas-updater")

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            return data["tag_name"], data["assets"]

    def __find_asset(self, assets: List) -> Tuple[Optional[str], Optional[str]]:
        system = platform.machine().lower()
        machine = "amd64"

        if system == "darwin":
            system = "macos"

        expected_name = f"atlas-{system}-{machine}.zip"

        for asset in assets:
            if asset["name"] == expected_name:
                return asset["browser_download_url"], asset["name"]

        return None, None

    def __install_update(self, url: str, filename: str, version: str) -> None:
        with self.__ui.console.status(f"Download {version}...") as status:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir) / filename
                urllib.request.urlretrieve(url, temp_path)

                status.update("Extracting update...")
                extract_path = Path(temp_dir) / "extracted"
                shutil.unpack_archive(temp_path, extract_path)

                new_binary = next(extract_path.glob("atlas*"))
                current_binary = Path(sys.executable)

                status.update("Installing...")
                self.__replace_binary(current_binary, new_binary)

        self.__ui.print_success(f"Successfully updated to {version}")

    def __replace_binary(self, current: Path, new: Path) -> None:
        backup = current.with_suffix(current.suffix + ".old")

        try:
            if backup.exists():
                os.remove(backup)

            os.rename(current, backup)
            shutil.move(str(new), str(current))

            if platform.system() != "Windows":
                os.chmod(current, 0o755)

        except OSError as e:
            if backup.exists() and not current.exists():
                os.rename(backup, current)
            raise e
