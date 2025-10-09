# Manarah (منارة) - AI Content Moderation System

**AI-powered content moderation for Saudi social media.** Manarah analyzes images and videos to detect bullying, child/worker exploitation, and hate speech (profanity, wealth bragging, tribal/sectarian/racist content).

This repository contains two applications:
- Backend — Python FastAPI server (folder: `backend/`)
- Frontend — React + Vite dashboard (folder: `Front-end/`)

---

## Quick Start

Prerequisites
- Python 3.11+
- Node.js (v18+ recommended) and npm
- FFmpeg installed on your machine (brew install ffmpeg on macOS)
- OpenAI API Key (if you plan to call the real models)

### Backend (Python FastAPI)

```bash
# filepath: backend/README (commands)
cd backend
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
pip install -r requirements.txt
cp .env.example .env             # add OPENAI_API_KEY and adjust thresholds as needed

# Run development server
python -m uvicorn src.main:app --reload --port 8000

# Run tests
pytest tests/
# or run single test file
python test_api_endpoints.py
```

Important backend files: `backend/src/main.py`, `backend/src/preprocessor.py`, `backend/src/vision_analyzer.py`, `backend/src/text_analyzer.py`, `backend/src/decision_engine.py`, `backend/src/storage.py`, `backend/src/config.py`.

### Frontend (React + Vite)

```bash
# filepath: Front-end/README (commands)
cd Front-end
npm install
cp .env.example .env             # set VITE_API_URL if needed

# Development
npm run dev

# Mock realtime server (dev-only, serves SSE for /api/events)
node mock-server.js

# Build / preview
npm run build
npm run preview
```

By default the Vite dev server runs on http://localhost:5173 and is configured to proxy `/api` to the backend at http://127.0.0.1:8000 (see `Front-end/vite.config.js`).

### Running Full Stack

1. Terminal 1 — Backend
   - cd backend && source .venv/bin/activate && python -m uvicorn src.main:app --reload --port 8000
2. Terminal 2 — Frontend
   - cd Front-end && npm run dev
3. Open the frontend: http://localhost:5173

The frontend proxies API calls starting with `/api` to `http://127.0.0.1:8000`. If you run the backend on a different host/port, update `Front-end/vite.config.js` or set VITE_API_URL accordingly.

---

## Architecture

Processing pipeline (asynchronous):

Upload → Extract Frames & Audio → Vision Analysis → Text Analysis → Decision Engine → Action

- Upload returns HTTP 202 with a `content_id`.
- Analysis runs in background and the frontend polls `/api/v1/content/{content_id}/status` for updates.
- Typical processing time: ~60–90s for a 30s video (depends on sampling, FFmpeg, and API latency).

Key backend modules (backend/src/)
- main.py — FastAPI app, endpoints, background tasks, CORS
- preprocessor.py — frame & audio extraction (FFmpeg)
- vision_analyzer.py — frame/image analysis (GPT-4o Vision integration)
- text_analyzer.py — Whisper transcription + GPT-4 text analysis
- decision_engine.py — combines vision/text scores, applies thresholds & hard rules
- storage.py — local JSON persistence for content, analysis, decisions
- config.py — Pydantic settings read from `.env`

Decision logic
- Scoring
  - Videos: combined_score = (vision × 0.6) + (text × 0.4)
  - Images:  combined_score = (vision × 0.7) + (text × 0.3)
- Action thresholds (configurable in `.env`)
  - ≥ 0.85 → auto_remove
  - 0.60–0.85 → human_review
  - 0.40–0.60 → warning
  - < 0.40 → allow
- Hard rules (override scoring)
  - Child exploitation + confidence > 0.80 → force human review
  - Hate symbols + confidence > 0.90 → auto-remove
  - Multiple violations (2+) + confidence > 0.85 → force review

---

## Frontend Structure

Folder: `Front-end/src/`

