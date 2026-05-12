# config.py
# ============================================================
# Loads all configuration from the .env file
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

# LLM Provider
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")  # "openai" or "anthropic"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Paths
DOCS_FOLDER = os.getenv("DOCS_FOLDER", "./docs")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./vector_store")

# Chunking
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

# Retrieval
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 5))

# LLM Model names
OPENAI_MODEL = "gpt-4o"
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

# System prompt for the chatbot
SYSTEM_PROMPT = """You are a helpful AI assistant for the Identity Manager application.
Your job is to answer user questions based ONLY on the provided documentation context.

Rules:
- Answer only from the given context. Do not make up information.
- If the context does not contain the answer, say: "I don't have information on this in the current documentation. Please contact support."
- Keep answers clear, concise, and step-by-step where applicable.
- Always mention the source document name at the end of your answer.
"""
