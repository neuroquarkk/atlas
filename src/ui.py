from collections import defaultdict
from typing import Dict, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from src.storage import Symbol


class UI:
    def __init__(self) -> None:
        self.console = Console()

    def print_success(self, message: str) -> None:
        self.console.print(f"[bold green]{message}[/bold green]")

    def print_error(self, message: str) -> None:
        self.console.print(f"[bold red]{message}[/bold red]")

    def print_warning(self, message: str) -> None:
        self.console.print(f"[bold yellow]{message}[/bold yellow]")

    def print_header(self, message: str) -> None:
        self.console.print(f"[bold blue]{message}[/bold blue]")

    def print_stats(self, symbols: List[Symbol]) -> None:
        func_count = sum(1 for s in symbols if s.symbol_type == "function")
        class_count = sum(1 for s in symbols if s.symbol_type == "class")
        method_count = sum(1 for s in symbols if s.symbol_type == "method")

        grid = Table.grid(expand=True)
        grid.add_column()
        grid.add_column(justify="right")

        grid.add_row("Functions", str(func_count))
        grid.add_row("Classes", str(class_count))
        grid.add_row("Methods", str(method_count))

        panel = Panel(
            grid,
            title=f"[bold]Indexed {len(symbols)} Symbols[/bold]",
            border_style="green",
            expand=False,
        )

        self.console.print(panel)

    def print_search_results(self, query: str, results: List[Symbol]) -> None:
        if not results:
            self.print_warning(f"No results found for {query}")
            return

        self.console.print(
            f"[bold]Found {len(results)} result(s) for {query}:[/bold]\n"
        )

        # Group by file
        grouped: Dict[str, List[Symbol]] = defaultdict(list)
        for symbol in results:
            grouped[symbol.file_path].append(symbol)

        # Render as file tree

        for file_path, symbols in grouped.items():
            tree = Tree(f"[bold magenta]{file_path}[/bold magenta]")
            # sort by line number
            symbols.sort(key=lambda x: x.line_number)

            table = Table(
                box=None,
                show_header=False,
                pad_edge=False,
                collapse_padding=True,
            )
            table.add_column("Line", style="green", width=6)
            table.add_column("Type", style="cyan", width=10)
            table.add_column("Name", style="bold white")

            for s in symbols:
                table.add_row(str(s.line_number), s.symbol_type, s.symbol_name)

            tree.add(table)
            self.console.print(tree)
            self.console.print("")

    def print_status(
        self, root: str, metadata_dir: str, last_indexed: str
    ) -> None:
        table = Table(title="Project Status", show_header=False, box=None)
        table.add_column("Key", style="bold")
        table.add_column("Value")

        table.add_row("Root", root)
        table.add_row("Index Location", str(metadata_dir))

        status_style = "green" if last_indexed != "Never" else "yellow"
        table.add_row(
            "Last Indexed", f"[{status_style}]{last_indexed}[/{status_style}]"
        )

        self.console.print(Panel(table, expand=False, border_style="blue"))
