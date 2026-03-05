# DocIntelligenceChat

Vectorless RAG chatbot: upload documents (PDF, DOCX, TXT) and ask questions. Uses reasoning-based retrieval — no vector DB.

## Quick start

1. **Backend** (terminal 1):
   ```bash
   cd backend
   source .venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. **Frontend** (terminal 2):
   ```bash
   cd frontend
   npm install && npm run dev
   ```

3. Open **http://localhost:3000**
   - Upload a document on the home page
   - Go to Chat, select the document, and ask questions

## Deploy to a server

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for step-by-step instructions to deploy on Railway + Vercel (or Render + Vercel) so anyone can use it remotely.

## Requirements

- Python 3.10+
- Node.js 18+
- `OPENAI_API_KEY` in `backend/.env`
