# 🔗 Frontend-Backend Integration Guide

## ✅ What Was Updated

### 1. **AutoScan.jsx** - Main Upload Component
- ✅ Added detailed console logging for debugging
- ✅ Updated to match backend API response structure
- ✅ Better error handling with JSON parse fallback
- ✅ Added support for new response fields:
  - `action_display` (formatted action text)
  - `totalViolations` (count of violations)
  - `violations.details` (detailed violation array)
  - `violations.source` (vision vs text)
  - `violations.severity` (critical/high/medium/low)

### 2. **vite.config.js** - Proxy Configuration
- ✅ Added proxy event logging
- ✅ Better visibility for debugging requests

---

## 📊 Backend API Structure (from main.py)

### Upload Endpoint
```
POST /api/v1/content/upload
```

**Request:**
- `file`: Video or image file (FormData)
- `user_id`: User identifier (FormData)
- `caption`: Optional caption (FormData)

**Response (202 Accepted):**
```json
{
  "content_id": "1234567890",
  "status": "processing",
  "message": "Content uploaded successfully and queued for analysis"
}
```

### Status Endpoint
```
GET /api/v1/content/{content_id}/status?user_id=react_user
```

**Response:**
```json
{
  "content_id": "1234567890",
  "status": "completed|processing|failed",
  "uploaded_at": "2025-10-07T12:34:56",
  "decision": {
    "action": "auto_remove|human_review|warning|approved",
    "action_display": "🚫 AUTO REMOVE - Content violates policies",
    "priority": "high|normal|low",
    "score": "85.5%",
    "reason": "Multiple violations detected...",
    "violations_found": 3,
    "categories": ["bullying", "child_exploitation"]
  },
  "processed_at": "2025-10-07T12:35:12"
}
```

### Details Endpoint
```
GET /api/v1/content/{content_id}/details?user_id=react_user
```

**Response:**
```json
{
  "content_id": "1234567890",
  "content_type": "video|image",
  "status": "completed",
  "uploaded_at": "2025-10-07T12:34:56",
  "processed_at": "2025-10-07T12:35:12",
  
  "decision": {
    "action": "auto_remove",
    "action_display": "🚫 AUTO REMOVE - Content violates policies",
    "priority": "high",
    "reasoning": "Multiple critical violations detected...",
    "combined_score": "85.5%",
    "vision_score": "90.0%",
    "text_score": "75.0%"
  },
  
  "violations": {
    "total_count": 3,
    "has_violations": true,
    "categories": ["bullying", "child_exploitation"],
    "severity_breakdown": {
      "critical": 2,
      "high": 1,
      "medium": 0,
      "low": 0
    },
    "details": [
      {
        "source": "vision",
        "category": "child_exploitation",
        "severity": "critical",
        "confidence": "95%",
        "description": "Children detected in inappropriate context",
        "evidence": "Multiple frames show...",
        "frame": 42
      },
      {
        "source": "text",
        "category": "bullying",
        "severity": "high",
        "confidence": "85%",
        "description": "Offensive language detected",
        "keywords": ["insult1", "insult2"]
      }
    ]
  },
  
  "analysis_summary": {
    "frames_analyzed": 150,
    "total_frames": 450,
    "transcript": "Full audio transcript...",
    "caption": "User's post caption",
    "language": "ar",
    "vision_violations": 2,
    "text_violations": 1
  }
}
```

---

## 🎨 Frontend Display Mapping

### Action Colors
```javascript
{
  "حذف تلقائي": "#dc2626" (red),
  "مراجعة بشرية": "#f59e0b" (orange),
  "تحذير": "#eab308" (yellow),
  "مسموح": "#10b981" (green)
}
```

### Severity Colors
```javascript
{
  "critical": "#dc2626" (red),
  "high": "#f59e0b" (orange),
  "medium": "#eab308" (yellow),
  "low": "#10b981" (green)
}
```

