# Deploy DocIntelligenceChat

Deploy the backend and frontend so anyone can use it remotely.

---

## Prerequisites

- GitHub account
- [OpenAI API key](https://platform.openai.com/api-keys)
- Push your code to a GitHub repository

---

## Step 1: Deploy Backend (Railway)

1. Go to [railway.app](https://railway.app) → **Login** with GitHub.

2. **New Project** → **Deploy from GitHub repo** → select your repository.

3. Railway may auto-detect the app. If not:
   - **Settings** → **Root Directory**: `backend`
   - **Settings** → **Build Command**: `pip install -r requirements.txt`
   - **Settings** → **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Variables** → Add:
   - `OPENAI_API_KEY` = your OpenAI API key
   - `MODEL_NAME` = `gpt-4o-mini`
   - `MAX_CONTEXT_PAGES` = `5`

5. **Deploy** → wait for the build to finish.

6. **Settings** → **Networking** → **Generate Domain** → copy the URL (e.g. `https://xxx.up.railway.app`).

**Save this URL** — you need it for the frontend.

---

## Step 2: Deploy Backend (Render, alternative)

1. Go to [render.com](https://render.com) → **Login** with GitHub.

2. **New** → **Blueprint** → connect your repo (if you have `render.yaml` in the repo root).

   Or **New** → **Web Service**:
   - Connect repo
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Environment** → Add `OPENAI_API_KEY` (mark as secret).

4. Deploy → copy the service URL (e.g. `https://docintelligencechat-api.onrender.com`).

**Save this URL** — you need it for the frontend.

---

## Step 3: Deploy Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com) → **Login** with GitHub.

2. **Add New** → **Project** → import your repository.

3. **Configure Project**:
   - **Root Directory**: `frontend` (click Edit, set to `frontend`)
   - **Environment Variables**:
     - Name: `NEXT_PUBLIC_API_URL`
     - Value: your backend URL from Step 1 or 2 (e.g. `https://xxx.up.railway.app`)
     - No trailing slash

4. **Deploy** → wait for the build.

5. Copy your Vercel URL (e.g. `https://docintelligencechat.vercel.app`).

---

## Step 4: Share the demo

Share the **Vercel URL** with others. They can:

1. Open the link
2. Upload a document (PDF, DOCX, TXT)
3. Go to Chat and ask questions

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Failed to load documents" / CORS errors | Ensure `NEXT_PUBLIC_API_URL` is set correctly in Vercel and matches your backend URL exactly. |
| Backend cold start (Render free tier) | First request may take 30–60 seconds. Subsequent requests are faster. |
| Documents disappear after a while | Railway/Render use ephemeral storage. Documents are lost on restart. For persistent storage you’d need S3 or a database. |

---

## Quick reference

| Platform | Backend | Frontend |
|----------|---------|----------|
| Railway | Root: `backend`, Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` | — |
| Render | Root: `backend`, same start command | — |
| Vercel | — | Root: `frontend`, Env: `NEXT_PUBLIC_API_URL` |
