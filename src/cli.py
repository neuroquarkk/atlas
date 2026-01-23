from src.analysis import Analyzer
import typer
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError
from src.indexer import Indexer
from src.project import Project
from src.search import Search
from src.stats import Stats
from src.ui import UI
from src.updater import Updater

app = typer.Typer(
    name="atlas",
    help="Project Scoped Codebase Indexer",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
ui = UI()

try:
    VERSION = version("atlas")
except PackageNotFoundError:
    VERSION = "0.0.0-dev"


@app.command()
def init():
    """Initialize atlas in current directory"""
    cwd = Path.cwd()
    try:
        Project.init(cwd)
        ui.print_success(f"Initialized atlas in {cwd}")
    except Exception as e:
        ui.print_error(f"Failed to initialize: {e}")
        raise typer.Exit(code=1)


@app.command()
def index(
    fresh: bool = typer.Option(
        False,
        "--fresh",
        "-f",
        help="Re-index from scratch",
    ),
):
    """Index the project"""
    cwd = Path.cwd()
    try:
        project = Project.load(cwd)
        indexer = Indexer(project)

        msg = "Re-indexing from scratch..." if fresh else "Indexing project..."

        with ui.console.status(msg):
            symbols = indexer.index(fresh=fresh)

        ui.print_stats(symbols)
    except FileNotFoundError:
        ui.print_warning("atlas not initialized. Run 'atlas init'")
        raise typer.Exit(code=1)
    except Exception as e:
        ui.print_error(f"Indexing failed: {e}")
        raise typer.Exit(code=1)


@app.command()
def search(
    query: str = typer.Argument(..., help="The symbol to search for"),
    partial: bool = typer.Option(
        False, "--partial", "-p", help="Enable partial search"
    ),
):
    """Search for symbols"""
    cwd = Path.cwd()
    try:
        project = Project.load(cwd)
        search_engine = Search(project)
        results = search_engine.find(query, partial=partial)
        ui.print_search_results(query, results)
    except FileNotFoundError:
        ui.print_warning("atlas not initialized or not indexed")
        raise typer.Exit(code=1)
    except Exception as e:
        ui.print_error(f"Search failed: {e}")
        raise typer.Exit(code=1)


@app.command()
def status():
    """Show indexing status"""
    cwd = Path.cwd()
    try:
        project = Project.load(cwd)
        indexer = Indexer(project)
        with ui.console.status("Checking file status..."):
            diff = indexer.diff_changes()
        ui.print_file_status(diff)
    except FileNotFoundError:
        ui.print_warning("atlas not initialized or not indexed")
        raise typer.Exit(code=1)
    except Exception as e:
        ui.print_error(f"Failed to get status: {e}")
        raise typer.Exit(code=1)


@app.command()
def stats(
    limit: int = typer.Option(
        5, "--limit", "-l", help="Number of top files to show"
    ),
):
    """Show advanced codebase statistics"""
    cwd = Path.cwd()
    try:
        project = Project.load(cwd)
        stats_engine = Stats(project)
        with ui.console.status("Calculating stats..."):
            data = stats_engine.generate(limit=limit)
        ui.print_advanced_stats(data)
    except FileNotFoundError:
        ui.print_warning("atlas not initialized or not indexed")
        raise typer.Exit(code=1)
    except Exception as e:
        ui.print_error(f"Failed to get status: {e}")
        raise typer.Exit(code=1)


@app.command()
def upgrade():
    """Update atlas to the latest version"""
    updater = Updater(VERSION, ui)
    updater.update()


@app.command()
def unused():
    """Find potentially unused symbols"""
    cwd = Path.cwd()
    try:
        project = Project.load(cwd)
        analyzer = Analyzer(project)

        with ui.console.status("Analyzing codebase for usage..."):
            unused_symbols = analyzer.find_unused_symbols()

        ui.print_unused(unused_symbols)
    except FileNotFoundError:
        ui.print_warning("atlas not initialized or not indexed")
        raise typer.Exit(code=1)
    except Exception as e:
        ui.print_error(f"Analysis failed: {e}")
        raise typer.Exit(code=1)


@app.command()
def version():
    """Show current version"""
    ui.console.print(f"atlas version [bold cyan]{VERSION}[/bold cyan]")
