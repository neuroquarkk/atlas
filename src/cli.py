import sys
import argparse
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError
from src.indexer import Indexer
from src.project import Project
from src.search import Search
from src.ui import UI
from src.updater import Updater


class CLI:
    def __init__(self) -> None:
        self.__ui = UI()
        try:
            self.__VERSION = version("atlas")
        except PackageNotFoundError:
            self.__VERSION = "0.0.0-dev"

    def run(self) -> None:
        parser = argparse.ArgumentParser(
            prog="atlas", description="Project Scoped Codebase Indexer"
        )
        subparsers = parser.add_subparsers(
            dest="command", help="Available commands"
        )

        # init command
        parser_init = subparsers.add_parser(
            "init", help="Initialize atlas in current directory"
        )
        parser_init.set_defaults(func=self.__init_command)

        # index command
        parser_index = subparsers.add_parser("index", help="Index the project")
        parser_index.add_argument(
            "-f", "--fresh", action="store_true", help="Re-index from scratch"
        )
        parser_index.set_defaults(func=self.__index_command)

        # search command
        parser_search = subparsers.add_parser(
            "search", help="Search for symbols"
        )
        parser_search.add_argument("query", help="The symbol to search for")
        parser_search.add_argument(
            "-p",
            "--partial",
            action="store_true",
            help="Enable partial matching",
        )
        parser_search.set_defaults(func=self.__search_command)

        # status command
        parser_status = subparsers.add_parser(
            "status", help="Show indexing status"
        )
        parser_status.set_defaults(func=self.__status_command)

        # version command
        parser_version = subparsers.add_parser(
            "version", help="Show current version"
        )
        parser_version.set_defaults(func=self.__version_command)

        # upgrade command
        parser_upgrade = subparsers.add_parser(
            "upgrade", help="Update atlas to the latest version"
        )
        parser_upgrade.set_defaults(func=self.__upgrade_command)

        args = parser.parse_args()

        if hasattr(args, "func"):
            args.func(args)
        else:
            parser.print_help()

    def __init_command(self, args: argparse.Namespace) -> None:
        cwd = Path.cwd()
        try:
            Project.init(cwd)
            self.__ui.print_success(f"initialized atlas in {cwd}")
        except Exception as e:
            self.__ui.print_error(f"Failed to initialize: {e}")
            sys.exit(1)

    def __index_command(self, args: argparse.Namespace) -> None:
        cwd = Path.cwd()
        try:
            project = Project.load(cwd)
            indexer = Indexer(project)

            msg = (
                "Re-indexing from scratch..."
                if args.fresh
                else "Indexing project..."
            )

            with self.__ui.console.status(msg):
                symbols = indexer.index(fresh=args.fresh)

            self.__ui.print_stats(symbols)

        except FileNotFoundError:
            self.__ui.print_warning("atlas not initialized. Run 'atlas init'")
            sys.exit(1)
        except Exception as e:
            self.__ui.print_error(f"Indexing failed: {e}")
            sys.exit(1)

    def __search_command(self, args: argparse.Namespace) -> None:
        query = args.query
        partial = args.partial
        cwd = Path.cwd()

        try:
            project = Project.load(cwd)
            search = Search(project)
            results = search.find(query, partial=partial)

            self.__ui.print_search_results(query, results)

        except FileNotFoundError:
            self.__ui.print_warning("atlas not initialized or not indexed")
            sys.exit(1)
        except Exception as e:
            self.__ui.print_error(f"Search failed: {e}")
            sys.exit(1)

    def __status_command(self, args: argparse.Namespace) -> None:
        cwd = Path.cwd()
        try:
            project = Project.load(cwd)
            indexer = Indexer(project)

            with self.__ui.console.status("Checking file status..."):
                diff = indexer.diff_changes()

            self.__ui.print_file_status(diff)
        except FileNotFoundError:
            self.__ui.print_warning("atlas not initialized")
            sys.exit(1)
        except Exception as e:
            self.__ui.print_error(f"Failed to get status: {e}")
            sys.exit(1)

    def __version_command(self, args: argparse.Namespace) -> None:
        self.__ui.console.print(
            f"atlas version [bold cyan]{self.__VERSION}[/bold cyan]"
        )

    def __upgrade_command(self, args: argparse.Namespace) -> None:
        updater = Updater(self.__VERSION, self.__ui)
        updater.update()
