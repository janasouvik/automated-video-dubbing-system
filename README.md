# Automated Video Dubbing System

An automated end-to-end pipeline that takes a YouTube video URL as input and generates a dubbed version in English with natural-sounding synthesized speech. 

## Overview

The system accepts a YouTube URL, processes the video through a series of AI models for transcription, translation, and text-to-speech synthesis, and then remixes the final audio back into the original video seamlessly without re-encoding the video track. The process runs locally, providing progress updates as it completes each stage.

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

## How to Run

This project consists of a backend processing pipeline and a frontend UI.

### 1. Start the Backend
The backend runs the FastAPI server and the video processing pipeline.
```bash
cd backend
pip install -r requirements.txt
make run
```
*(Ensure you have `ffmpeg` installed on your system path).*

### 2. Start the Frontend
The frontend provides the interface to input the YouTube URL and track job progress.
```bash
cd frontend
npm install
npm run dev
```

Once both servers are running, open the frontend URL in your browser, paste a YouTube link, and watch the progress in real-time as the system automatically dubs your video!
