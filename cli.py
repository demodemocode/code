import typer
from rich.console import Console
from codi.constants import CODI_VERSION
from codi.logic.ai_keywords import MissingAPIKeyError

app = typer.Typer(help="CODI - Project Code Intelligence CLI")
console = Console()


# ----------------------------------------------------------
# codi version
# ----------------------------------------------------------
@app.command()
def version():
    """Show CODI version"""
    typer.echo(f"CODI version {CODI_VERSION}")


# ----------------------------------------------------------
# codi init
# ----------------------------------------------------------
@app.command()
def init():
    """Index all project files → generate .codi/index.json"""
    try:
        with console.status("[bold green]Indexing project files...", spinner="dots"):
            from codi.logic.file_indexer import index_project
            index_project()

        console.print("[bold green]✓ Indexing completed successfully!")

    except MissingAPIKeyError as e:
        console.print(f"[bold red]❌ ERROR:[/bold red] {str(e)}")
        raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[bold red]❌ Unexpected error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)




# ----------------------------------------------------------
# codi task command
# ----------------------------------------------------------
from codi.logic.task_processor import (
    list_tasks,
    run_existing_task,
    create_or_update_task,
)
@app.command()
def task(
    list: bool = typer.Option(False, "--list", help="List all saved tasks"),
    id: str = typer.Option(None, "--id", "-i", help="Task ID"),
    description: str = typer.Option(None, "--desc", "-d", help="Task description")
):
    # LIST tasks
    if list:
        list_tasks()
        return

    # RUN existing task
    if id and not description:
        run_existing_task(id)
        return

    # CREATE or UPDATE a task
    if id and description:
        create_or_update_task(id, description)
        return

    # INVALID usage
    console.print(
        "[bold red]❌ Invalid usage.[/bold red]\n\n"
        "Examples:\n"
        "  codi task --list\n"
        "  codi task --id add-email --desc \"Add email validation\"\n"
        "  codi task --id add-email\n"
    )


# ----------------------------------------------------------
# codi update
# ----------------------------------------------------------
@app.command()
def update():
    """Update CODI to latest version (Git-based)"""
    with console.status("[bold cyan]Checking for updates...", spinner="line"):
        import subprocess
        try:
            subprocess.run(["git", "pull"], check=True)
            console.print("[bold green]✓ CODI updated to latest version!")
        except Exception:
            console.print("[bold red]Update failed. Was CODI installed using git clone?")
            console.print("If installed via pip, upgrade using:")
            console.print("[bold yellow]pip install --upgrade codi-cli")


if __name__ == "__main__":
    app()