### Category Arabic Mapping
```javascript
{
  bullying: "التنمر والاستهزاء",
  child_exploitation: "استغلال الأطفال",
  worker_exploitation: "استغلال العاملين",
  vulgar_language: "الألفاظ المبتذلة",
  wealth_bragging: "التباهي بالأموال",
  tribal: "إثارة القبلية",
  sectarian: "إثارة الطائفية",
  racism: "العنصرية"
}
```

---

## 🚀 How to Run

### Terminal 1: Backend
```powershell
cd C:\Projects\work\Version_Control\capstone-project-manarah
python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Terminal 2: Frontend
```powershell
cd C:\Projects\work\capstone-project-manarah
npm run dev
```

**Expected output:**
```
VITE v5.4.0  ready in 1234 ms
➜  Local:   http://localhost:5173/
```

---

## 🧪 Testing Flow

1. **Open Browser Console** (F12)
2. **Navigate to** http://localhost:5173/autoscan
3. **Select a file** → Look for: `✅ File selected: { name, size, type }`
4. **Click Analyze** → Look for:
   ```
   📤 Uploading file: test.jpg
   📥 Upload response: 202
   ✅ Content uploaded, ID: 1234567890
   🔄 Polling attempt 1/60
   📊 Status: processing
   🔄 Polling attempt 2/60
   📊 Status: completed
   ✅ Analysis completed! Fetching details...
   📋 Analysis details: { ... }
   🔧 Formatting results: { ... }
   ✅ Formatted results: { ... }
   ```

---

## ⚠️ Common Issues

### Issue: "Failed to load resource: 400"
**Cause:** Backend rejecting upload

**Solutions:**
1. Check backend logs for exact error
2. Verify file size < 100MB (default max)
3. Verify file type is supported (.mp4, .mov, .jpg, .png)

### Issue: "Unexpected end of JSON input"
**Cause:** Backend returning non-JSON response

**Fixed:** Frontend now handles text responses gracefully

### Issue: Proxy Error
**Cause:** Backend not running or wrong port

**Solutions:**
1. Verify backend is running: `netstat -an | findstr "8000"`
2. Check backend terminal for startup messages
3. Restart both frontend and backend

---

## 📝 Console Logs Reference

| Emoji | Meaning |
|-------|---------|
| ✅ | Success |
| 📤 | Outgoing request |
| 📥 | Response received |
| 🔄 | Polling/retry |
| 📊 | Status update |
| 📋 | Data received |
| 🔧 | Processing/formatting |
| ❌ | Error |
| ⏱️ | Timeout |

---

## 🎯 What to Expect

### Happy Path
1. File selected → ✅ logged
2. Upload initiated → 📤 logged
3. Backend responds → 📥 202 logged
4. Polling starts → 🔄 logged every 2s
5. Status: processing → 📊 logged
6. Status: completed → ✅ logged
7. Fetch details → 📋 logged
8. Format results → 🔧 logged
9. Display to user → Results card shown

### Error Path
1. File selected → ✅ logged
2. Upload initiated → 📤 logged
3. Backend error → ❌ logged with details
4. Error shown to user → Red error box in UI

---

## 📚 Files Modified

1. **src/pages/AutoScan.jsx**
   - Added comprehensive logging
   - Updated response parsing for backend structure
   - Enhanced violation display with severity colors
   - Added source badges (🔍 بصري / 💬 نصي)

2. **vite.config.js**
   - Added proxy event logging

3. **INTEGRATION_GUIDE.md** (this file)
   - Complete API reference
   - Testing instructions
   - Troubleshooting guide

---

## ✨ New Features in UI

1. **Violation Count Badge** - Shows total violations detected
2. **Source Labels** - Distinguishes between vision (🔍) and text (💬) violations
3. **Severity Indicators** - Color-coded left border on violation cards
4. **Severity Badges** - Shows critical/high/medium/low
5. **Frame Numbers** - Shows which video frame had the violation
6. **Action Display** - Shows formatted action text with emoji

---

Good luck! 🚀
