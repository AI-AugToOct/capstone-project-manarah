# Manarah (منارة) - Content Moderation System
## Product Requirements Document

**Version:** 1.0  
**Date:** October 4, 2025  
**Status:** Final

---

## 1. EXECUTIVE SUMMARY

### 1.1 Product Vision
Backend system that automatically detects violations in Saudi social media content (videos, images, text) using AI vision and language models.

### 1.2 Problem Statement
Saudi social media platforms need automated detection of three violation types:
- Bullying and mockery
- Child and worker exploitation  
- Hate speech (profanity, wealth bragging, tribal/sectarian/racist content)

Manual moderation cannot scale and is inconsistent.

### 1.3 Solution Overview
API-based backend that:
1. Accepts content uploads
2. Analyzes using GPT-4o (vision) and GPT-4 (text)
3. Scores violations
4. Routes to actions (remove, review, warn, allow)
5. Stores evidence for audit

### 1.4 Success Metrics
- Detection accuracy: >85%
- Processing time: <30 seconds per video
- False positive rate: <15%
- Cost: <$0.02 per content item

---

## 2. SCOPE

### 2.1 In Scope
- Content upload API
- Frame extraction from videos
- Audio transcription
- Vision analysis (all violations)
- Text analysis (all violations)
- Decision engine with scoring
- Database storage
- Evidence preservation
- API endpoints for status/results

### 2.2 Out of Scope
- Frontend UI (already built)
- User authentication (frontend handles)
- Content delivery/streaming
- User management
- Payment processing
- Mobile apps
- Real-time live stream analysis

### 2.3 Technical Constraints
- Must use GPT-4o for vision (no custom ML models)
- Must use GPT-4 for text analysis
- Must use Whisper for audio transcription
- Must store media in AWS S3
- Must use PostgreSQL for metadata
- Backend framework: FastAPI (Python 3.11+)

---

## 3. VIOLATION DEFINITIONS

### 3.1 Violation Category 1: Bullying & Mockery (التنمر والاستهزاء)

**Definition:** Content that harasses, insults, mocks, or ridicules individuals or groups.

**Detection Criteria - Visual:**
- Offensive hand gestures (middle finger, rude signs)
- Mocking facial expressions toward camera
- Insulting text overlays on images
- Screenshots of harassment messages

