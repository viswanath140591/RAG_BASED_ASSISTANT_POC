# main.py
# ============================================================
# Entry point for the Identity Manager RAG Chatbot
#
# Usage:
#   python main.py               → Start chatbot
#   python main.py --ingest      → Re-run document ingestion only
#   python main.py --help        → Show help
# ============================================================

import typer
from rich.console import Console
import ingestion
import chatbot

app = typer.Typer(help="Identity Manager AI Chatbot powered by RAG")
console = Console()


@app.command()
def start(
    ingest: bool = typer.Option(
        False,
        "--ingest",
        "-i",
        help="Run document ingestion before starting the chatbot",
    )
):
    """
    Start the Identity Manager AI Chatbot.
    """
    console.print("\n[bold magenta]━━━ Identity Manager RAG Chatbot ━━━[/bold magenta]")

    if ingest:
        ingestion.run_ingestion()

    chatbot.run_chatbot()


@app.command()
def ingest_only():
    """
    Run document ingestion only (without starting the chatbot).
    Use this when you have added or updated help documents.
    """
    ingestion.run_ingestion()
    console.print("\n[bold green]✅ Ingestion complete. Run 'python main.py' to start the chatbot.[/bold green]")


if __name__ == "__main__":
    app()
