# Health Genie Demo

A standalone chatbot demo for the Health Vibe platform.
Rule-based conversation flow, no LLM, no database.

---

## Stack

| Layer    | Technology          |
|----------|---------------------|
| Frontend | Next.js 14 + TypeScript |
| Backend  | Python FastAPI      |

---

## Local development

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8010
```

### 2. Frontend

```bash
cd frontend
cp .env.local.example .env.local   # copy env file (already correct for local dev)
npm install
npm run dev -- --port 3005
```

### Local URLs

| Service      | URL                          |
|--------------|------------------------------|
| Frontend     | http://localhost:3005         |
| Backend      | http://localhost:8010         |
| FastAPI docs | http://localhost:8010/docs    |

---

## Environment variables

| Variable                   | Default                 | Description          |
|----------------------------|-------------------------|----------------------|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8010` | Backend API base URL |

Create `frontend/.env.local` (copy from `.env.local.example`) and set the
variable to your deployed backend URL before building for production.

---

## API contract

### `POST /api/chat`

**Request**
```json
{
  "session_id": "string | null",
  "current_step": "string | null",
  "selected_option": "string | null"
}
```

**Response**
```json
{
  "session_id": "string",
  "step": "string",
  "message": "string",
  "options": [{ "label": "string", "value": "string" }],
  "cta": { "label": "string", "url": "string" } | null
}
```

### `GET /health`

Returns `{"status": "ok"}`.

---

## Deployment

Frontend and backend are fully independent and can be deployed separately.

**Frontend** → Vercel, Netlify, or any Node host.
Set `NEXT_PUBLIC_API_BASE_URL` to your deployed backend URL before `npm run build`.

**Backend** → Railway, Render, Fly.io, or any Python host.
Run: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

Update `allow_origins` in `backend/app/main.py` to include your production
frontend domain before deploying.
