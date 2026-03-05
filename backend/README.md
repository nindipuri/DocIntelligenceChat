# DocIntelligenceChat Backend

FastAPI backend for the vectorless RAG chatbot. Upload documents (PDF, DOCX, TXT), index pages, and answer questions using reasoning-based retrieval and GPT.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

## Run

```bash
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs

## Endpoints

- **POST /upload** — Upload a document (multipart `file`). Returns `document_id` and `pages`.
- **POST /chat** — Body: `{ "document_id": "uuid", "question": "..." }`. Returns `answer` and `sources` (page numbers).
- **GET /documents** — List all documents with `document_id`, `filename`, `pages`.
- **GET /health** — Health check.

## Storage

- Uploaded files: `storage/documents/`
- Page indexes: `storage/indexes/` (JSON per document)

## Environment

| Variable           | Description              | Default       |
|--------------------|--------------------------|---------------|
| OPENAI_API_KEY     | OpenAI API key           | (required)    |
| MODEL_NAME         | Model for retrieval/QA   | gpt-4o-mini   |
| MAX_CONTEXT_PAGES  | Max pages in LLM context| 5             |
