# Manarah API Integration Guide

## ✅ Endpoints Ready for Production

All three API endpoints are fully implemented and tested:

### 1. **POST /api/v1/content/upload**
Upload content (video or image) for moderation analysis.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/content/upload" \
  -F "file=@video.mp4" \
  -F "user_id=user123" \
  -F "caption=Optional caption text"
```

**Response (202 Accepted):**
```json
{
  "content_id": "uuid-here",
  "status": "processing",
  "message": "Content uploaded successfully and queued for analysis"
}
```

**Validation:**
- ✅ File size limit: 500MB (configurable via `MAX_UPLOAD_SIZE_MB`)
- ✅ Allowed formats: `.mp4`, `.mov`, `.avi`, `.jpg`, `.jpeg`, `.png`, `.webp`
- ✅ Required fields: `file`, `user_id`
- ✅ Optional field: `caption`

---

### 2. **GET /api/v1/content/{content_id}/status**
Check processing status of uploaded content.

**Request:**
```bash
curl "http://localhost:8000/api/v1/content/{content_id}/status?user_id=user123"
```

**Response (200 OK):**

*While Processing:*
```json
{
  "content_id": "uuid-here",
  "status": "processing",
  "uploaded_at": "2025-10-06T10:30:00Z"
}
```

*When Completed:*
```json
{
  "content_id": "uuid-here",
  "status": "completed",
  "uploaded_at": "2025-10-06T10:30:00Z",
  "processed_at": "2025-10-06T10:31:30Z",
  "decision": {
    "action": "auto_remove",
    "score": 0.89,
    "reason": "High confidence bullying detected"
  }
}
```

*If Failed:*
```json
{
  "content_id": "uuid-here",
  "status": "failed",
  "uploaded_at": "2025-10-06T10:30:00Z",
  "error": "Error message here"
}
```

**Status Values:**
- `processing` - Analysis in progress (60-90 seconds for videos)
- `completed` - Analysis finished, decision available
- `failed` - Processing error occurred

---

### 3. **GET /api/v1/content/{content_id}/details**
Get complete analysis results and decision details.

**Request:**
```bash
curl "http://localhost:8000/api/v1/content/{content_id}/details?user_id=user123"
```

**Response (200 OK):**
```json
{
  "content_id": "uuid-here",
  "content_type": "video",
  "status": "completed",
  "uploaded_at": "2025-10-06T10:30:00Z",
  "vision_analysis": {
    "avg_violation_score": 0.75,
    "violations": [
      {
        "category": "bullying",
        "confidence": 0.82,
        "description": "Person being mocked",
        "frame_number": 45
      }
    ]
  },
  "text_analysis": {
    "violation_score": 0.65,
    "violations": [
      {
        "category": "vulgar_language",
        "confidence": 0.70,
        "context": "Profanity detected in audio"
      }
    ],
    "transcript": "Audio transcription..."
  },
  "decision": {
    "action": "auto_remove",
    "combined_score": 0.89,
    "vision_score": 0.75,
    "text_score": 0.65,
    "reasoning": "High confidence violation detected",
    "decision_timestamp": "2025-10-06T10:31:30Z"
  },
  "evidence": {
    "original_file": "data/content/user123/uuid/original.mp4",
    "frames": ["frame_0001.jpg", "frame_0002.jpg", ...],
    "audio": "data/content/user123/uuid/audio.wav",
    "metadata": "data/content/user123/uuid/metadata.json"
  }
}
```

---

## 🔧 Key Features Implemented

### ✅ CORS Configuration
CORS middleware configured to allow React frontend from:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (React default)
- `http://127.0.0.1:5173`
- `http://127.0.0.1:3000`

### ✅ Async Processing
- Upload returns immediately with 202 status
- Analysis runs in background task
- Frontend polls `/status` endpoint for updates

### ✅ Error Handling
- **404** - Content not found
- **400** - Invalid file type or missing filename
- **413** - File too large
- **500** - Internal server error

