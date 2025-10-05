# 🕌 Manarah — Saudi Content Violation Detection Platform (منارة)

## 📖 Overview
**Manarah (منارة)** is an AI-powered monitoring system that detects **content violations in real-time** from social media and uploaded videos.  
It focuses on protecting Saudi digital platforms by analyzing **visual and audio content** for signs of:
- **Child exploitation**
- **Bullying or verbal abuse**
- **Display of wealth or indecent exposure**
- **Tribal, racist, or sectarian promotion**

Built with a **React + Vite frontend** and an **AI model backend** (integrated via REST API / SSE).

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| Frontend | React (Vite) + JSX + Tailwind / custom CSS |
| Backend | Node.js mock server (SSE) or real Python FastAPI (AI model) |
| AI Model | Computer Vision + Speech Analysis (deployed separately) |
| Communication | SSE (Server-Sent Events) for live notifications |
| Design | Saudi color palette (Vision 2030 theme), Najdi Sadu style |
| Deployment | Docker-ready (or Node + npm start) |

---

## 🧩 System Architecture

```
                    ┌────────────────────────────┐
                    │   AI Model Server (Python) │
                    │  • /api/analyze endpoint   │
                    │  • Image & Audio Detection │
                    └─────────────┬──────────────┘
                                  │  (JSON result)
                                  ▼
     ┌────────────────────────────────────────────────────┐
     │  Frontend (Vite + React)                           │
     │  • /autoscan → Manual video upload & AI results     │
     │  • /realtime → Live feed via SSE                   │
     │  • /dashboard → Charts & metrics                   │
     │  • /team → About developers                        │
     └─────────────┬──────────────────────────────────────┘
                   │  (SSE)
                   ▼
           ┌──────────────────────────────┐
           │ mock-server.js (Dev mode)    │
           │  • Generates random alerts    │
           │  • Sends events to /api/events│
           └──────────────────────────────┘
```

---

## 🧠 Features

### 1. **Real-Time Violation Detection (الكشف اللحظي)**
- Displays live notifications as soon as the AI flags content.
- Supports both **audio** and **image** violations.
- Auto refreshes every few seconds via **SSE** (`/api/events`).

### 2. **Auto-Scan Page (فحص تلقائي)**
- Users upload a video manually.
- The system analyzes both **visual and verbal** content.
- Returns final decision:  
  **Violation Type | Confidence | Reason**  
  in a clean card format.

### 3. **Dashboard (لوحة التحكم)**
- Summarizes total detections, categories, and percentages.
- Displays **Pie & Bar charts** for admin overview.

### 4. **Team Page (أعضاء الفريق)**
- Lists developers with name, position, and LinkedIn links.

---

## 📁 Project Structure

```
manarah/
├── public/
│   ├── assets/
│   │   ├── sadu1.jpg
│   │   ├── wrong.jpg
│   │   └── sample-voice.mp3
│   └── index.html
│
├── src/
│   ├── components/
│   │   ├── NotificationCard.jsx
│   │   └── HeaderNav.jsx
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── Realtime.jsx
│   │   ├── AutoScan.jsx
│   │   └── Team.jsx
│   ├── styles/
│   │   └── main.css
│   ├── mock-server.js
│   ├── App.jsx
│   ├── main.jsx
│   └── vite.config.js
│
├── package.json
├── Dockerfile
└── README.md
```

---

## 🔌 Setup Guide

### 1. **Install Dependencies**
```bash
npm install
```

### 2. **Run Mock AI Server**
```bash
node mock-server.js
```
> Starts a local event stream on `http://localhost:7070/api/events`

### 3. **Run Frontend**
```bash
npm run dev
```
> Open: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Integrating with Real AI Model

If the actual AI model runs on another machine:

1. Ensure the backend exposes:
   ```http
   POST /api/analyze
   ```
   Example JSON Response:
   ```json
   {
     "type_ar": "كشف الجسد من الكتفين حتى الساقين",
     "confidence": 0.92,
     "reason": "Model detected inappropriate visual exposure"
   }
   ```

2. Update `vite.config.js` proxy:
   ```js
   server: {
     proxy: {
       '/api': {
         target: 'http://<AI_MODEL_IP>:8000',
         changeOrigin: true
       }
     }
   }
   ```

3. Restart Vite (`npm run dev`) — `/autoscan` will now call the real AI model.

---

## 🧱 Docker Deployment

```bash
docker build -t manarah-dashboard .
docker run -p 5173:5173 manarah-dashboard
```

If using both frontend + AI model:
- Deploy model separately on port 8000.
- Adjust `proxy.target` in vite.config.js.

---

## 🧭 API Endpoints

| Endpoint | Method | Description |
|-----------|---------|-------------|
| `/api/events` | GET (SSE) | Stream live events |
| `/api/analyze` | POST | Analyze uploaded video |
| `/autoscan` | UI | Manual video scan |
| `/realtime` | UI | Live detections |
| `/dashboard` | UI | Admin overview |
| `/team` | UI | Developer info |

---

## 🎨 Design Guidelines
- **Colors**: Saudi Green `#006C35`, Sand `#EDE6D5`, Black `#222`
- **Fonts**: Noto Kufi Arabic, SaduNajdi
- **Theme**: Najdi Sadu & Vision 2030 branding
- **Layout**: RTL (Right-to-Left)

---

## 🧰 Developer Notes
- Modify `mock-server.js` to simulate new categories.
- SSE keeps frontend updated automatically.
- Each alert format:
  ```json
  {
    "id": 172815733,
    "type": "image",
    "kind_ar": "التباهي بالأموال",
    "status": "verified",
    "image_url": "...",
    "audio_url": "..."
  }
  ```

---

## 📜 License
© 2025 VisionGuard. All Rights Reserved.  
Developed under the **Saudi Vision 2030** initiative.
