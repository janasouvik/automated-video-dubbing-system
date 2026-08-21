# 🎙️ Automated Video Dubbing System

An automated end-to-end pipeline that takes a YouTube video URL as input and generates a dubbed version in English with natural-sounding synthesized speech.

## 📺 Live Demo / Preview
- **Live Demo Link:** Coming Soon (Deploying to cloud)
- **API Sandbox:** [http://localhost:8000/docs](http://localhost:8000/docs) (Interactive Swagger UI)

## 🎯 About the Project

### The Problem
When content creators publish videos in regional or foreign languages, they face a massive barrier to reaching global audiences. Traditional manual dubbing is:
- **Costly & Time-Consuming:** Hiring voice actors and audio engineers takes days and is expensive.
- **Scaling Barriers:** Dubbing a large library of videos across multiple channels is practically impossible manually.
- **Quality Loss:** Simple translations often lose conversational flow, and robotic text-to-speech results in low user retention.

### Our Solution
The Automated Video Dubbing System processes the video through an intelligent pipeline (transcription, translation, alignment, and synthesis) and remixing, running entirely locally or on a server to generate a high-quality dubbed video in seconds. It replaces the original audio track seamlessly without re-encoding the video track, preserving original video quality and maximizing processing speed.

---

## ✨ Features

### 🎙️ Stage 1 — Fetch & Transcribe
- **Robust Downloading:** Uses `yt-dlp` to download the video from a YouTube URL.
- **Audio Extraction:** Automatically extracts a 16kHz mono WAV audio file using FFmpeg.
- **Whisper Transcription:** Transcribes multi-language audio into timestamped text segments using OpenAI's Whisper model.

### 🌐 Stage 2 — Translation
- **Contextual Translation:** Uses **NLLB** (No Language Left Behind) and supports translation for meaning and conversational flow.
- **Segment Alignment:** Retains timing markers so dubbed speech aligns with the original visual timestamps.

### 🔊 Stage 3 — Speech Synthesis (TTS)
- **Natural Voices:** Integrates **edge-tts** to generate high-quality, expressive English voices.
- **Smart Time-Stretching:** Uses audio algorithms (tempo adjustments) to stretch or shrink synthesized speech segments to naturally fit within the original speaker's timing windows.

### 🎬 Stage 4 — Audio Remixing
- **FFmpeg Muxing:** Replaces the original audio track in the video with the newly generated English dub.
- **Direct Stream Copy:** Avoids re-encoding the video track to prevent quality loss and ensure fast execution.

---

## 🛠️ Tech Stack

- **Frontend:** Next.js (App Router), React 19, TypeScript, Tailwind CSS, NextAuth.js, Framer Motion, next-themes.
- **Backend:** FastAPI, SQLAlchemy 2.0 (ORM) with PostgreSQL, Alembic (Migrations), Pydantic v2 (Validation), yt-dlp, FFmpeg.
- **AI/ML Models:** OpenAI Whisper (Transcription), Meta NLLB-200 (Translation), Microsoft Edge TTS (Speech Synthesis).

---

## 📂 Project Structure

```
Automated Video Dubbing System/
├── backend/                # FastAPI Backend & ML Pipeline
│   ├── app/                # Core application (models, database, services, API)
│   ├── alembic/            # Database migration scripts & schemas
│   ├── data/               # Local data storage for jobs & temporary files
│   ├── scripts/            # Helper scripts (benchmarks, downloading models)
│   └── tests/              # Unit & API test suites
│   ├── .env.example        # Backend environment configuration template
│   ├── requirements.txt    # Backend dependency checklist
│   └── main.py             # API entrypoint
└── frontend/               # Next.js Frontend Application
    ├── src/                # React components & UI logic
    │   ├── app/            # App Router pages (Dashboard, etc.)
    │   ├── components/     # Reusable UI components (NewJobView, JobDetailView)
    │   ├── lib/            # Shared utilities and API client
    ├── .env.example        # Frontend environment configuration template
    ├── package.json        # Frontend project manifest
    └── next.config.ts      # Next.js configurations
```

---

## 🚀 Installation & Setup

### Prerequisites
Before setting up the project, make sure you have the following installed:
- **Node.js** (v18+) & **npm**
- **Python** (v3.10+) & **pip**
- **FFmpeg** & **FFprobe** (must be accessible on your system path)
- **PostgreSQL** database running locally or accessible remotely

---

### 1. 🗄️ Database Setup (PostgreSQL)
Create the application database:
```sql
CREATE DATABASE video_dubbing;
```

---

### 2. 🐍 Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment & activate it:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Setup Environment Variables:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and set your database connection, e.g.:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/video_dubbing
   FRONTEND_URL=http://localhost:3000
   ```
5. Run Database Migrations:
   ```bash
   make migrate
   ```
6. Start the API Server:
   ```bash
   make dev
   ```

---

### 3. 💻 Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Setup Environment Variables:
   ```bash
   cp .env.example .env.local
   ```
   Verify that `NEXT_PUBLIC_API_URL` points to your backend instance:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```
3. Install npm packages:
   ```bash
   npm install
   ```
4. Launch Next.js Development Server:
   ```bash
   npm run dev
   ```
   The application will run locally at [http://localhost:3000](http://localhost:3000/).

---

## 🌿 Git Workflow & Pushing Changes
Follow these steps to stage, commit, and push your changes to GitHub:

1. **Check Current Status**
   ```bash
   git status
   ```
2. **Stage Your Changes**
   ```bash
   git add .
   ```
3. **Commit Your Changes**
   ```bash
   git commit -m "feat: configure backend API endpoints and connect frontend"
   ```
4. **Pull Latest Remote Changes**
   ```bash
   git pull --rebase origin main
   ```
5. **Push to GitHub**
   ```bash
   git push origin main
   ```

---

## 📖 API Documentation
FastAPI automatically handles endpoint mapping and serves interactive Swagger documentation:
- **Swagger UI:** Visit [http://localhost:8000/docs](http://localhost:8000/docs) to test API endpoints in real-time.
- **ReDoc UI:** Alternate representation at [http://localhost:8000/redoc](http://localhost:8000/redoc).

---

## 🔮 Future Improvements
- **Multi-speaker Support:** Integrate `pyannote.audio` for speaker diarization.
- **Voice Cloning:** Enable realistic dubbing using Coqui XTTS.
- **Speech-to-Speech:** Real-time speech input translation.

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🧑💻 Authors / Contact
- **Souvik Jana** - [@janasouvik](https://github.com/janasouvik)
- **Sayan Maji** - [@Sayanmaji0506](https://github.com/Sayanmaji0506)
- **Repository Link:** [https://github.com/janasouvik/automated-video-dubbing-system](https://github.com/janasouvik/automated-video-dubbing-system)
