# Vectorless RAG Chatbot (PageIndex)

## 1. Project Overview

This project is a **Vectorless RAG (Retrieval Augmented Generation) chatbot** built using the **PageIndex library**.

Unlike traditional RAG systems that rely on embeddings and vector databases, this system performs **reasoning-based retrieval directly on document pages**.

Users can upload documents and ask questions about them.
The system retrieves relevant pages and generates answers using an LLM.

The goal of the project is to demonstrate **modern RAG architecture without vector databases**.

---

# 2. Core Features

### Document Upload

Users should be able to upload documents.

Supported formats:

* PDF
* DOCX
* TXT

Uploaded files should be stored locally.

---

### Document Parsing

Documents must be parsed into **pages or logical sections**.

Expected output format:

```
[
  {
    "page": 1,
    "text": "Page content"
  },
  {
    "page": 2,
    "text": "Page content"
  }
]
```

PDF → split by pages
DOCX → split by paragraphs or sections
TXT → split every 800–1200 characters

---

### PageIndex Indexing

After parsing, the system should create a **PageIndex instance**.

Responsibilities:

* Store document pages
* Allow retrieval using natural language queries

Example usage:

```
index = PageIndex()

index.add_pages(pages)

results = index.search(query)
```

Search results should return **relevant page numbers and text**.

---

### Chat Query System

Users ask questions about the uploaded document.

The query pipeline should work as follows:

1. Receive user question
2. Retrieve relevant pages using PageIndex
3. Select top 3–5 pages
4. Send those pages to the LLM
5. Generate an answer
6. Return the answer with citations

---

### LLM Prompt Format

The prompt sent to the LLM should include retrieved pages.

Example:

```
You are an assistant answering questions about a document.

Use only the context below.

If the answer is not present, say "I cannot find the answer in the document."

Context:
{retrieved_pages}

Question:
{user_question}
```

---

# 3. System Architecture

Frontend: Next.js
Backend: FastAPI
AI Retrieval: PageIndex
LLM: OpenAI GPT-4o

Architecture Flow:

User → Frontend → Backend API → PageIndex → LLM → Response

---

# 4. Backend Structure

Backend should be written in **Python using FastAPI**.

Expected directory structure:

```
backend/
  app/
    main.py
    document_loader.py
    rag_engine.py
    query_engine.py
    models.py
    config.py
```

Responsibilities:

main.py
Defines API endpoints.

document_loader.py
Handles parsing of uploaded documents.

rag_engine.py
Handles PageIndex creation and retrieval.

query_engine.py
Handles question answering logic.

models.py
Pydantic request/response models.

config.py
Stores environment configuration.

---

# 5. API Endpoints

## Upload Document

POST /upload

Accepts:

multipart/form-data

file

Response:

```
{
  "document_id": "uuid",
  "pages": 24
}
```

---

## Chat With Document

POST /chat

Request:

```
{
  "document_id": "uuid",
  "question": "What is the main topic?"
}
```

Response:

```
{
  "answer": "...",
  "sources": [
    { "page": 4 },
    { "page": 7 }
  ]
}
```

---

## List Documents

GET /documents

Response:

```
[
  {
    "document_id": "...",
    "filename": "...",
    "pages": 10
  }
]
```

---

# 6. Frontend Requirements

Frontend should be built using:

* Next.js
* Tailwind CSS
* Shadcn UI

Features required:

Document Upload UI
Chat Interface
Message Streaming
Source Citation Display

---

# 7. UI Layout

Pages:

```
/
Upload Document

/chat
Chat with document
```

Chat layout should be similar to ChatGPT:

Left side:

document selector

Main area:

chat conversation

Bottom:

message input box

---

# 8. Data Storage

Documents should be stored in:

```
/storage/documents
```

Indexes should be stored in:

```
/storage/indexes
```

For MVP, storage can be local.

---

# 9. Environment Variables

Create a `.env` file.

Variables required:

```
OPENAI_API_KEY=
MODEL_NAME=gpt-4o-mini
MAX_CONTEXT_PAGES=5
```

---

# 10. Error Handling

The system should gracefully handle:

Invalid file uploads
Unsupported formats
Empty queries
LLM API failures

---

# 11. Logging

Backend should log:

Document uploads
Index creation
Queries
LLM responses

---

# 12. Deployment

Frontend:

Vercel

Backend:

Railway or Render

---

# 13. Future Improvements

Multi-document chat
Conversation memory
Streaming responses
Document summaries
Page highlighting

---

# 14. Non Goals

This project does NOT require:

Vector databases
Embeddings
Semantic search libraries

The system must rely on **PageIndex retrieval only**.

---

# 15. Development Guidelines

Code must follow:

Clean architecture
Modular structure
Type hints
Clear comments

Cursor should prioritize **simple readable code** over heavy abstractions.

---
