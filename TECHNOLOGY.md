# Technology Stack

## Primary Language
**Python** — Core implementation language providing robust libraries for NLP, embeddings, and LLM integration.

## Architectural Pattern
**RAG (Retrieval-Augmented Generation)** — Combines document retrieval with generative AI to provide accurate, context-aware responses grounded in actual documentation.

## Key Dependencies

| Dependency | Purpose |
|------------|---------|
| **LangChain** | Framework for chaining LLM operations, embeddings, and vector store interactions |
| **ChromaDB** | Vector database for efficient document embedding storage and semantic search |
| **Sentence Transformers** | Generates high-quality embeddings for document and query vectors |
| **Anthropic** | Claude LLM integration for generation |
| **OpenAI** | GPT-4o LLM integration for generation |

## LLM Integration
**Multi-provider support** enables flexibility and redundancy:
- **Claude (Anthropic)** — Primary LLM for conversational AI
- **GPT-4o (OpenAI)** — Alternative LLM provider for generation

## Vector Database
**ChromaDB** — Persistent, disk-based vector store for document embeddings with fast semantic retrieval.

## Use Case
**Documentation-based Q&A Chatbot** — Enables users to ask natural language questions about documentation, retrieving relevant sections and generating contextual answers using retrieval-augmented generation.
