# 🚀 Manarah Setup Guide

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] **Python 3.11+** - [Download](https://www.python.org/downloads/)
- [ ] **FFmpeg** - [Download](https://ffmpeg.org/download.html)
- [ ] **OpenAI API Key** - [Get one](https://platform.openai.com/api-keys)
- [ ] **Git** (optional) - [Download](https://git-scm.com/downloads)

## Step-by-Step Setup

### 1. Install FFmpeg

**Windows:**
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to System PATH
4. Verify: Open PowerShell and run `ffmpeg -version`

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 2. Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-...`)
5. **Save it somewhere safe** - you won't see it again!

### 3. Set Up the Project

**Clone or download the project:**
```bash
cd C:\Users\YourName\Desktop
# If using Git:
git clone <repository-url>
cd manarah3
```

**Install Python dependencies:**
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate it
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 4. Configure Environment

**Copy the template:**
```bash
cp .env.example .env
```

**Edit `.env` file:**
```bash
# Open in your favorite text editor
notepad .env
```

**Add your OpenAI API key:**
```env
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY-HERE
```

Save the file.

### 5. Test the System

**Run the test suite:**
```bash
python tests/test_system.py
```

You should see:
```
✅ All tests passed! System is ready.
```

If any tests fail:
- **Configuration**: Check your `.env` file
- **FFmpeg**: Ensure FFmpeg is in your PATH
- **OpenAI API**: Verify your API key is correct

### 6. Start the Server

**Option A: Using the quick start script (Windows)**
```powershell
.\start.ps1
```

**Option B: Manual start**
```bash
python -m uvicorn src.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 7. Verify It's Working

**Open your browser:**
- Main API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Test with curl:**
```bash
curl http://localhost:8000
```

You should get:
```json
{
  "service": "Manarah Content Moderation API",
  "status": "running",
  "version": "1.0.0"
}
```

## Quick Test Upload

### Prepare a Test File

1. Find a short video (MP4, < 30 seconds) or image (JPG/PNG)
2. Save it to your Desktop as `test.mp4` or `test.jpg`

### Upload via API Docs

1. Go to http://localhost:8000/docs
2. Click on `POST /api/v1/content/upload`
3. Click "Try it out"
4. Fill in:
   - **file**: Click "Choose File" and select your test file
   - **user_id**: `test_user`
   - **caption**: `Testing the system`
5. Click "Execute"

### Check the Results

1. Copy the `content_id` from the response
2. Go to `GET /api/v1/content/{content_id}/status`
3. Click "Try it out"
4. Paste the `content_id`
5. Enter `user_id`: `test_user`
6. Click "Execute"

Wait 60-90 seconds for video processing, then check again.

### Upload via curl (Alternative)

```bash
curl -X POST "http://localhost:8000/api/v1/content/upload" \
  -F "file=@test.mp4" \
  -F "user_id=test_user" \
  -F "caption=Testing"
```

## Common Issues & Solutions

### ❌ "ModuleNotFoundError: No module named 'ffmpeg'"

**Solution:**
```bash
pip install ffmpeg-python
```

### ❌ "FileNotFoundError: ffmpeg"

**Solution:** FFmpeg is not in your PATH. 

**Windows:**
1. Press Win + R
2. Type `sysdm.cpl` and press Enter
3. Go to "Advanced" → "Environment Variables"
4. Edit "Path" under "System variables"
5. Add FFmpeg's bin folder path
6. Restart PowerShell

### ❌ "AuthenticationError: Invalid API key"

**Solution:** 
1. Check your `.env` file
2. Ensure `OPENAI_API_KEY=sk-proj-...` has no spaces
3. Make sure you copied the complete key
4. Restart the server after changing `.env`

### ❌ "Rate limit exceeded"

**Solution:** 
- You're making too many API calls
- Wait a few minutes
- Consider upgrading your OpenAI plan

### ❌ Video processing takes too long

**Solution:**
1. Test with shorter videos first (< 10 seconds)
2. Reduce FPS in `.env`: `FRAME_EXTRACTION_FPS=10`
3. Videos process at ~2 seconds per second of video

## Docker Deployment (Optional)

If you prefer using Docker:

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Next Steps

✅ **System is running!** Now you can:

1. **Upload test content** via the API
2. **Check the `data/` folder** to see stored files
3. **Review decisions** in `data/decisions/`
4. **Adjust thresholds** in `.env` file
5. **Read the full documentation** in `README.md`
6. **Check the PRD** for detailed specifications

## Need Help?

- **Documentation**: See `README.md`
- **API Reference**: http://localhost:8000/docs
- **Full PRD**: `manarah_prd_clean.md`
- **AI Instructions**: `.github/copilot-instructions.md`

## Production Deployment

For production use:
- Use proper HTTPS/SSL
- Set up proper authentication
- Configure rate limiting
- Use cloud storage (S3) instead of local files
- Set up database (PostgreSQL) instead of JSON
- Add monitoring and alerting
- See PRD section 11 for full deployment guide

---

**Congratulations! 🎉 Your Manarah system is ready.**
