# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Manarah (منارة)** is an AI-powered content moderation system for Saudi social media. It detects violations in videos and images across three main categories: bullying, child/worker exploitation, and hate speech (profanity, wealth bragging, tribal/sectarian/racist contsent).

The system consists of two separate applications:

1. **Backend** (`capstone-project-manarah-backend/`) - Python FastAPI server with OpenAI integration
2. **Frontend** (`capstone-project-manarah/`) - React + Vite dashboard

## Development Commands

### Backend (Python FastAPI)

```bash
# Navigate to backend
cd capstone-project-manarah-backend

# Install dependencies
pip install -r requirements.txt

# Set up environment (required)
cp .env.example .env
# Edit .env and add OPENAI_API_KEY

# Run development server
python -m uvicorn src.main:app --reload --port 8000

# Run tests
python test_api_endpoints.py
pytest tests/

# Run with debug logging
uvicorn src.main:app --reload --port 8000 --log-level debug
```

### Frontend (React + Vite)

```bash
# Navigate to frontend
cd capstone-project-manarah

# Install dependencies
npm install

# Run development server (with proxy to backend)
npm run dev

# Run mock server (for testing without backend)
npm run mock

# Build for production
npm run build

# Preview production build
npm run preview
```

### Running Full Stack

The frontend proxies `/api` requests to `http://127.0.0.1:8000` (backend). Start both servers:

1. Terminal 1: `cd capstone-project-manarah-backend && python -m uvicorn src.main:app --reload --port 8000`
2. Terminal 2: `cd capstone-project-manarah && npm run dev`
3. Access frontend at http://localhost:5173

## Architecture

### Backend Processing Pipeline

```
Upload → Extract Frames/Audio → Vision Analysis → Text Analysis → Decision → Action
                                      ↓                ↓
                                 GPT-4o Vision    Whisper + GPT-4
```

**Key modules:**
- `src/main.py` - FastAPI endpoints and CORS configuration
- `src/preprocessor.py` - Video/image processing with FFmpeg (frame extraction at 15 FPS, sampled every 3rd frame for analysis)
- `src/vision_analyzer.py` - GPT-4o vision analysis of frames/images
- `src/text_analyzer.py` - Whisper audio transcription + GPT-4 text analysis
- `src/decision_engine.py` - Scoring and action routing with hard rules
- `src/storage.py` - JSON-based persistence (local files in `data/` directory)
- `src/config.py` - Environment-based configuration with Pydantic

**Processing is asynchronous:**
- Upload returns 202 immediately with `content_id`
- Analysis runs in background task (60-90 seconds for 30s video)
- Frontend polls `/api/v1/content/{content_id}/status` for updates

### Decision Logic

**Scoring:**
- Videos: `combined_score = (vision × 0.6) + (text × 0.4)`
- Images: `combined_score = (vision × 0.7) + (text × 0.3)`

**Actions (configurable thresholds in `.env`):**
- Score ≥0.85 → `auto_remove` (High priority)
- Score 0.60-0.85 → `human_review` (Medium priority)
- Score 0.40-0.60 → `warning` (Low priority)
- Score <0.40 → `allow`

**Hard Rules** (override scoring):
- Child exploitation + confidence >0.80 → Force human review
- Hate symbols + confidence >0.90 → Auto-remove
- Multiple violations (2+) with confidence >0.85 → Force review

### Frontend Structure

- **Pages:**
  - `/` - Home page (landing)
  - `/realtime` - Live SSE feed of violations (uses `mock-server.js` in dev)
  - `/autoscan` - Manual video/image upload for analysis (calls `/api/v1/content/upload`)
  - `/dashboard` - Charts and metrics (Chart.js + react-chartjs-2)
  - `/members` - Team information

- **Components:**
  - `Header.jsx` - Navigation bar
  - `Splash.jsx` - Route transition animations
  - Components in `src/components/`

- **Routing:** React Router v6 (`react-router-dom`)
- **Styling:** Custom CSS (`src/styles.css`) with Saudi color palette (Green #006C35, Sand #EDE6D5)
- **Theme:** RTL layout, Najdi Sadu design elements

### API Endpoints

**Backend (FastAPI):**
- `POST /api/v1/content/upload` - Upload video/image (returns `content_id`, status 202)
- `GET /api/v1/content/{content_id}/status?user_id={user_id}` - Check processing status
- `GET /api/v1/content/{content_id}/details?user_id={user_id}` - Get full analysis results

**Mock Server (Node.js):**
- `GET /api/events` - SSE stream for realtime page (runs on port 7070)

## Important Configuration

### Backend `.env` Variables

Required:
- `OPENAI_API_KEY` - OpenAI API key (must be set)

Optional (with defaults):
- `API_PORT=8000`
- `MAX_UPLOAD_SIZE_MB=500`
- `FRAME_EXTRACTION_FPS=15` - Frames extracted per second
- `AUTO_REMOVE_THRESHOLD=0.85`
- `REVIEW_THRESHOLD=0.60`
- `WARNING_THRESHOLD=0.40`

### Frontend Proxy Configuration

Located in `capstone-project-manarah/vite.config.js`:
- Proxies `/api` to `http://127.0.0.1:8000`
- Change `target` if backend runs on different port/host

### CORS Settings

Backend allows origins: `http://localhost:5173`, `http://localhost:3000`, `http://127.0.0.1:5173`, `http://127.0.0.1:3000`

Add more origins in `src/main.py` if needed.

## Dependencies

**Backend requires:**
- Python 3.11+
- FFmpeg (for video processing) - must be installed separately
- OpenAI API key

**Frontend requires:**
- Node.js
- npm

## Data Storage

Backend uses local JSON files (not production-ready):
- `data/content/{user_id}/{content_id}/` - Uploaded files, frames, audio
- `data/analysis/{user_id}/{content_id}.json` - Analysis results
- `data/decisions/{user_id}/{content_id}.json` - Decision results
- `data/audit/{date}/events.jsonl` - Audit log

**User ID is required** for all API calls to isolate data between users and prevent cross-user access.

## Cost Optimization

Video analysis is expensive (~$1.50 per 30s video):
- Frames extracted at 15 FPS (450 frames for 30s)
- Sampled every 3rd frame (150 frames analyzed, 5 FPS effective)
- Adjust sample rate in `src/vision_analyzer.py` or FPS in `.env` to reduce costs

## Violation Categories

1. **Bullying & Mockery** - Offensive gestures, mocking, harassment
2. **Child Exploitation** - Child as main subject (>40% frame), performing for camera
3. **Worker Exploitation** - Domestic workers in content
4. **Vulgar Language** - Profanity, sexual terms
5. **Wealth Bragging** - Cash stacks, luxury items
6. **Tribal Incitement** - Tribal superiority claims
7. **Sectarian Content** - Sectarian division
8. **Racism** - Racial slurs, ethnic mockery

## Troubleshooting

**Backend won't start:**
- Verify FFmpeg is installed: `ffmpeg -version`
- Check `.env` has valid `OPENAI_API_KEY`
- Ensure port 8000 is not in use

**Frontend API calls failing:**
- Confirm backend is running on port 8000
- Check browser console for CORS errors
- Verify Vite proxy configuration

**Processing takes too long:**
- Videos: 60-90 seconds is normal for 30s video
- Check OpenAI API quota and rate limits
- Review `data/audit/{date}/events.jsonl` for errors

**Mock server for realtime page:**
- Run `npm run mock` separately (port 7070)
- Used for development/demo without backend

## API Documentation

When backend is running:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
