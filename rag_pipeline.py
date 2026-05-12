# rag_pipeline.py
# ============================================================
# Core RAG Pipeline:
#   1. Embeds the user query
#   2. Retrieves top-K relevant chunks from ChromaDB
#   3. Builds a prompt with context
#   4. Calls the LLM and returns the answer
# ============================================================

from langchain_community.vectorstores import Chroma
from langchain.schema import HumanMessage, SystemMessage

import config


def get_llm():
    """
    Returns the configured LLM client (Anthropic Claude or OpenAI GPT).
    """
    if config.LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=config.ANTHROPIC_MODEL,
            anthropic_api_key=config.ANTHROPIC_API_KEY,
            max_tokens=1024,
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=config.OPENAI_MODEL,
            openai_api_key=config.OPENAI_API_KEY,
            max_tokens=1024,
        )


def retrieve_context(vector_store: Chroma, query: str) -> tuple[str, list[str]]:
    """
    Searches the vector store for the most relevant chunks.

    Returns:
        - context_text: Combined text of retrieved chunks
        - sources: List of source document names
    """
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": config.TOP_K_RESULTS},
    )
    relevant_docs = retriever.invoke(query)

    if not relevant_docs:
        return "", []

    # Combine retrieved chunks into a single context block
    context_parts = []
    sources = []

    for i, doc in enumerate(relevant_docs, 1):
        source = doc.metadata.get("source", "Unknown")
        context_parts.append(f"[Chunk {i} — Source: {source}]\n{doc.page_content}")
        if source not in sources:
            sources.append(source)

    context_text = "\n\n---\n\n".join(context_parts)
    return context_text, sources


def build_prompt(context: str, query: str) -> list:
    """
    Constructs the message list to send to the LLM.
    System prompt enforces answer-from-context-only behavior.
    """
    user_message = f"""Use the following documentation context to answer the question.

CONTEXT:
{context}

QUESTION:
{query}
"""
    return [
        SystemMessage(content=config.SYSTEM_PROMPT),
        HumanMessage(content=user_message),
    ]


def ask(vector_store: Chroma, query: str, llm) -> dict:
    """
    Full RAG query flow:
        Query → Retrieve → Prompt → LLM → Answer

    Returns a dict with:
        - answer: The LLM's response
        - sources: Documents used to generate the answer
        - context_found: Whether relevant context was retrieved
    """
    # Step 1: Retrieve relevant context
    context, sources = retrieve_context(vector_store, query)

    if not context:
        return {
            "answer": "I don't have information on this in the current documentation. Please contact the support team.",
            "sources": [],
            "context_found": False,
        }

    # Step 2: Build prompt
    messages = build_prompt(context, query)

    # Step 3: Call LLM
    response = llm.invoke(messages)

    return {
        "answer": response.content,
        "sources": sources,
        "context_found": True,
    }
