# ingestion.py
# ============================================================
# Handles loading, parsing, chunking, and storing documents
# into the ChromaDB vector store.
#
# Supported formats: PDF, DOCX, HTML, TXT
# ============================================================

import os
from pathlib import Path
from rich.console import Console
from rich.progress import track

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    BSHTMLLoader,
    TextLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

import config

console = Console()


# ── Supported file types ──────────────────────────────────────────────────────
LOADERS = {
    ".pdf":  PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".html": BSHTMLLoader,
    ".htm":  BSHTMLLoader,
    ".txt":  TextLoader,
}


def load_documents(docs_folder: str) -> list:
    """
    Walk through the docs folder and load all supported documents.
    Returns a list of LangChain Document objects.
    """
    docs_path = Path(docs_folder)
    if not docs_path.exists():
        console.print(f"[red]❌ Docs folder not found: {docs_folder}[/red]")
        raise FileNotFoundError(f"Docs folder not found: {docs_folder}")

    all_documents = []
    files = list(docs_path.rglob("*"))
    supported_files = [f for f in files if f.suffix.lower() in LOADERS]

    if not supported_files:
        console.print(f"[yellow]⚠️  No supported documents found in {docs_folder}[/yellow]")
        return []

    console.print(f"\n[bold cyan]📂 Found {len(supported_files)} document(s) to ingest...[/bold cyan]")

    for file_path in track(supported_files, description="Loading documents..."):
        try:
            loader_class = LOADERS[file_path.suffix.lower()]
            loader = loader_class(str(file_path))
            docs = loader.load()

            # Tag each document chunk with its source filename
            for doc in docs:
                doc.metadata["source"] = file_path.name

            all_documents.extend(docs)
            console.print(f"  [green]✔[/green] Loaded: {file_path.name} ({len(docs)} page(s))")

        except Exception as e:
            console.print(f"  [red]✘ Failed to load {file_path.name}: {e}[/red]")

    console.print(f"\n[bold green]✅ Total pages/sections loaded: {len(all_documents)}[/bold green]")
    return all_documents


def chunk_documents(documents: list) -> list:
    """
    Split documents into smaller overlapping chunks for better retrieval.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    console.print(f"[bold cyan]✂️  Split into {len(chunks)} chunks "
                  f"(size={config.CHUNK_SIZE}, overlap={config.CHUNK_OVERLAP})[/bold cyan]")
    return chunks


def get_embedding_model():
    """
    Returns a HuggingFace embedding model (runs locally, no API key needed).
    Uses 'all-MiniLM-L6-v2' — fast, lightweight, good quality.
    """
    console.print("[cyan]🔄 Loading embedding model (HuggingFace all-MiniLM-L6-v2)...[/cyan]")
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
    )


def build_vector_store(chunks: list) -> Chroma:
    """
    Embed all chunks and store them in ChromaDB (persisted to disk).
    """
    embedding_model = get_embedding_model()

    console.print(f"[cyan]💾 Building vector store at: {config.VECTOR_DB_PATH}[/cyan]")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=config.VECTOR_DB_PATH,
        collection_name="idm_knowledge_base",
    )
    console.print(f"[bold green]✅ Vector store built with {len(chunks)} chunks![/bold green]")
    return vector_store


def load_existing_vector_store() -> Chroma:
    """
    Load an already-built vector store from disk (no re-ingestion needed).
    """
    embedding_model = get_embedding_model()
    vector_store = Chroma(
        persist_directory=config.VECTOR_DB_PATH,
        embedding_function=embedding_model,
        collection_name="idm_knowledge_base",
    )
    return vector_store


def is_vector_store_ready() -> bool:
    """
    Check if a vector store already exists on disk.
    """
    return Path(config.VECTOR_DB_PATH).exists()


def run_ingestion():
    """
    Full ingestion pipeline: Load → Chunk → Embed → Store.
    Call this once (or whenever documents are updated).
    """
    console.print("\n[bold magenta]━━━ Identity Manager RAG — Document Ingestion ━━━[/bold magenta]\n")
    documents = load_documents(config.DOCS_FOLDER)
    if not documents:
        return
    chunks = chunk_documents(documents)
    build_vector_store(chunks)
    console.print("\n[bold green]🎉 Ingestion complete! Knowledge base is ready.[/bold green]\n")
