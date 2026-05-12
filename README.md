# 🤖 Identity Manager RAG Chatbot

An AI-powered CLI chatbot that answers questions about Identity Manager
using your existing help documentation — powered by RAG (Retrieval-Augmented Generation).

---

## 📁 Project Structure

```
idm-rag-chatbot/
│
├── main.py          → Entry point (run this)
├── chatbot.py       → CLI chatbot interface
├── rag_pipeline.py  → RAG query logic (retrieve + generate)
├── ingestion.py     → Document loading, chunking, embedding
├── config.py        → All configuration settings
├── requirements.txt → Python dependencies
├── .env.example     → Copy this to .env and fill in your keys
│
├── docs/            → 📂 PUT YOUR HELP DOCUMENTS HERE
│   └── (PDF, DOCX, HTML, TXT files)
│
└── vector_store/    → Auto-created after first ingestion (ChromaDB)
```

---

## ⚙️ Setup Instructions

### 1. Clone / Download the project

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and fill in your API key and settings
```

### 5. Add your Identity Manager help documents
```
Copy all your PDF / DOCX / HTML / TXT help files into the /docs folder
```

### 6. Run ingestion (first time only)
```bash
python main.py --ingest
```

### 7. Start the chatbot
```bash
python main.py
```

---

## 💬 Example Questions

```
You: How do I perform a Privileged Certification?
You: What is the process to provision access for a new joiner?
You: How do I revoke a role from a user?
You: What does the Certification History report show?
```

---

## 🔧 CLI Commands

| Command     | Description                              |
|-------------|------------------------------------------|
| `/help`     | Show available commands                  |
| `/stats`    | Show session feedback statistics         |
| `/reingest` | Re-ingest docs after updates             |
| `/sources`  | Show the configured docs folder          |
| `/exit`     | Exit the chatbot                         |

---

## 🔄 Updating the Knowledge Base

When help documents are added or updated:
```bash
python main.py ingest-only
```
Or from within the chatbot, type `/reingest`.

---

## 🔐 LLM Provider Options

| Provider  | Model                      | Set in .env              |
|-----------|----------------------------|--------------------------|
| Anthropic | claude-3-5-sonnet-20241022 | LLM_PROVIDER=anthropic   |
| OpenAI    | gpt-4o                     | LLM_PROVIDER=openai      |

---

## 🏗️ Architecture

```
User Query
    │
    ▼
Embedding (HuggingFace all-MiniLM-L6-v2)
    │
    ▼
Similarity Search (ChromaDB)
    │
    ▼
Top-K Relevant Chunks Retrieved
    │
    ▼
Prompt = System Prompt + Context + Query
    │
    ▼
LLM (Claude / GPT-4o)
    │
    ▼
Answer + Source Citation → User
```,,