All errors return structured JSON:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "timestamp": "2025-10-06T10:30:00Z"
  }
}
```

### ✅ Input Validation
- File size validation (configurable limit)
- File type validation (whitelist approach)
- Required field validation
- Null safety checks

### ✅ Security Features
- User ID validation (prevents cross-user access)
- Temporary file cleanup after upload
- Secure file path handling

---

## 🚀 Running the Backend

### Method 1: Direct Python
```powershell
cd C:\Users\BeesT\Desktop\Tuwaiq-AI-Mod\manarah3
python -m uvicorn src.main:app --reload --port 8000
```

### Method 2: Using start.ps1
```powershell
.\start.ps1
```

### Method 3: Docker
```powershell
docker-compose up
```

---

## 🧪 Testing the Endpoints

### Quick Test
```powershell
python test_api_endpoints.py
```

This will test:
- ✅ Root health check
- ✅ CORS headers
- ✅ Error handling (404, 400)
- ✅ Image upload workflow
- ✅ Status polling
- ✅ Details retrieval

### Manual Testing with cURL

**1. Upload:**
```bash
curl -X POST "http://localhost:8000/api/v1/content/upload" \
  -F "file=@test.jpg" \
  -F "user_id=test_user" \
  -F "caption=Test caption"
```

**2. Check Status (use content_id from step 1):**
```bash
curl "http://localhost:8000/api/v1/content/{content_id}/status?user_id=test_user"
```

**3. Get Details:**
```bash
curl "http://localhost:8000/api/v1/content/{content_id}/details?user_id=test_user"
```

---

## 🌐 React Frontend Integration

### Vite Proxy Setup
Your `vite.config.js` should be configured as:
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path
      }
    }
  }
})
```

### Frontend API Calls
```javascript
// Upload content
const formData = new FormData();
formData.append('file', file);
formData.append('user_id', 'react_user');
formData.append('caption', 'User caption');

const uploadRes = await fetch('/api/v1/content/upload', {
  method: 'POST',
  body: formData
});
const { content_id } = await uploadRes.json();

// Poll for status
const checkStatus = async () => {
  const res = await fetch(
    `/api/v1/content/${content_id}/status?user_id=react_user`
  );
  const data = await res.json();
  
  if (data.status === 'completed') {
    // Get full details
    const detailsRes = await fetch(
      `/api/v1/content/${content_id}/details?user_id=react_user`
    );
    const details = await detailsRes.json();
    // Display results
  } else if (data.status === 'processing') {
    setTimeout(checkStatus, 2000); // Poll every 2 seconds
  }
};
```

---

## 📊 Processing Times

| Content Type | Processing Time | Cost (Estimate) |
|--------------|----------------|-----------------|
| Image (JPG)  | 3-5 seconds    | $0.01          |
| Video (30s)  | 60-90 seconds  | $1.50          |
| Video (60s)  | 90-120 seconds | $2.50          |

*Processing scales with video length*

---

## 🔍 Decision Actions

| Action         | Score Range | Description |
|----------------|-------------|-------------|
| `auto_remove`  | ≥0.85       | Automatic removal |
| `human_review` | 0.60-0.85   | Requires manual review |
| `warning`      | 0.40-0.60   | User warning |
| `allow`        | <0.40       | No violations |

---

## 🛠️ Configuration

Edit `.env` to customize:

```env
# API Settings
API_PORT=8000
MAX_UPLOAD_SIZE_MB=500
FRAME_EXTRACTION_FPS=15

# Thresholds (0.0 - 1.0)
AUTO_REMOVE_THRESHOLD=0.85
REVIEW_THRESHOLD=0.60
WARNING_THRESHOLD=0.40

# OpenAI API
OPENAI_API_KEY=your_key_here
```

---

## 📝 API Documentation

Interactive API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## ⚠️ Important Notes

1. **Processing is async** - Upload returns immediately, poll `/status` for results
2. **User ID required** - Used for data isolation and access control
3. **Temporary files** - Automatically cleaned up after upload
4. **Rate limiting** - OpenAI API has rate limits, consider queueing for high traffic
5. **Cost optimization** - Frames sampled every 3rd frame (5 fps effective from 15 fps)

---

## 🐛 Troubleshooting

### CORS Errors
- Ensure backend is running on port 8000
- Check Vite proxy configuration
- Verify CORS origins in `main.py`

### 404 Errors
- Confirm content_id is correct
- Ensure user_id matches upload user
- Check backend logs for details

### Timeout Issues
- Videos take 60-90+ seconds to process
- Increase polling timeout in frontend
- Check OpenAI API key and quota

### Processing Failures
- Check `data/audit/{date}/events.jsonl` for errors
- Verify FFmpeg is installed (`ffmpeg -version`)
- Check OpenAI API connectivity
- Review backend logs

---

## 📞 Support

For issues or questions:
1. Check backend logs: `logs/` directory
2. Check audit trail: `data/audit/{date}/events.jsonl`
3. Review API docs: http://localhost:8000/docs
4. Run test suite: `python test_api_endpoints.py`
