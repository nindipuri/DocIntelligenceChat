# DocIntelligenceChat Frontend

Next.js UI for uploading documents and chatting with them.

## Run

```bash
npm install
npm run dev
```

Open http://localhost:3000

**Backend must be running** on http://127.0.0.1:8000 (see `backend/README.md`).

## Pages

- **/** — Upload documents (PDF, DOCX, TXT). Drag & drop or click to browse.
- **/chat** — Select a document and ask questions. Answers include source page citations.

## API proxy

The frontend proxies `/api/*` to the backend. To use a different backend URL, set:

```
NEXT_PUBLIC_API_URL=http://your-backend:8000
```

Then use `fetch(\`${NEXT_PUBLIC_API_URL}/upload\`, ...)` — update `src/lib/api.ts` to use this base when set.
