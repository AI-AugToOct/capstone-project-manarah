# Manarah (منارة) AI Coding Agent Instructions

## Project Overview

**Manarah** is a Saudi social media content moderation system that uses OpenAI's GPT-4o (vision), GPT-4 (text), and Whisper (audio) to detect violations in uploaded videos and images. The system operates as a FastAPI backend with JSON-based local storage (MVP approach).

## Architecture

### Core Pipeline Flow
```
Upload → Preprocess → Vision Analysis → Decision → Action
                  ↓        ↓
              Audio → Text Analysis ↗
```

### Key Components

1. **`src/main.py`** - FastAPI app with 3 endpoints:
   - `POST /api/v1/content/upload` - Upload video/image
   - `GET /api/v1/content/{id}/status` - Check processing status
   - `GET /api/v1/content/{id}/details` - Get full analysis results

2. **`src/preprocessor.py`** - Handles uploads:
   - Extracts frames from videos at 15 fps using FFmpeg
   - Extracts audio as WAV (16kHz mono for Whisper)
   - Saves files to `data/content/{user_id}/{content_id}/`

3. **`src/vision_analyzer.py`** - GPT-4o integration:
   - Analyzes frames for visual violations (8 categories)
   - Returns violation score (0-1) + detailed violations array
   - Samples every 3rd frame by default (cost optimization)

4. **`src/text_analyzer.py`** - Whisper + GPT-4 integration:
   - Transcribes audio using Whisper API
   - Analyzes transcript + caption using GPT-4
   - Detects text-based violations

5. **`src/decision_engine.py`** - Scoring & routing:
   - Combines vision/text scores with weighted formula
   - Applies hard rules (child exploitation, hate symbols, multiple violations)
   - Routes to: `auto_remove`, `human_review`, `warning`, or `allow`

6. **`src/storage.py`** - JSON persistence:
   - `save_metadata()`, `load_metadata()` - Content metadata
   - `save_analysis()`, `load_analysis()` - AI analysis results
   - `save_decision()`, `load_decision()` - Moderation decisions
   - `append_audit_log()` - JSONL audit trail

7. **`src/config.py`** - Environment-based settings using Pydantic

## Critical Implementation Details

### Violation Categories (8 Total)

Defined in PRD section 3, implemented in prompts:
- `bullying` - Mockery, harassment, insults
- `child_exploitation` - Child as main content subject (>40% frame)
- `worker_exploitation` - Domestic workers in content
- `vulgar_language` - Profanity, sexual terms
- `wealth_bragging` - Ostentatious cash/luxury display
- `tribal` - Tribal superiority/division
- `sectarian` - Religious sect hatred
- `racism` - Race/ethnicity discrimination

### Decision Thresholds

```python
# Score ≥0.85 → Auto-remove
# Score 0.60-0.85 → Human review
# Score 0.40-0.60 → Warning
# Score <0.40 → Allow
```

### Scoring Formula

**Videos:** `(vision × 0.6) + (text × 0.4)`  
**Images:** `(vision × 0.7) + (text × 0.3)`

### Hard Rules (Override Scores)

1. Child exploitation + confidence >0.80 → Force review
2. Hate symbols + confidence >0.90 → Auto-remove
3. Multiple violations (2+) with confidence >0.85 → Force review

### Data Storage Structure

**No database** - Using JSON files:
```
data/
├── content/{user_id}/{content_id}/
│   ├── original.{mp4|jpg}
│   ├── frames/frame_0001.jpg, frame_0002.jpg, ...
│   ├── audio.wav
│   └── metadata.json
├── analysis/{content_id}.json
├── decisions/{content_id}.json
└── audit/{date}/events.jsonl
```

## Development Patterns

### When Adding Features

1. **Always use async processing** for content analysis (see `process_content_async` in `main.py`)
2. **Log audit events** using `append_audit_log()` for all major actions
3. **Update metadata status** (`processing` → `completed`/`failed`)
4. **Handle API failures gracefully** - Log and continue with partial results

### FFmpeg Usage

Extract frames:
```python
ffmpeg.input(video_path).filter('fps', fps=15).output(
    'frame_%04d.jpg', format='image2', vcodec='mjpeg', qscale=2
).run()
```

Extract audio:
```python
ffmpeg.input(video_path).output(
    audio_path, acodec='pcm_s16le', ar='16000', ac=1
).run()
```

### OpenAI API Calls

**GPT-4o Vision:**
```python
client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": [
        {"type": "text", "text": VISION_ANALYSIS_PROMPT},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
    ]}],
    temperature=0.2  # Low for consistency
)
```

**Whisper:**
```python
client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="ar"  # Arabic
)
```

### Error Handling

- **API failures**: Already handled in analyzers with try/except
- **Missing files**: Check `Path.exists()` before operations
- **Partial failures**: Continue processing (e.g., video with no audio)
- **Status tracking**: Update `metadata["status"]` to `failed` on errors

## Common Tasks

### Adding New Violation Category

1. Update prompts in `vision_analyzer.py` and `text_analyzer.py`
2. Add category to decision engine logic if special handling needed
3. Update PRD section 3 documentation

### Adjusting Thresholds

Edit `.env` file:
```
AUTO_REMOVE_THRESHOLD=0.85
REVIEW_THRESHOLD=0.60
WARNING_THRESHOLD=0.40
```

### Optimizing Costs

1. Increase frame sample rate in `vision_analyzer.py` (3 → 5 or 10)
2. Reduce FPS: `FRAME_EXTRACTION_FPS=10` in `.env`
3. Analyze shorter clips first

### Testing

Run server:
```bash
python -m uvicorn src.main:app --reload --port 8000
```

Upload test content:
```bash
curl -X POST "http://localhost:8000/api/v1/content/upload" \
  -F "file=@test.mp4" -F "user_id=test" -F "caption=test"
```

## Important Constraints

- **Must use**: GPT-4o for vision, GPT-4 for text, Whisper for audio (per PRD)
- **No custom ML models** allowed
- **Arabic language focus** - All prompts culturally aware for Saudi context
- **Local storage only** for MVP (migration to S3 + PostgreSQL later)
- **Async processing required** - Videos take 60-90 seconds to process

## File Naming Conventions

- Snake_case for Python files: `text_analyzer.py`
- PascalCase for classes: `VisionAnalyzer`, `DecisionEngine`
- Lowercase for functions: `analyze_frame()`, `save_metadata()`
- All JSON keys use snake_case: `content_id`, `violation_score`

## Configuration Management

All settings in `.env` → loaded via `src/config.py` → accessed as `settings.variable_name`

Never hardcode:
- API keys
- File paths
- Thresholds
- Port numbers

## Expected Performance

| Content | Processing Time | Cost |
|---------|----------------|------|
| Image | 3-5 seconds | $0.01 |
| Video (30s) | 60-90 seconds | $1.50 |

*Processing scales linearly with video length*

## Migration Path (Future Reference)

Current: Local JSON → Future: AWS S3 + PostgreSQL  
See PRD section 15.3 for migration steps

## References

- **Full specifications**: `manarah_prd_clean.md`
- **API docs**: http://localhost:8000/docs (when running)
- **OpenAI docs**: https://platform.openai.com/docs