**Detection Criteria - Text:**
- Direct insults: فاشل (failure), غبي (stupid), احذف حسابك (delete account)
- Mockery phrases: ما تستحي (aren't you ashamed)
- Repeated targeting of same individual
- Encouraging others to mock

**Detection Criteria - Audio:**
- Insulting tone with target's name
- Mocking laughter
- Repeated verbal harassment

**Severity Levels:**
- High: Threats, doxxing, severe insults
- Medium: Mockery, offensive gestures
- Low: Borderline rude comments

**Edge Cases:**
- Comedy/satire → Check if specific person targeted
- Friendly teasing → Assess relationship context
- Self-deprecating → NOT violation unless harmful

---

### 3.2 Violation Category 2: Child & Worker Exploitation

#### 3.2.1 Child Exploitation (استغلال الأطفال)

**Definition:** Using children as primary content subjects for views, engagement, or profit.

**PROHIBITED Indicators:**
- Child occupies >40% of frame consistently
- Child performing for camera (challenges, reactions)
- "Day in life of my child" format
- Gaming videos featuring child prominently
- Extended screen time (>30 seconds continuously)
- Multiple children in content farm setup
- Child looking directly at camera (performing)
- Close-up face framing (thumbnail bait)
- Text overlays mentioning child: "شوفوا ولدي" (watch my kid)
- Professional lighting focused on child

**ALLOWED Content:**
- Child in background (<20% frame time)
- Family birthday documentation (not for profit)
- Educational content (child learning, not performing)
- News/documentary with consent
- Child incidentally in public space

**Assessment Factors:**
- Screen time ratio: <30% OK, >50% exploitation
- Camera focus: On child vs. happens to be there
- Setting: Natural family vs. staged production
- Intent: Documentation vs. monetization

**Severity Levels:**
- High: Clear monetization, extended featuring
- Medium: Ambiguous intent, moderate screen time
- Low: Brief appearance with unclear purpose

#### 3.2.2 Worker Exploitation (استغلال العاملين)

**Definition:** Filming domestic workers as content subjects without consent.

**PROHIBITED:**
- Worker facing camera (not natural work position)
- Worker performing for content
- "Day with my helper" format
- Workers in jokes or pranks
- Showcasing living conditions for views

**ALLOWED:**
- Worker briefly in background doing job
- Appreciation posts with consent indicators

---

### 3.3 Violation Category 3: Hate Speech (مكافحة العنصرية)

#### 3.3.1 Vulgar Language (الألفاظ المبتذلة)

**Definition:** Profanity, obscene language, sexual references.

**Detection - Visual:**
- Profanity in text overlays
- Censored text (***) indicating hidden words
- Obscene symbols

**Detection - Text/Audio:**
- Animal insults: كلب، حمار، خنزير
- Sexual terms: زنا، عاهرة، قحبة
- Curses: يلعن أبوك، تف عليك

**Severity:**
- High: Sexual profanity, severe curses
- Medium: Common swear words
- Low: Mild crude language

#### 3.3.2 Wealth Bragging (التباهي بالأموال)

**Definition:** Ostentatious display of money/possessions for showing off.

**Detection - Visual:**
- Cash stacks prominently displayed
- Saudi Riyal notes spread out
- Luxury watches showcased (Rolex, AP)
- Multiple expensive cars in frame
- Designer tags visible
- Jewelry display
- High-end property tours

**Detection - Text:**
- "مجرد مصروف جيب" (just pocket money) with cash
- "السيارة الخامسة" (my fifth car)
- Price mentions: "ساعتي ب ٥٠ ألف" (my watch 50k)
- Brand dropping: Gucci, Ferrari

**Context Differentiators:**
- Educational finance → ALLOWED
- Product reviews with disclosure → ALLOWED
- Bragging for engagement → VIOLATION

**Severity:**
- High: Excessive + bragging caption
- Medium: Display without context
- Low: Subtle luxury visibility

#### 3.3.3 Tribal Incitement (إثارة القبلية)

**Definition:** Content promoting tribal superiority or division.

**Detection - Visual:**
- Tribal flags prominently displayed
- Tribal symbols/insignia
- Maps showing tribal territories
- Historical conflict imagery

**Detection - Text:**
- Superiority claims: "قبيلتنا أشرف" (our tribe nobler)
- Derogatory terms: عبيد، خضيري
- Calls for tribal unity against others

**Detection - Audio:**
- Tribal chants
- Divisive poetry
- Stories glorifying conflicts

**Context:**
- Historical/educational → ALLOWED
- Cultural heritage → ALLOWED
- Division incitement → VIOLATION

#### 3.3.4 Sectarian Content (إثارة الطائفية)

**Definition:** Content promoting sectarian division.

**Detection - Visual:**
- Sectarian symbols
- Divisive religious flags
- Conflict imagery

**Detection - Text:**
- Labels: رافضي، ناصبي، وهابي
- Takfir (declaring others non-Muslim)
- Mocking other sects' practices

**Severity:**
- High: Violence calls
- Medium: Mocking practices
- Low: Subtle references

#### 3.3.5 Racism (العنصرية)

**Definition:** Discrimination based on race, ethnicity, nationality.

**Detection - Visual:**
- Racist symbols (swastikas)
- Mocking ethnic imagery
- Blackface, ethnic mockery

**Detection - Text:**
- Slurs: عبد، زنجي (anti-Black terms)
- Nationality insults: يمني، مصري used negatively
- Stereotyping: "كل [nationality] هم..."

**Detection - Audio:**
- Racist jokes
- Malicious accent mocking
- Verbal slurs

---

## 4. SYSTEM ARCHITECTURE

### 4.1 High-Level Flow

```
Content Upload → Preprocessor → Vision Analysis → Decision Engine → Action
                           ↓            ↓
                     Audio Extract → Text Analysis ↗
```

### 4.2 Components

**Component 1: Content Preprocessor**
- Accept uploads (video/image)
- Extract frames (1 fps for videos)
- Extract audio track
- Store in S3
- Generate metadata

**Component 2: Vision Analyzer**
- Use GPT-4o API
- Analyze frames for all visual violations
- Return violation score (0-1)
- Store results in database

**Component 3: Text Analyzer**
- Transcribe audio (Whisper API)
- Analyze text (GPT-4 API)
- Check captions/comments
- Detect text violations
- Return violation score (0-1)

**Component 4: Decision Engine**
- Combine vision + text scores
- Apply hard rules
- Route to action:
  - Auto-remove (score ≥0.85)
  - Human review (0.60-0.85)
  - Warning (0.40-0.60)
  - Allow (<0.40)
- Store decision with evidence

### 4.3 Technology Stack

**AI Models:**
- GPT-4o (vision analysis)
- GPT-4 (text analysis)
- Whisper (speech-to-text)

**Infrastructure:**
- Backend: FastAPI (Python 3.11+)
- Data Storage: JSON files (local filesystem)
- File Storage: Local directories
- Deployment: Docker containers (optional for MVP)

**No Cloud Services for MVP:** Using local storage and JSON files to simplify setup and reduce costs during development.

**Migration Path:** Once MVP validated, can migrate to:
- PostgreSQL for relational data
- AWS S3 for media storage
- Redis for caching

---

## 5. FUNCTIONAL REQUIREMENTS

### 5.1 Content Upload
- Accept video files: MP4, MOV, AVI (max 500MB)
- Accept image files: JPG, PNG, WEBP (max 10MB)
- Accept metadata: user_id, caption (optional)
- Return content_id immediately
- Process asynchronously

### 5.2 Frame Extraction (Videos Only)
- Extract 15 frames per second (minimum for proper analysis)
- Save as JPG files
- Maintain original resolution (or 1920x1080 max)
- Extract audio track as WAV

### 5.3 Storage
- Store all files locally in organized directory structure
- Structure: `data/{user_id}/{content_id}/original.mp4`
- Structure: `data/{user_id}/{content_id}/frames/frame_001.jpg`
- Structure: `data/{user_id}/{content_id}/audio.wav`
- Generate metadata.json locally
- Use JSON files for data persistence (no database for MVP)

### 5.4 Vision Analysis
- Analyze each frame with GPT-4o
- Single prompt detects all visual violations
- Return violations array with confidence scores
- Return overall violation_score (0-1)
- Store results in database

### 5.5 Audio Transcription
- Use Whisper API for Arabic audio
- Return transcript text
- Return language detection
- Store transcript

### 5.6 Text Analysis
- Analyze transcript + caption with GPT-4
- Single prompt detects all text violations
- Return violations array
- Return violation_score (0-1)
- Store results

### 5.7 Decision Making
- Combine vision_score and text_score
- Formula: (vision × 0.6) + (text × 0.4) for video
- Formula: (vision × 0.7) + (text × 0.3) for image
- Apply hard rules (override scoring)
- Route to action based on thresholds
- Store decision with reasoning

### 5.8 Hard Rules (Auto-Escalate)
- Child exploitation + confidence >0.80 → Force human review
- Hate symbols + confidence >0.90 → Auto-remove
- Multiple violations (2+) with confidence >0.85 → Force review

### 5.9 Action Routing
- Score ≥0.85 → Auto-remove
- Score 0.60-0.85 → Human review
- Score 0.40-0.60 → Warning
- Score <0.40 → Allow

---

## 6. NON-FUNCTIONAL REQUIREMENTS

### 6.1 Performance
- Frame extraction: <10 seconds per video (15 fps extraction)
- Vision analysis: <3 seconds per frame (95th percentile)
- Text analysis: <2 seconds per transcript
- Decision engine: <100ms
- Total pipeline: <60 seconds for 30-second video (due to 15 fps = 450 frames to analyze)

### 6.2 Scalability
- Support 10 concurrent uploads
- Process 100 items per hour minimum
- Database handles 10,000+ records

### 6.3 Reliability
- 99% uptime
- Retry failed API calls (3 attempts, exponential backoff)
- Graceful degradation (if vision fails, use text only)

### 6.4 Cost
- Target: <$0.02 per content item
- GPT-4o: ~$0.01 per image
- GPT-4 text: ~$0.002 per analysis
- Whisper: ~$0.006 per minute

### 6.5 Security
- Store API keys in environment variables
- Validate all inputs
- Sanitize user data
- Use parameterized SQL queries
- S3 buckets private (no public access)

### 6.6 Compliance
- Store all decisions for audit (90 days minimum)
- Log all API calls
- Preserve evidence bundles
- GDPR-compliant data handling

---

## 7. API SPECIFICATIONS

### 7.1 Endpoints

**POST /api/v1/content/upload**
- Purpose: Upload content for analysis
- Input: file, user_id, caption (optional)
- Output: content_id, status
- Status codes: 200 (success), 400 (invalid), 413 (too large), 500 (error)

**GET /api/v1/content/{content_id}/status**
- Purpose: Check processing status
- Output: status (processing/completed/failed), decision

**GET /api/v1/content/{content_id}/details**
- Purpose: Get full analysis results
- Output: vision_analysis, text_analysis, decision, evidence

### 7.2 Response Formats

**Upload Response:**
```json
{
  "content_id": "uuid",
  "status": "processing"
}
```

**Status Response:**
```json
{
  "content_id": "uuid",
  "status": "completed",
  "decision": {
    "action": "human_review",
    "score": 0.72,
    "reason": "Medium violation score detected"
  },
  "processed_at": "2025-10-04T10:30:00Z"
}
```

**Details Response:**
```json
{
  "content_id": "uuid",
  "vision_analysis": {
    "frames_analyzed": 30,
    "avg_violation_score": 0.75,
    "violations": [
      {
        "frame_number": 15,
        "category": "child_exploitation",
        "confidence": 0.85,
        "description": "Child is main subject performing for camera"
      }
    ]
  },
  "text_analysis": {
    "transcript": "...",
    "violations": [
      {
        "category": "bullying",
        "confidence": 0.70,
        "matched_keywords": ["فاشل"]
      }
    ]
  },
  "decision": {
    "action": "human_review",
    "combined_score": 0.72,
    "reasoning": "Child exploitation indicators detected"
  },
  "evidence": {
    "frame_urls": ["s3://..."],
    "audio_url": "s3://...",
    "metadata_url": "s3://..."
  }
}
```

---

## 8. DATA STORAGE STRUCTURE

### 8.1 File System Organization

**Directory Structure:**
```
manarah-backend/
├── data/
│   ├── content/
│   │   └── {user_id}/
│   │       └── {content_id}/
│   │           ├── original.{mp4|jpg|png}
│   │           ├── frames/
│   │           │   ├── frame_0001.jpg
│   │           │   ├── frame_0002.jpg
│   │           │   └── ...
│   │           ├── audio.wav
│   │           └── metadata.json
│   ├── analysis/
│   │   └── {content_id}.json
│   ├── decisions/
│   │   └── {content_id}.json
│   └── audit/
│       └── {date}/
│           └── events.jsonl
```

### 8.2 JSON Data Schemas

**File: data/content/{user_id}/{content_id}/metadata.json**
```json
{
  "content_id": "uuid",
  "user_id": "string",
  "upload_timestamp": "2025-10-04T10:30:00Z",
  "content_type": "video|image",
  "duration_seconds": 30.5,
  "frame_count": 450,
  "fps": 15,
  "post_caption": "optional text",
  "status": "processing|completed|failed",
  "file_paths": {
    "original": "data/content/user123/uuid/original.mp4",
    "frames": ["data/content/user123/uuid/frames/frame_0001.jpg", "..."],
    "audio": "data/content/user123/uuid/audio.wav"
  }
}
```

**File: data/analysis/{content_id}.json**
```json
{
  "content_id": "uuid",
  "analysis_timestamp": "2025-10-04T10:35:00Z",
  "vision_analysis": {
    "frames_analyzed": 450,
    "avg_violation_score": 0.65,
    "violations": [
      {
        "frame_number": 150,
        "category": "child_exploitation",
        "confidence": 0.85,
        "description": "...",
        "evidence": "...",
        "severity": "high"
      }
    ]
  },
  "text_analysis": {
    "transcript": "full transcribed text",
    "language": "ar",
    "dialect": "gulf",
    "violations": [
      {
        "category": "bullying",
        "confidence": 0.70,
        "matched_keywords": ["فاشل"],
        "context": "...",
        "severity": "medium"
      }
    ],
    "violation_score": 0.70
  }
}
```

**File: data/decisions/{content_id}.json**
```json
{
  "content_id": "uuid",
  "decision_timestamp": "2025-10-04T10:35:30Z",
  "vision_score": 0.65,
  "text_score": 0.70,
  "combined_score": 0.67,
  "action": "human_review",
  "hard_rule_triggered": null,
  "reasoning": "Medium violation score - requires review",
  "priority": "medium",
  "evidence_summary": {
    "total_violations": 2,
    "categories": ["child_exploitation", "bullying"],
    "highest_confidence": 0.85
  }
}
```

**File: data/audit/{date}/events.jsonl** (JSON Lines format)
```jsonl
{"timestamp": "2025-10-04T10:30:00Z", "event": "upload", "content_id": "uuid", "user_id": "user123"}
{"timestamp": "2025-10-04T10:35:00Z", "event": "analysis_complete", "content_id": "uuid", "score": 0.67}
{"timestamp": "2025-10-04T10:35:30Z", "event": "decision_made", "content_id": "uuid", "action": "human_review"}
```

### 8.3 Data Access Functions

All components must use these standard functions:
- `save_metadata(content_id, data)` → Save to metadata.json
- `load_metadata(content_id)` → Load from metadata.json
- `save_analysis(content_id, analysis)` → Save to analysis JSON
- `load_analysis(content_id)` → Load analysis JSON
- `save_decision(content_id, decision)` → Save to decision JSON
- `append_audit_log(event)` → Append to audit JSONL

---

## 9. ERROR HANDLING

### 9.1 Error Response Format
All errors return structured JSON:
```json
{
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "Supported formats: MP4, MOV, JPG, PNG",
    "timestamp": "2025-10-04T10:30:00Z",
    "content_id": "uuid (if applicable)"
  }
}
```

### 9.2 Error Codes
- **400** - INVALID_FILE_FORMAT: Unsupported file type
- **400** - INVALID_INPUT: Missing required fields
- **413** - FILE_TOO_LARGE: Exceeds size limits
- **429** - RATE_LIMIT_EXCEEDED: Too many requests
- **500** - PROCESSING_FAILED: Internal error during processing
- **500** - STORAGE_ERROR: S3 upload/download failed
- **500** - API_ERROR: OpenAI API error
- **504** - ANALYSIS_TIMEOUT: Processing took too long

### 9.3 Retry Strategy
- **OpenAI API calls:** 3 retries, exponential backoff (1s, 2s, 4s)
- **S3 operations:** 3 retries, linear backoff (1s each)
- **Database operations:** 2 retries, immediate

### 9.4 Fallback Behavior
- If vision analysis fails → Use text analysis only, log warning
- If text analysis fails → Use vision analysis only, log warning
- If both fail → Mark status as "analysis_failed", send admin alert
- If single frame fails → Continue with remaining frames
- If API timeout → Cancel request, retry with timeout extension

---

## 10. TESTING REQUIREMENTS

### 10.1 Test Scenarios (Mandatory)

**Scenario 1: Child Exploitation Detection**
- **Input:** Video (30 seconds) - child unboxing toys, looking at camera
- **Caption:** "شوفوا ولدي وهو يفتح الألعاب" (Watch my kid opening toys)
- **Expected Results:**
  - vision_score: 0.80-0.90 (child is main subject)
  - text_score: 0.55-0.65 (child-focused caption)
  - combined_score: 0.70-0.80
  - action: human_review
  - hard_rule: child_exploitation_detected

**Scenario 2: Wealth Bragging**
- **Input:** Image - cash pile (Saudi Riyals) with luxury watch visible
- **Caption:** "مجرد مصروف جيب 😎💰" (Just pocket money)
- **Expected Results:**
  - vision_score: 0.85-0.95 (prominent cash + luxury item)
  - text_score: 0.75-0.85 (bragging phrase)
  - combined_score: 0.82-0.92
  - action: auto_remove (score >0.85)
  - priority: high

**Scenario 3: Bullying Content**
- **Input:** Image - screenshot with insulting text overlay
- **Caption:** "رد على الفاشل هذا" (Reply to this loser)
- **Expected Results:**
  - vision_score: 0.65-0.75 (insult visible in image)
  - text_score: 0.70-0.80 (insulting caption)
  - combined_score: 0.68-0.77
  - action: human_review
  - category: bullying

**Scenario 4: Safe Family Content**
- **Input:** Image - family birthday party, child in background (<20% frame)
- **Caption:** "عيد ميلاد سعيد لأمي" (Happy birthday mom)
- **Expected Results:**
  - vision_score: 0.10-0.20 (child incidental)
  - text_score: 0.00-0.10 (benign caption)
  - combined_score: 0.08-0.18
  - action: allow
  - priority: none

### 10.2 Test Coverage Requirements
- **Unit tests:** Each component tested individually
- **Integration tests:** Full pipeline end-to-end
- **Error handling tests:** All error paths verified
- **Performance tests:** Latency and throughput validated
- **Target:** Minimum 80% code coverage
- **Accuracy target:** >85% correct classifications on test set

### 10.3 Test Data Requirements

**Available Test Videos: 6-7 videos**
- Use your existing test videos covering different violation types
- Label each video with expected violation category
- Note expected violation score range
- Document any edge cases or ambiguous content

**Minimum Coverage:**
- At least 1 video for child exploitation detection
- At least 1 video for wealth bragging
- At least 1 video for bullying/harassment
- At least 2 videos with safe content (negative examples)
- Include at least 1 ambiguous/borderline case

**Test Video Documentation Template:**
```
Video 1: child_content_test.mp4
- Duration: 30s
- Expected category: child_exploitation
- Expected score range: 0.75-0.90
- Expected action: human_review
- Notes: Child unboxing toys, looking at camera

Video 2: safe_family.mp4
- Duration: 45s
- Expected category: none
- Expected score range: 0.0-0.20
- Expected action: allow
- Notes: Family gathering, child incidental in background
```

---

## 11. DEPLOYMENT

### 11.1 Environment Configuration

**Required Environment Variables:**
```bash
# OpenAI API (REQUIRED)
OPENAI_API_KEY=sk-proj-your-key-here

# Application Settings
API_PORT=8000
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE_MB=500
FRAME_EXTRACTION_FPS=15

# Thresholds (tunable)
AUTO_REMOVE_THRESHOLD=0.85
REVIEW_THRESHOLD=0.60
WARNING_THRESHOLD=0.40

# Data Paths (local storage)
DATA_DIR=./data
CONTENT_DIR=./data/content
ANALYSIS_DIR=./data/analysis
DECISIONS_DIR=./data/decisions
AUDIT_DIR=./data/audit
```

**Optional (for future migration to cloud):**
```bash
# AWS S3 (Placeholder - not used in MVP)
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_REGION=
# S3_BUCKET_NAME=

# Database (Placeholder - not used in MVP)  
# DATABASE_URL=
```

### 11.2 Infrastructure Requirements

**Compute:**
- Minimum: 2 vCPU, 4GB RAM
- Recommended: 4 vCPU, 8GB RAM (for concurrent processing)
- Python 3.11 or higher

**Storage:**
- Local disk: Minimum 50GB free space
- No database required for MVP (using JSON files)
- No S3 required for MVP (using local filesystem)

**Network:**
- Outbound HTTPS (443) for OpenAI API
- Inbound HTTP/HTTPS for API endpoints

**Cost Savings:**
- No AWS charges during development
- No database hosting costs
- Only OpenAI API costs (~$10-20 for MVP testing)

### 11.3 Docker Deployment

**Dockerfile structure:**
```
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["uvicorn", "src.api.routes:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose (optional):**
- API service container
- PostgreSQL container
- Nginx reverse proxy (optional)

### 11.4 Monitoring & Logging

**Metrics to Track:**
- API request count
- Processing success/failure rate
- Average processing time per content type
- API call counts (GPT-4o, GPT-4, Whisper)
- Cost per content item
- Database query performance
- S3 storage usage

**Logging Requirements:**
- Log all API requests (INFO level)
- Log all violations detected (WARNING level)
- Log all errors (ERROR level)
- Log all decisions (INFO level)
- Rotate logs daily
- Retain logs for 30 days minimum

**Log Format:**
```
2025-10-04 10:30:00 [INFO] content_id=abc-123 event=upload_complete user_id=user_456
2025-10-04 10:30:15 [WARNING] content_id=abc-123 event=violation_detected category=child_exploitation score=0.85
2025-10-04 10:30:16 [ERROR] content_id=abc-123 event=api_error service=openai error=rate_limit
```

---

## 12. ACCEPTANCE CRITERIA

### 12.1 Must Have (MVP Requirements)

**Functional - Core Pipeline:**
- [ ] Upload API accepts videos (MP4) and images (JPG, PNG)
- [ ] Frame extraction works for videos (15 fps minimum)
- [ ] Audio extraction functional
- [ ] Vision analysis calls GPT-4o successfully
- [ ] Text analysis calls GPT-4 successfully  
- [ ] Audio transcription calls Whisper successfully
- [ ] Decision engine produces action (remove/review/warn/allow)
- [ ] Results stored in JSON files
- [ ] Status API returns processing state

**Performance - Baseline:**
- [ ] Processing completes for 30s video (expected: ~60-90 seconds due to 450 frames)
- [ ] System handles 1 upload at a time without crashing
- [ ] Vision API calls complete successfully (with retries)
- [ ] Text API calls complete successfully (with retries)

**Quality - Minimum Viable:**
- [ ] Detects obvious violations in at least 4 of 6-7 test videos
- [ ] No crashes during normal operation
- [ ] JSON files store results without data loss
- [ ] Local file storage works reliably

**Cost - Tracking:**
- [ ] Cost per item is logged and measured
- [ ] Total costs tracked (expected: ~$0.15-0.30 per 30s video due to 450 frames)

**Documentation - Basic:**
- [ ] README with setup steps
- [ ] Environment variables documented
- [ ] Basic API usage examples
- [ ] Test video labels documented

**Security - Essential:**
- [ ] API keys not hardcoded
- [ ] File paths validated (prevent directory traversal)
- [ ] Basic input validation (file type, size)

### 12.2 Should Have (Post-MVP Improvements)

**Performance - Target Goals:**
- [ ] 95th percentile latency <45 seconds for 30s video (relaxed from 30s)
- [ ] Vision analysis <5 seconds per frame (relaxed from 3s)
- [ ] Supports 3-5 concurrent uploads
- [ ] Processes 50+ items per hour

**Quality - Improved Accuracy:**
- [ ] Detection accuracy >70% on test set (realistic starting point)
- [ ] All 4 test scenarios pass with reasonable scores
- [ ] False positive rate <25% (will improve with tuning)
- [ ] False negative rate <20% (will improve with tuning)

**Cost - Optimization:**
- [ ] Average cost <$0.03 per item (relaxed from $0.02)
- [ ] Cost reduction strategies identified

**Documentation - Complete:**
- [ ] API documentation with all endpoints
- [ ] Database schema with relationships explained
- [ ] Troubleshooting guide
- [ ] Deployment checklist

**Testing - Expanded:**
- [ ] Unit tests for critical functions
- [ ] Code coverage >60% (relaxed from 80%)

### 12.3 Nice to Have (Future Enhancements)

**Performance - Optimal:**
- [ ] <30 seconds for 30s video (original target)
- [ ] 10+ concurrent uploads
- [ ] 100+ items per hour

**Quality - High Accuracy:**
- [ ] >85% detection accuracy (original target)
- [ ] False positives <15%
- [ ] False negatives <10%
- [ ] Code coverage >80%

**Features - Advanced:**
- [ ] Automatic prompt optimization
- [ ] Confidence calibration
- [ ] Performance monitoring dashboard
- [ ] Automated testing suite

### 12.4 Project Completion Definition

**The MVP is considered COMPLETE when:**

1. **Core functionality works**: Can upload content, process it, and return a decision
2. **APIs are functional**: All 3 endpoints work (upload, status, details)
3. **Basic accuracy achieved**: Correctly identifies obvious violations in test cases
4. **System is stable**: Runs without crashes for 1 hour continuous operation
5. **Costs are tracked**: Know how much each analysis costs
6. **Documentation exists**: Someone else can set up and run the system
7. **Security basics**: No obvious security vulnerabilities

**Notes on Realistic Expectations:**
- First version will not be perfect - that's expected
- Accuracy will improve with prompt tuning and iteration
- Performance will improve with optimization
- Some false positives/negatives are acceptable in MVP
- Focus is on proving the approach works, not perfection
- Thresholds can be adjusted based on real-world testing

**Iteration Plan:**
- **Version 1.0 (MVP)**: Meet "Must Have" criteria - proves concept works
- **Version 1.1**: Achieve "Should Have" - production-ready
- **Version 2.0**: Implement "Nice to Have" - optimized system

---

## 13. CONSTRAINTS & LIMITATIONS

### 13.1 Technical Constraints
- **Must use:** GPT-4o for vision, GPT-4 for text, Whisper for audio
- **Cannot use:** Custom ML models, AWS Rekognition, YOLO, TensorFlow
- **Language support:** Arabic and English only
- **Video length:** Maximum 5 minutes (practical limit)
- **File size:** 500MB video, 10MB image

### 13.2 Rate Limits
- OpenAI GPT-4o: ~500 requests per minute
- OpenAI GPT-4: ~10,000 requests per minute
- OpenAI Whisper: ~50 requests per minute
- Implementation must respect these limits

### 13.3 Out of Scope
- Frontend UI (already built)
- User authentication system
- User management
- Payment/billing system
- Content recommendation engine
- Analytics dashboard
- Mobile applications
- Real-time live stream analysis
- Content appeals workflow
- Multi-language support beyond Arabic/English
- Custom ML model training
- Video editing capabilities
- Content distribution/CDN

---

## 14. GLOSSARY

**Terms:**
- **VLM:** Vision-Language Model (GPT-4o)
- **LLM:** Large Language Model (GPT-4)
- **STT:** Speech-to-Text (Whisper)
- **Violation Score:** Numeric score 0-1 indicating violation severity
- **Hard Rule:** Override logic that ignores scoring thresholds
- **Evidence Bundle:** Complete set of analysis results and artifacts
- **Content Item:** Single video or image uploaded for analysis
- **Frame:** Single image extracted from video
- **FPS:** Frames Per Second (extraction rate = 15 fps)

**Actions:**
- **Auto-remove:** Immediately flag content for removal (score ≥0.85)
- **Human review:** Send to moderator queue for manual decision (score 0.60-0.85)
- **Warning:** Flag user but allow content (score 0.40-0.60)
- **Allow:** No action needed (score <0.40)

**Violation Categories:**
- **Bullying:** Harassment, mockery, insults
- **Child exploitation:** Using children as content for profit
- **Worker exploitation:** Filming domestic workers inappropriately
- **Vulgar language:** Profanity, obscenity
- **Wealth bragging:** Ostentatious money/luxury display
- **Tribal:** Tribal superiority or division content
- **Sectarian:** Religious sect-based hatred
- **Racism:** Race/ethnicity-based discrimination

---

## 15. APPENDIX

### 15.1 Example Violation Detections

**Example 1: Child Exploitation**
```
Input: 30-second video, 450 frames analyzed
Frame 150 detection:
- Category: child_exploitation
- Confidence: 0.87
- Description: "Child occupies 65% of frame, looking directly at camera, performing unboxing activity"
- Evidence: "Professional lighting setup, thumbnail-style framing, child as main subject"
- Severity: high

Decision: Human review (hard rule triggered)
```

**Example 2: Wealth Bragging**
```
Input: Single image
Vision detection:
- Category: wealth_bragging
- Confidence: 0.92
- Description: "Large stack of Saudi Riyal notes prominently displayed with luxury watch"
- Severity: high

Text analysis (caption: "مجرد مصروف جيب"):
- Matched keywords: ["مصروف جيب" (pocket money)]
- Confidence: 0.85

Combined score: 0.90
Decision: Auto-remove
```

### 15.2 Cost Calculation Example

**30-second video processing:**
- Frames extracted: 30s × 15 fps = 450 frames
- Vision analysis: 450 × $0.01 = $4.50
- Audio transcription: 30s = $0.003
- Text analysis: $0.002
- **Total: ~$4.51 per video**

**Optimization strategies:**
- Sample every 3rd frame (5 fps): $1.50 per video
- Process only 10-second clips initially: $1.50 per video
- Batch process overnight: Same cost, better throughput

### 15.3 Migration Path

**Current (MVP): Local + JSON**
- Storage: Local filesystem
- Data: JSON files
- Cost: OpenAI API only (~$4.50/video)
- Setup: Simple (1 API key)

**Future (Production): Cloud + Database**
- Storage: AWS S3
- Data: PostgreSQL
- Cost: $4.50/video + $0.05 infrastructure
- Setup: Complex (AWS account, database)
- Benefits: Scalability, durability, backup

**Migration steps when ready:**
1. Set up AWS S3 bucket
2. Set up PostgreSQL database
3. Migrate existing JSON data to database
4. Update storage module to use S3
5. Update data module to use PostgreSQL
6. Keep JSON as backup for 30 days
7. Deprecate JSON storage

---

## 16. REFERENCES

**Related Standards:**
- MPAA Content Rating System (for severity guidelines)
- Saudi Media Content Regulations
- OpenAI Usage Policies
- GDPR/Data Protection Guidelines

**Technical Documentation:**
- OpenAI API Documentation: https://platform.openai.com/docs
- FastAPI Documentation: https://fastapi.tiangolo.com
- FFmpeg Documentation: https://ffmpeg.org/documentation.html

**Project Documents:**
- Manarah TaskMaster: Sequential implementation tasks
- Test Video Documentation: Labels for 6-7 test videos
- Environment Setup Guide: Pre-implementation checklist

---

## DOCUMENT END

**Document Version:** 1.0  
**Last Updated:** October 4, 2025  
**Status:** Complete and Ready for Implementation  
**Next Step:** Provide to AI coding agent with TaskMaster document