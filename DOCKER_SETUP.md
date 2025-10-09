# 🐳 Docker Setup Guide for Manarah

Complete guide for running Manarah locally with Docker.

---

## 📋 Prerequisites

1. **Docker Desktop** installed ([Get Docker](https://docs.docker.com/get-docker/))
2. **Docker Compose** (included with Docker Desktop)
3. **OpenAI API Key** from [platform.openai.com](https://platform.openai.com/api-keys)
4. **Git** (to clone the repository)

### Verify Installation
```bash
docker --version          # Should show 20.x or higher
docker compose version    # Should show 2.x or higher
```

---

## 🚀 Quick Start

### 1. Clone & Setup Environment

```bash
# Navigate to project
cd /path/to/ffaaee2

# Copy environment files
cp capstone-project-manarah-backend/.env.example capstone-project-manarah-backend/.env
cp capstone-project-manarah/.env.example capstone-project-manarah/.env

# Edit backend .env and add your OpenAI API key
nano capstone-project-manarah-backend/.env
# or
code capstone-project-manarah-backend/.env
```

**Required:** Set `OPENAI_API_KEY=sk-proj-your-actual-key-here` in backend `.env`

### 2. Run Development Environment (Hot Reload)

```bash
docker compose -f docker-compose.dev.yml up --build
```

**Access:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/healthz

**Stop:** Press `Ctrl+C` or run:
```bash
docker compose -f docker-compose.dev.yml down
```

### 3. Run Production Environment (Local Test)

```bash
# Build and start
docker compose up --build

# Run in background (detached)
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

**Access:**
- Frontend: http://localhost:4173
- Backend: http://localhost:8000

---

## 🏗️ Architecture

### Services

**1. Backend (`manarah-backend`)**
- **Base Image:** Python 3.11-slim
- **Port:** 8000
- **Features:** FastAPI, FFmpeg, OpenAI, Whisper
- **Health Check:** `/healthz` endpoint
- **Volume (dev):** Hot-reload enabled for `src/` directory

**2. Frontend (`manarah-frontend`)**
- **Base Image:** Node 18-alpine
- **Port:** 5173 (dev) / 4173 (prod)
- **Features:** React, Vite, Chart.js
- **Build:** Multi-stage (deps → build → runner)
- **Volume (dev):** Hot-reload enabled for all source files

### Docker Compose Modes

| Mode | File | Purpose | Volumes | Reload |
|------|------|---------|---------|--------|
| Development | `docker-compose.dev.yml` | Active coding | ✅ Yes | ✅ Hot |
| Production | `docker-compose.yml` | Local prod test | ❌ No | ❌ No |

---

## 📝 Environment Variables

### Backend (`.env` in `capstone-project-manarah-backend/`)

```bash
# Required
OPENAI_API_KEY=sk-proj-your-key-here

# Optional (with defaults)
ENV=development
HOST=0.0.0.0
PORT=8000
OPENAI_MODEL_VISION=gpt-4o
OPENAI_MODEL_AUDIO=whisper-1
OPENAI_MODEL_REASONER=gpt-4
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE_MB=500
FRAME_EXTRACTION_FPS=15
AUTO_REMOVE_THRESHOLD=0.85
REVIEW_THRESHOLD=0.60
WARNING_THRESHOLD=0.40
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:4173
```

### Frontend (`.env` in `capstone-project-manarah/`)

```bash
# For local dev, proxy handles this automatically
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Testing the Setup

### 1. Health Checks

**Backend:**
```bash
curl http://localhost:8000/healthz
```
**Expected:**
```json
{"status":"ok","service":"manarah-backend"}
```

**Frontend:**
```bash
curl http://localhost:5173  # Dev
curl http://localhost:4173  # Prod
```
Should return HTML (200 OK)

### 2. API Documentation

Open: http://localhost:8000/docs

You should see interactive Swagger UI with all endpoints.

### 3. Upload Test

1. Open frontend: http://localhost:5173
2. Navigate to **Auto Scan** page
3. Upload a test image or video
4. Monitor backend logs:
   ```bash
   docker compose -f docker-compose.dev.yml logs -f backend-dev
   ```

---

## 🔧 Common Commands

### Build & Run

```bash
# Dev mode
docker compose -f docker-compose.dev.yml up --build

# Prod mode
docker compose up --build

# Rebuild single service
docker compose build backend
docker compose build frontend

# Run in background
docker compose up -d

# Stop all
docker compose down

# Stop and remove volumes
docker compose down -v
```

### Logs & Debugging

```bash
# View all logs
docker compose logs

# Follow logs (live)
docker compose logs -f

# Specific service
docker compose logs backend
docker compose logs frontend

# Last 100 lines
docker compose logs --tail=100
```

### Shell Access

```bash
# Backend shell
docker compose exec backend-dev bash

# Frontend shell
docker compose exec frontend-dev sh

# Run commands inside container
docker compose exec backend-dev python -m pytest
docker compose exec frontend-dev npm run build
```

### Cleanup

```bash
# Remove stopped containers
docker compose down

# Remove containers + volumes
docker compose down -v

# Remove unused images
docker image prune -a

# Nuclear option (clean everything)
docker system prune -a --volumes
```

---

## 🐛 Troubleshooting

### Problem: "Port already in use"

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process (replace PID)
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Map to different host port
```

### Problem: "Cannot connect to Docker daemon"

**Error:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Solution:**
- Start Docker Desktop
- Wait for Docker to fully initialize
- Check Docker Desktop → Settings → Resources

### Problem: Backend crashes with "OpenAI API key not found"

**Solution:**
1. Check `.env` file exists: `capstone-project-manarah-backend/.env`
2. Verify `OPENAI_API_KEY` is set (no quotes needed)
3. Restart containers: `docker compose down && docker compose up`

### Problem: Frontend shows blank page

**Causes:**
- Build failed
- API calls blocked by CORS
- Backend not running

**Solutions:**
```bash
# Check frontend logs
docker compose logs frontend

# Check backend is healthy
curl http://localhost:8000/healthz

# Verify CORS in backend logs
docker compose logs backend | grep CORS

# Rebuild frontend
docker compose build frontend
docker compose up frontend
```

### Problem: Hot reload not working in dev mode

**Solution:**
```bash
# For Mac/Linux: Enable file watching
export CHOKIDAR_USEPOLLING=true

# Already set in docker-compose.dev.yml for frontend

# For backend, ensure volume is mounted:
# volumes:
#   - ./capstone-project-manarah-backend/src:/app/src
```

### Problem: "Out of memory" / Crashes

**Solutions:**

1. **Increase Docker Memory:**
   - Docker Desktop → Settings → Resources
   - Increase Memory to 4GB+ (8GB recommended)

2. **Reduce video processing:**
   Edit backend `.env`:
   ```
   FRAME_EXTRACTION_FPS=10  # Was 15
   MAX_UPLOAD_SIZE_MB=100   # Was 500
   ```

### Problem: FFmpeg not found

**Error:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'
```

**Solution:**
FFmpeg is included in the Dockerfile. If error persists:

```bash
# Rebuild backend with no cache
docker compose build --no-cache backend
```

### Problem: Slow build times

**Solutions:**

1. **Use BuildKit:**
   ```bash
   export DOCKER_BUILDKIT=1
   docker compose build
   ```

2. **Don't rebuild unnecessarily:**
   ```bash
   # Only rebuild if Dockerfile/deps changed
   docker compose up  # No --build flag
   ```

3. **Multi-stage caching is automatic** (already optimized)

---

## 📊 Monitoring

### Resource Usage

```bash
# Real-time stats
docker stats

# Specific container
docker stats manarah-backend-1
```

### Disk Usage

```bash
# Check Docker disk usage
docker system df

# Detailed breakdown
docker system df -v
```

---

## 🔐 Security Notes

### Development
- `.env` files are excluded via `.dockerignore`
- Never commit `.env` to git
- Use `.env.example` for templates

### Production
- Runs as non-root user (`appuser` in backend, `node` in frontend)
- Minimal base images (alpine/slim)
- No dev dependencies in final image
- Health checks enabled

---

## 📈 Performance Optimization

### Image Size

```bash
# Check image sizes
docker images | grep manarah

# Expected sizes:
# Backend:  ~500-700MB (includes FFmpeg)
# Frontend: ~50-100MB (alpine-based)
```

### Build Cache

```bash
# Warm up cache (first build slow, subsequent fast)
docker compose build

# Force fresh build (if deps corrupted)
docker compose build --no-cache
```

### Network Optimization

```bash
# Docker creates internal network automatically
# Backend and frontend communicate via service names:
# - backend-dev
# - frontend-dev
```

---

## 🧰 Advanced Usage

### Custom Compose File

Create `docker-compose.override.yml` for local overrides:

```yaml
version: "3.9"

services:
  backend-dev:
    environment:
      - LOG_LEVEL=DEBUG
    ports:
      - "9000:8000"  # Use different port
```

### Multiple Environments

```bash
# Dev
docker compose -f docker-compose.dev.yml up

# Staging
docker compose -f docker-compose.staging.yml up

# Prod
docker compose -f docker-compose.yml up
```

### Persist Data Between Restarts

Data is automatically persisted in Docker volumes:

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect ffaaee2_backend-data

# Backup volume
docker run --rm -v ffaaee2_backend-data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data
```

---

## 📚 Additional Resources

### Dockerfile Locations
- Backend: `capstone-project-manarah-backend/Dockerfile`
- Frontend: `capstone-project-manarah/Dockerfile`

### Compose Files
- Dev: `docker-compose.dev.yml`
- Prod: `docker-compose.yml`

### Documentation
- Docker Docs: [docs.docker.com](https://docs.docker.com)
- Docker Compose: [docs.docker.com/compose](https://docs.docker.com/compose)
- FastAPI: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- Vite: [vitejs.dev](https://vitejs.dev)

---

## ✅ Checklist

Before starting development:

- [ ] Docker Desktop installed and running
- [ ] `.env` files created from `.env.example`
- [ ] `OPENAI_API_KEY` set in backend `.env`
- [ ] Port 8000 and 5173 available (or 4173 for prod)
- [ ] At least 4GB RAM allocated to Docker
- [ ] Internet connection (for downloading images)

---

## 🎯 Quick Reference

### Start Development
```bash
docker compose -f docker-compose.dev.yml up
```

### Start Production
```bash
docker compose up
```

### View Logs
```bash
docker compose logs -f
```

### Stop Everything
```bash
docker compose down
```

### Clean Restart
```bash
docker compose down -v
docker compose up --build
```

---

**Happy Coding! 🚀**
