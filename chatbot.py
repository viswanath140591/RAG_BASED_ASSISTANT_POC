# chatbot.py
# ============================================================
# CLI Chatbot Interface
# Provides an interactive terminal chat experience using Rich
# for beautiful formatted output.
# ============================================================

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich import box
from datetime import datetime

import rag_pipeline as rag
import ingestion
import config

console = Console()

# Track session feedback stats
session_stats = {"total": 0, "thumbs_up": 0, "thumbs_down": 0}


def print_banner():
    console.print(Panel.fit(
        "[bold cyan]🤖 Identity Manager AI Assistant[/bold cyan]\n"
        "[dim]Powered by RAG — Answers from your official documentation[/dim]",
        border_style="cyan",
        padding=(1, 4),
    ))
    console.print(
        "[dim]Type your question below. Commands: [bold]/help[/bold] | "
        "[bold]/sources[/bold] | [bold]/stats[/bold] | [bold]/exit[/bold][/dim]\n"
    )


def print_help():
    table = Table(box=box.ROUNDED, border_style="cyan", show_header=True)
    table.add_column("Command", style="bold yellow")
    table.add_column("Description")
    table.add_row("/help",    "Show this help menu")
    table.add_row("/sources", "Show all documents in the knowledge base")
    table.add_row("/stats",   "Show session feedback statistics")
    table.add_row("/reingest","Re-ingest documents (after docs are updated)")
    table.add_row("/exit",    "Exit the chatbot")
    console.print(table)


def print_answer(result: dict, query: str):
    """Render the LLM answer in a nicely formatted panel."""

    # Answer panel
    console.print(Panel(
        Markdown(result["answer"]),
        title="[bold green]💬 Answer[/bold green]",
        border_style="green",
        padding=(1, 2),
    ))

    # Sources used
    if result["sources"]:
        sources_text = "  ".join(f"📄 [cyan]{s}[/cyan]" for s in result["sources"])
        console.print(f"[dim]Sources: {sources_text}[/dim]")
    else:
        console.print("[dim]No matching documentation found.[/dim]")


def collect_feedback() -> str:
    """Ask user to rate the response."""
    console.print("\n[dim]Was this answer helpful? ([bold]y[/bold]es / [bold]n[/bold]o / [bold]s[/bold]kip)[/dim]")
    feedback = Prompt.ask("  Feedback", choices=["y", "n", "s"], default="s")

    session_stats["total"] += 1
    if feedback == "y":
        session_stats["thumbs_up"] += 1
        console.print("[green]  👍 Thanks for your feedback![/green]")
    elif feedback == "n":
        session_stats["thumbs_down"] += 1
        console.print("[red]  👎 Sorry about that! We'll use this to improve.[/red]")

    return feedback


def print_stats():
    """Display session statistics."""
    total = session_stats["total"]
    up = session_stats["thumbs_up"]
    down = session_stats["thumbs_down"]
    score = f"{(up / total * 100):.0f}%" if total > 0 else "N/A"

    table = Table(box=box.SIMPLE, title="📊 Session Stats")
    table.add_column("Metric", style="bold")
    table.add_column("Value", style="cyan")
    table.add_row("Questions Asked", str(session_stats["total"]))
    table.add_row("👍 Helpful",      str(up))
    table.add_row("👎 Not Helpful",  str(down))
    table.add_row("Satisfaction",   score)
    console.print(table)


def run_chatbot():
    """Main chatbot loop."""

    # ── Step 1: Ensure knowledge base is ready ─────────────────────────────
    if not ingestion.is_vector_store_ready():
        console.print("[yellow]⚠️  No knowledge base found. Running ingestion first...[/yellow]")
        ingestion.run_ingestion()
    else:
        console.print("[green]✅ Knowledge base loaded.[/green]\n")

    # ── Step 2: Load vector store & LLM ────────────────────────────────────
    vector_store = ingestion.load_existing_vector_store()
    llm = rag.get_llm()

    console.print(f"[dim]🤖 LLM: {config.LLM_PROVIDER.upper()} | "
                  f"📚 Docs: {config.DOCS_FOLDER} | "
                  f"🔍 Top-K: {config.TOP_K_RESULTS}[/dim]\n")

    print_banner()

    # ── Step 3: Chat loop ───────────────────────────────────────────────────
    while True:
        try:
            query = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip()

            if not query:
                continue

            # ── Handle commands ─────────────────────────────────────────────
            if query.lower() == "/exit":
                console.print("\n[bold cyan]👋 Goodbye! Session ended.[/bold cyan]")
                print_stats()
                break

            elif query.lower() == "/help":
                print_help()
                continue

            elif query.lower() == "/stats":
                print_stats()
                continue

            elif query.lower() == "/reingest":
                console.print("[yellow]🔄 Re-ingesting documents...[/yellow]")
                ingestion.run_ingestion()
                vector_store = ingestion.load_existing_vector_store()
                console.print("[green]✅ Knowledge base updated![/green]")
                continue

            elif query.lower() == "/sources":
                console.print(f"[cyan]📂 Docs folder: {config.DOCS_FOLDER}[/cyan]")
                continue

            # ── RAG Query ───────────────────────────────────────────────────
            timestamp = datetime.now().strftime("%H:%M:%S")
            console.print(f"\n[dim][{timestamp}] 🔍 Searching knowledge base...[/dim]")

            result = rag.ask(vector_store, query, llm)
            print_answer(result, query)
            collect_feedback()

        except KeyboardInterrupt:
            console.print("\n\n[bold cyan]👋 Session interrupted. Goodbye![/bold cyan]")
            print_stats()
            break
        except Exception as e:
            console.print(f"[red]❌ Error: {e}[/red]")
            console.print("[dim]Please try again or type /exit to quit.[/dim]")
