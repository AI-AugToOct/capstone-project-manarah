# Manarah (منارة) - Content Moderation System

**AI-powered backend system for automated detection of violations in Saudi social media content**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)](https://openai.com/)

---

## 📋 Overview

Manarah is a backend API system that automatically detects three types of violations in Saudi social media content:
1. **Bullying and Mockery** (التنمر والاستهزاء)
2. **Child & Worker Exploitation** (استغلال الأطفال والعاملين)
3. **Hate Speech** (الكراهية: profanity, wealth bragging, tribal/sectarian/racist content)

### How It Works

```
Upload Content → Extract Frames/Audio → AI Analysis → Decision → Action
                                      ↓                ↓
                               GPT-4o (Vision)   GPT-4 (Text)
                               Whisper (Audio)
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** installed
- **FFmpeg** installed ([Download here](https://ffmpeg.org/download.html))
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd manarah3
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=sk-proj-your-key-here
   ```

4. **Run the server**
   ```bash
   python -m uvicorn src.main:app --reload --port 8000
   ```

5. **Test the API**
   
   Open your browser: http://localhost:8000
   
   API Documentation: http://localhost:8000/docs

---

## 📚 API Usage

### 1. Upload Content

```bash
curl -X POST "http://localhost:8000/api/v1/content/upload" \
  -F "file=@video.mp4" \
  -F "user_id=user123" \
  -F "caption=Optional caption text"
```

**Response:**
```json
{
  "content_id": "abc-123-def-456",
  "status": "processing",
  "message": "Content uploaded successfully and queued for analysis"
}
```

### 2. Check Status

```bash
curl "http://localhost:8000/api/v1/content/{content_id}/status?user_id=user123"
```

**Response:**
```json
{
  "content_id": "abc-123-def-456",
  "status": "completed",
  "decision": {
    "action": "human_review",
    "score": 0.72,
    "reason": "Medium violation score requires human review"
  },
  "processed_at": "2025-10-05T10:30:00Z"
}
```

### 3. Get Details

```bash
curl "http://localhost:8000/api/v1/content/{content_id}/details?user_id=user123"
```

**Response includes:**
- Vision analysis results (frame-by-frame violations)
- Text analysis results (transcript + caption violations)
- Decision details (action, scores, reasoning)
- Evidence files (frame paths, audio path)

---

## 🏗️ Project Structure

```
manarah3/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app & endpoints
│   ├── config.py            # Configuration management
│   ├── storage.py           # JSON-based data persistence
│   ├── preprocessor.py      # Video/image processing
│   ├── vision_analyzer.py   # GPT-4o vision analysis
│   ├── text_analyzer.py     # Whisper + GPT-4 text analysis
│   ├── decision_engine.py   # Scoring & action routing
│   └── utils.py             # Retry logic & error handling
├── data/
│   ├── content/             # Uploaded files & frames
│   ├── analysis/            # Analysis results (JSON)
│   ├── decisions/           # Decisions (JSON)
│   └── audit/               # Audit logs (JSONL)
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── .gitignore
└── README.md
```

---

## ⚙️ Configuration

Edit `.env` file to customize:

```bash
# OpenAI API (REQUIRED)
OPENAI_API_KEY=sk-proj-your-key-here

# Application Settings
API_PORT=8000
MAX_UPLOAD_SIZE_MB=500
FRAME_EXTRACTION_FPS=15

# Decision Thresholds (tunable)
AUTO_REMOVE_THRESHOLD=0.85    # Score ≥0.85 → Auto-remove
REVIEW_THRESHOLD=0.60         # Score 0.60-0.85 → Human review
WARNING_THRESHOLD=0.40        # Score 0.40-0.60 → Warning
                              # Score <0.40 → Allow
```

---

## 🎯 Violation Categories

### 1. Bullying & Mockery
- Offensive gestures, mocking expressions
- Insulting text overlays
- Harassment messages

### 2. Child Exploitation
- Child as main content subject (>40% frame)
- Child performing for camera
- Monetization of children

### 3. Worker Exploitation
- Domestic workers as content subjects
- Workers in staged scenarios

### 4. Vulgar Language
- Profanity, sexual terms, curses

### 5. Wealth Bragging
- Cash stacks, luxury items display
- Ostentatious wealth showcasing

### 6. Tribal Incitement
- Tribal superiority claims
- Divisive tribal content

### 7. Sectarian Content
- Sectarian division, mockery

### 8. Racism
- Racial slurs, ethnic mockery
- Discriminatory content

---

## 📊 Decision Logic

### Scoring Formula

**Videos:** `combined_score = (vision × 0.6) + (text × 0.4)`

**Images:** `combined_score = (vision × 0.7) + (text × 0.3)`

### Actions

| Score Range | Action | Priority |
|-------------|--------|----------|
| ≥0.85 | Auto-remove | High |
| 0.60-0.85 | Human review | Medium |
| 0.40-0.60 | Warning | Low |
| <0.40 | Allow | None |

### Hard Rules (Override Scoring)

1. **Child exploitation + confidence >0.80** → Force human review
2. **Hate symbols + confidence >0.90** → Auto-remove
3. **Multiple violations (2+) with confidence >0.85** → Force review

---

## 💰 Cost Estimation

**For a 30-second video:**
- Frames extracted: 30s × 15 fps = 450 frames
- Sampled for analysis: 450 ÷ 3 = 150 frames (5 fps effective)
- Vision analysis: 150 × $0.01 = **$1.50**
- Audio transcription: 30s = **$0.003**
- Text analysis: **$0.002**
- **Total: ~$1.50 per video**

**Cost reduction strategies:**
- Increase sample rate (analyze fewer frames)
- Process shorter clips initially
- Batch process during off-peak hours

---

## 🧪 Testing

### Run Test

Place test videos in `tests/data/` directory and run:

```bash
python tests/test_pipeline.py
```

### Test Scenarios

1. **Child content** - Expected: human_review (score 0.70-0.90)
2. **Wealth bragging** - Expected: auto_remove (score >0.85)
3. **Bullying** - Expected: human_review (score 0.65-0.80)
4. **Safe content** - Expected: allow (score <0.40)

---

## 🛠️ Development

### Install FFmpeg

**Windows:** Download from https://ffmpeg.org/download.html

**Mac:** `brew install ffmpeg`

**Linux:** `sudo apt install ffmpeg`

### Run in Development Mode

```bash
uvicorn src.main:app --reload --port 8000 --log-level debug
```

### View Logs

Logs are automatically created in the console. For file logging, configure in `src/main.py`.

---

## 📈 Performance

### Expected Processing Times

| Content Type | Duration | Processing Time |
|--------------|----------|-----------------|
| Image | - | 3-5 seconds |
| Video (30s) | 30 seconds | 60-90 seconds |
| Video (60s) | 60 seconds | 120-180 seconds |

*Note: Processing time scales with video length due to frame analysis*

### Optimization Tips

1. **Reduce FPS**: Change `FRAME_EXTRACTION_FPS` in `.env` (15 → 10 fps)
2. **Sample rate**: Increase sample rate in vision analyzer (3 → 5)
3. **Parallel processing**: Deploy multiple instances behind load balancer

---

## 🔒 Security

- API keys stored in environment variables (never hardcoded)
- Input validation on all endpoints
- File type and size restrictions
- Local file storage with proper permissions
- Parameterized queries (when migrating to DB)

---

## 🚧 Known Limitations

1. **Processing time**: Videos take 60-90s due to 450 frames/30s
2. **Cost**: ~$1.50 per 30s video (can be reduced with sampling)
3. **Language support**: Arabic and English only
4. **No real-time analysis**: Asynchronous processing required
5. **Local storage**: Not scalable for production (migrate to cloud)

---

## 🔄 Migration Path (Future)

**Current (MVP):** Local filesystem + JSON files

**Production:** AWS S3 + PostgreSQL

**Migration steps in PRD section 15.3**

---

## 📝 License

[Specify your license here]

---

## 🤝 Contributing

[Add contribution guidelines]

---

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

---

## 📖 Additional Resources

- **Product Requirements Document:** `manarah_prd_clean.md`
- **API Documentation:** http://localhost:8000/docs (when running)
- **OpenAI API Docs:** https://platform.openai.com/docs

---

**Built with ❤️ for Saudi social media content moderation**