Pages
- / (Home) — Landing
- /realtime — Live / SSE feed of violations (uses `mock-server.js` in dev)
- /autoscan — Manual upload for image/video analysis
- /dashboard — Charts and metrics (Chart.js)
- /members — Team info

Components
- Header.jsx — navigation
- Splash.jsx — page transitions
- NotificationCard.jsx — result/notification UI
- Custom CSS located in `Front-end/src/styles.css` (RTL layout, Saudi palette & Sadu design elements)

Routing
- React Router v6 is used (see App.jsx / main.jsx).

---

## API Endpoints

Backend (FastAPI) — default base: http://127.0.0.1:8000

- POST /api/v1/content/upload
  - multipart/form-data: file, user_id, caption?
  - Returns: 202 Accepted with JSON { content_id, status: "processing" }
- GET /api/v1/content/{content_id}/status?user_id={user_id}
  - Poll for processing status
- GET /api/v1/content/{content_id}/details?user_id={user_id}
  - Full analysis & decision JSON
- GET /healthz
  - Health check

Mock Server (dev)
- Frontend mock-server.js:
  - GET /api/events  — SSE endpoint used by realtime page (runs on port 7070 when started via node)

---

## Configuration

Backend `.env` (see `backend/.env.example`)
- Required
  - OPENAI_API_KEY
- Optional (defaults in code)
  - API_PORT=8000
  - FRAME_EXTRACTION_FPS=15
  - AUTO_REMOVE_THRESHOLD=0.85
  - REVIEW_THRESHOLD=0.60
  - WARNING_THRESHOLD=0.40
  - ALLOWED_ORIGINS (comma-separated)

Frontend `.env` (see `Front-end/.env.example`)
- VITE_API_URL (optional; proxy in vite config handles local dev)

CORS
- Backend allows origins for Vite dev host by default; add origins in `backend/src/main.py` or via ALLOWED_ORIGINS.

---

## Data Storage

Backend stores data locally under `backend/data/` (JSON & media)
- data/content/{user_id}/{content_id}/ — uploaded files, frames, audio
- data/analysis/{user_id}/{content_id}.json — analysis results
- data/decisions/{user_id}/{content_id}.json — decision output
- data/audit/{date}/events.jsonl — audit log

Note: local JSON storage is for development/demo only. Migrate to a DB/S3 for production.

---

## Cost & Optimization

Estimated cost per 30s video (approximate)
- Vision analysis (sampled frames) — ~$1.50
- Whisper transcription — negligible (~$0.003)
- Text reasoning — negligible

Optimization strategies
- Reduce FRAME_EXTRACTION_FPS (e.g., 15 → 10)
- Increase sampling interval (analyze fewer frames)
- Analyze only first N seconds when appropriate
- Batch requests and off-peak processing

---

## Violation Categories

1. Bullying & Mockery
2. Child Exploitation
3. Worker Exploitation
4. Vulgar Language
5. Wealth Bragging
6. Tribal Incitement
7. Sectarian Content
8. Racism

---

## Testing

Backend tests: `backend/tests/` (pytest)
- Run: cd backend && pytest

Manual test
1. Start backend and frontend
2. Open http://localhost:5173 → Auto Scan
3. Upload image/video with user_id and observe status polling and result details

---

## Docker (optional)

There are Dockerfiles and docker-compose files in the repo for containerized development. See `docker-compose.dev.yml` (if present) or the Dockerfiles in `backend/` and `Front-end/`. Typical command:

```bash
docker compose -f docker-compose.dev.yml up --build
```

---

## Troubleshooting

- Backend won't start: ensure FFmpeg installed: ffmpeg -version
- Missing OPENAI_API_KEY: copy `.env.example` and add key
- CORS: add frontend origin(s) to ALLOWED_ORIGINS
- Ports in use: lsof -i :8000 or lsof -i :5173

---

## References & Docs

- Interactive API docs (when backend running): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Acknowledgments

Built with FastAPI, React, Vite, OpenAI (GPT & Whisper), and FFmpeg.

---

