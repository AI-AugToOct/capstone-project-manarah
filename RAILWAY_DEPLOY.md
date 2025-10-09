# 🚂 Railway Deployment Guide for Manarah

Complete guide for deploying the Manarah content moderation system to Railway.

---

## 📋 Prerequisites

1. **Railway Account:** Sign up at [railway.app](https://railway.app)
2. **Railway CLI:** `npm install -g @railway/cli`
3. **OpenAI API Key:** Get from [platform.openai.com](https://platform.openai.com/api-keys)
4. **Git Repository:** Push code to GitHub/GitLab

---

## 🏗️ Architecture Overview

**Two Services:**
- **Backend Service** (FastAPI) - Content analysis API
- **Frontend Service** (React + Vite) - Dashboard UI

Both services are containerized and deployed independently on Railway.

---

## 🚀 Deployment Methods

### Method 1: Railway Dashboard (Recommended)

#### Step 1: Create Project
1. Go to [railway.app/dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway and select your repository

#### Step 2: Deploy Backend Service

1. Railway will auto-detect the repository
2. Click **"Add Service"** → **"GitHub Repo"**
3. Configure the service:
   - **Service Name:** `manarah-backend`
   - **Root Directory:** `capstone-project-manarah-backend`
   - **Dockerfile Path:** `capstone-project-manarah-backend/Dockerfile`

4. **Add Environment Variables** (click Variables tab):
   ```
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   OPENAI_MODEL_VISION=gpt-4o
   OPENAI_MODEL_AUDIO=whisper-1
   OPENAI_MODEL_REASONER=gpt-4
   ENV=production
   LOG_LEVEL=INFO
   MAX_UPLOAD_SIZE_MB=500
   FRAME_EXTRACTION_FPS=15
   AUTO_REMOVE_THRESHOLD=0.85
   REVIEW_THRESHOLD=0.60
   WARNING_THRESHOLD=0.40
   ```

5. **Important:** Wait for backend to deploy and note the URL:
   - Example: `https://manarah-backend-production.up.railway.app`

6. **Add CORS Variable:**
   - Go back to backend Variables
   - Add: `ALLOWED_ORIGINS=https://your-frontend-url.up.railway.app`
   - (You'll get the frontend URL in the next step)

#### Step 3: Deploy Frontend Service

1. In the same project, click **"New Service"**
2. Select **"GitHub Repo"** (same repo)
3. Configure:
   - **Service Name:** `manarah-frontend`
   - **Root Directory:** `capstone-project-manarah`
   - **Dockerfile Path:** `capstone-project-manarah/Dockerfile`

4. **Add Environment Variables:**
   ```
   VITE_API_URL=https://manarah-backend-production.up.railway.app
   NODE_ENV=production
   ```
   *(Replace with your actual backend URL from Step 2)*

5. Click **"Deploy"**

#### Step 4: Update Backend CORS

1. Go back to **Backend Service** → **Variables**
2. Update `ALLOWED_ORIGINS` with the frontend URL:
   ```
   ALLOWED_ORIGINS=https://manarah-frontend-production.up.railway.app
   ```
3. Backend will auto-redeploy

#### Step 5: Generate Public Domains

1. **Backend Service:**
   - Go to Settings → Networking
   - Click **"Generate Domain"**
   - Copy the public URL

2. **Frontend Service:**
   - Go to Settings → Networking
   - Click **"Generate Domain"**
   - This is your app's public URL!

---

### Method 2: Railway CLI

```bash
# Login
railway login

# Create project
railway init

# Link to existing project (if already created)
railway link

# Deploy backend
cd capstone-project-manarah-backend
railway up --service manarah-backend

# Deploy frontend
cd ../capstone-project-manarah
railway up --service manarah-frontend
```

**Note:** You still need to set environment variables via the dashboard.

---

## ⚙️ Environment Variables Reference

### Backend Service (`manarah-backend`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | Auto | 8000 | Railway sets this automatically |
| `OPENAI_API_KEY` | ✅ Yes | - | OpenAI API key |
| `OPENAI_MODEL_VISION` | No | gpt-4o | Vision model |
| `OPENAI_MODEL_AUDIO` | No | whisper-1 | Audio transcription model |
| `OPENAI_MODEL_REASONER` | No | gpt-4 | Text analysis model |
| `ENV` | No | production | Environment name |
| `LOG_LEVEL` | No | INFO | Logging level |
| `ALLOWED_ORIGINS` | ✅ Yes | - | Frontend URL (comma-separated) |
| `MAX_UPLOAD_SIZE_MB` | No | 500 | Max file size |
| `FRAME_EXTRACTION_FPS` | No | 15 | Video frame rate |
| `AUTO_REMOVE_THRESHOLD` | No | 0.85 | Auto-remove score |
| `REVIEW_THRESHOLD` | No | 0.60 | Review score |
| `WARNING_THRESHOLD` | No | 0.40 | Warning score |

### Frontend Service (`manarah-frontend`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | Auto | 4173 | Railway sets this automatically |
| `VITE_API_URL` | ✅ Yes | - | Backend service URL |
| `NODE_ENV` | No | production | Node environment |

---

## 🧪 Post-Deployment Verification

### 1. Check Backend Health
```bash
curl https://your-backend-url.up.railway.app/healthz
```

**Expected Response:**
```json
{"status":"ok","service":"manarah-backend"}
```

### 2. Check Frontend
Open: `https://your-frontend-url.up.railway.app`

Should load the Manarah dashboard.

### 3. Test API from Frontend
1. Go to `/autoscan` page
2. Upload a test image
3. Check browser console for network requests
4. Verify requests go to your backend URL

### 4. Check CORS
Open browser DevTools → Network tab:
- Look for CORS errors (red)
- Verify `Access-Control-Allow-Origin` header in responses
- If CORS errors exist, update `ALLOWED_ORIGINS` in backend

---

## 🐛 Troubleshooting

### Problem: "502 Bad Gateway"

**Causes:**
- Service not binding to `$PORT`
- App crashed on startup
- Health check failing

**Solutions:**
1. Check Railway logs: Service → Deployments → View Logs
2. Verify Dockerfile CMD uses `${PORT}` variable
3. Check health endpoint: `/healthz`

### Problem: "CORS Error"

**Error:** `Access to fetch at 'https://backend...' from origin 'https://frontend...' has been blocked by CORS policy`

**Solution:**
1. Go to backend service Variables
2. Update `ALLOWED_ORIGINS` to include **exact** frontend URL
3. No trailing slashes: ✅ `https://app.railway.app` ❌ `https://app.railway.app/`

### Problem: Frontend shows "Network Error"

**Causes:**
- Wrong `VITE_API_URL`
- Backend not deployed

**Solutions:**
1. Check frontend Variables → `VITE_API_URL` is correct
2. Test backend health endpoint directly
3. Rebuild frontend after changing env vars

### Problem: "Out of Memory" / Crashes

**Causes:**
- Railway free tier: 512MB RAM limit
- Video processing is memory-intensive

**Solutions:**
1. Reduce `FRAME_EXTRACTION_FPS` (15 → 10)
2. Reduce `MAX_UPLOAD_SIZE_MB` (500 → 100)
3. Upgrade to Railway Pro ($5/month) for 8GB RAM

### Problem: Builds Fail

**Common Issues:**

**Backend:**
```
Error: pip install failed
```
**Solution:** Check `requirements.txt` syntax, ensure FFmpeg is in Dockerfile

**Frontend:**
```
Error: npm run build failed
```
**Solution:** Check for TypeScript errors, missing dependencies

### Problem: Slow Startup (Health Check Timeout)

**Solution:**
1. Go to Service Settings
2. Increase **Health Check Timeout** to 300 seconds
3. Railway default is 100s, but video processing init can take longer

---

## 💰 Cost Estimation

### Railway Costs (as of 2024)

**Free Tier (Hobby):**
- $5 free credits/month
- 512MB RAM per service
- Good for: Testing, low traffic

**Pro Tier ($5/month):**
- $5 credits included
- 8GB RAM per service
- Better for: Production, video processing

**Usage:**
- ~$0.000463/GB-minute
- Backend: ~$5-15/month depending on traffic
- Frontend: ~$1-5/month (mostly static)

### OpenAI Costs

**Per 30-second video:**
- Vision analysis: ~$1.50 (150 frames × $0.01)
- Audio transcription: ~$0.003
- Text analysis: ~$0.002
- **Total: ~$1.50 per video**

**Optimization:**
- Reduce FPS (15 → 10): Save ~33%
- Reduce sample rate: Save more

---

## 🔐 Security Best Practices

1. **Never commit `.env` files**
2. **Rotate API keys regularly**
3. **Use Railway's secret management** (not hardcoded)
4. **Enable Railway's built-in DDoS protection**
5. **Set up monitoring/alerts** for API key usage

---

## 📊 Monitoring

### Railway Dashboard
- **Metrics:** CPU, Memory, Network
- **Logs:** Real-time application logs
- **Deployments:** Build history and rollback

### Check Logs
```bash
railway logs --service manarah-backend
railway logs --service manarah-frontend
```

---

## 🔄 Continuous Deployment

Railway auto-deploys on git push:

1. Push to `main` branch (or configured branch)
2. Railway detects changes
3. Rebuilds affected services
4. Auto-deploys with zero downtime

**Disable Auto-Deploy:**
Go to Service Settings → Disable "Auto Deploy"

---

## 📝 Quick Reference

### Backend URLs
```
Health:  https://[backend-url]/healthz
API:     https://[backend-url]/api/v1/content/upload
Docs:    https://[backend-url]/docs
```

### Frontend URLs
```
Home:     https://[frontend-url]/
AutoScan: https://[frontend-url]/autoscan
Realtime: https://[frontend-url]/realtime
Dashboard: https://[frontend-url]/dashboard
```

### Commands
```bash
# View logs
railway logs

# Open service URL
railway open

# Environment variables
railway variables

# Restart service
railway restart

# Rollback deployment
railway rollback
```

---

## 🎯 Production Checklist

Before going live:

- [ ] Backend health check passes: `/healthz`
- [ ] Frontend loads without errors
- [ ] CORS configured correctly
- [ ] OpenAI API key valid and has credits
- [ ] Environment variables set for both services
- [ ] Custom domains configured (optional)
- [ ] Monitoring/alerts enabled
- [ ] Error logging configured
- [ ] Rate limiting implemented (optional)
- [ ] Backup strategy for data (if storing files)

---

## 📞 Support

**Railway:**
- Docs: [docs.railway.app](https://docs.railway.app)
- Discord: [discord.gg/railway](https://discord.gg/railway)

**OpenAI:**
- Docs: [platform.openai.com/docs](https://platform.openai.com/docs)
- Status: [status.openai.com](https://status.openai.com)

---

## 🚀 Next Steps

After deployment:
1. Test with real videos
2. Monitor OpenAI costs
3. Set up alerts for errors
4. Configure custom domain
5. Enable CDN for frontend (Railway provides this)
6. Set up backup jobs for analysis data

---

**Built with ❤️ for Saudi content moderation**
