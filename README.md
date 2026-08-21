# Automated Video Dubbing System

An automated end-to-end pipeline that takes a YouTube video URL as input and generates a dubbed version in English with natural-sounding synthesized speech. 

## Overview

The system accepts a YouTube URL, processes the video through a series of AI models for transcription, translation, and text-to-speech synthesis, and then remixes the final audio back into the original video seamlessly without re-encoding the video track. The process runs locally, providing progress updates as it completes each stage.

## Repository Structure

```
.
├── backend/                # FastAPI backend & ML pipeline
│   ├── app/                # Core application (models, database, services, API)
│   ├── alembic/            # Database migration scripts
│   ├── data/               # Local data storage for jobs & temporary files
│   ├── scripts/            # Helper scripts (benchmarks, downloading models)
│   └── tests/              # Unit & API test suites
└── frontend/               # Vite + TypeScript + React frontend SPA
```

## Pipeline Steps & Tools Used

### 1. Fetch & Transcribe
The system downloads the video from the provided URL and turns its speech into text.
- **Downloading:** Uses [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) for robust and reliable video downloading from YouTube.
- **Transcription:** Uses **Whisper** (open-source by OpenAI) as a solid starting point for transcribing audio across multiple languages into text segments.

### 2. Translate
The transcribed text is translated for meaning and natural phrasing, not just a literal word-for-word conversion, so the dubbed speech sounds conversational.
- **Translation Engine:** Uses **IndicTrans2** (open-source, built specifically for translating Indian languages into English) and **NLLB** (No Language Left Behind) for carrying the meaning of the original speech into English accurately.

### 3. Synthesize
The translated English text is synthesized into natural-sounding speech.
- **Text-to-Speech:** Uses **edge-tts** to generate high-quality, natural (non-robotic) English voices. The generated audio is time-stretched to reasonably match the duration of the original speaker's segments.

### 4. Remix & Output
The new audio is swapped in, and the final video is shipped.
- **Muxing:** Uses **FFmpeg** to replace the original audio track in the video with the newly generated English dub. This is done without re-encoding the visual stream, preserving original video quality and maximizing processing speed.

---

## Stretch Goals & Future Enhancements

- **Multi-speaker Support:** Ability to tell different speakers apart and dub each in a distinct voice, optionally cloning the original speaker's own voice. 
  - **Speaker Diarization:** Integration with `pyannote.audio` to segment audio by speaker.
  - **Voice Cloning:** Utilizing free voice-cloning models like Coqui XTTS for character-accurate dubbing.

---

## Prerequisites

Before setting up the project, ensure you have the following installed on your system:
- **Python** (v3.10 or higher)
- **Node.js** (v18 or higher) & **npm**
- **FFmpeg** & **FFprobe** (must be accessible on your system path)
- **PostgreSQL** database running locally or accessible remotely

---

## How to Run & Set Up

### 1. Set Up the Backend

The backend runs the FastAPI server, interacts with PostgreSQL, and manages the video processing pipeline.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and set your `DATABASE_URL` (e.g., `postgresql+asyncpg://postgres:password@localhost:5432/video_dubbing`).

5. Run database migrations:
   ```bash
   make migrate
   ```

6. Start the development server:
   ```bash
   make dev
   ```

### 2. Set Up the Frontend

The frontend is a modern Next.js (App Router) application built with TypeScript, Tailwind CSS, NextAuth.js, Framer Motion, and next-themes.

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Next.js development server:
   ```bash
   npm run dev
   ```

Open [http://localhost:3000](http://localhost:3000) in your browser. You can explore the landing page, sign in/up, and launch live video dubbing jobs with real-time stage telemetry on the dashboard!

---

## Running with Docker

Alternatively, you can run the backend and its services using Docker:

1. Build the Docker image:
   ```bash
   make docker-build
   ```

2. Spin up the containers (database & backend):
   ```bash
   make docker-up
   ```

To stop the containers:
```bash
make docker-down
```

---

## Testing

To run the unit and API test suites, run the following in the backend directory:
```bash
make test
```

