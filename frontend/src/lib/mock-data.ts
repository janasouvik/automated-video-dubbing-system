export type StageId = 'fetch' | 'transcribe' | 'translate' | 'synthesize' | 'remux';

export type StageStatus = 'pending' | 'in_progress' | 'completed' | 'failed';

export interface PipelineStageInfo {
  id: StageId;
  name: string;
  tool: string;
  description: string;
  status: StageStatus;
  progressPercent: number;
  message?: string;
  durationSec?: number;
}

export interface DubbingJob {
  id: string;
  title: string;
  youtubeUrl: string;
  targetLanguage: string;
  targetLanguageLabel: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  currentStageId: StageId;
  progressPercent: number;
  createdAt: string;
  completedAt?: string;
  stages: PipelineStageInfo[];
  videoDuration?: string;
  sourceLanguage?: string;
  downloadUrl?: string;
  error?: string;
}

export const INITIAL_STAGES: PipelineStageInfo[] = [
  {
    id: 'fetch',
    name: 'Audio Extraction',
    tool: 'yt-dlp',
    description: 'Downloading audio stream from YouTube container',
    status: 'pending',
    progressPercent: 0,
    message: 'Queued for stream extraction',
  },
  {
    id: 'transcribe',
    name: 'Speech Transcription',
    tool: 'OpenAI Whisper',
    description: 'Generating millisecond-aligned text transcript',
    status: 'pending',
    progressPercent: 0,
    message: 'Waiting for audio isolation',
  },
  {
    id: 'translate',
    name: 'Contextual Translation',
    tool: 'IndicTrans2 / NLLB',
    description: 'Translating to conversational English idioms',
    status: 'pending',
    progressPercent: 0,
    message: 'Waiting for transcription',
  },
  {
    id: 'synthesize',
    name: 'Speech Synthesis (TTS)',
    tool: 'edge-tts Neural',
    description: 'Synthesizing voiceover with duration time-stretching',
    status: 'pending',
    progressPercent: 0,
    message: 'Waiting for translation',
  },
  {
    id: 'remux',
    name: 'Lossless Remuxing',
    tool: 'FFmpeg Stream Copy',
    description: 'Muxing synthesized English audio into original video',
    status: 'pending',
    progressPercent: 0,
    message: 'Waiting for synthesized audio',
  },
];

export const MOCK_HISTORY_JOBS: DubbingJob[] = [
  {
    id: 'job-9821',
    title: 'Building Modern Web Applications with AI - Tech Talk',
    youtubeUrl: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    targetLanguage: 'en',
    targetLanguageLabel: 'English (US)',
    status: 'completed',
    currentStageId: 'remux',
    progressPercent: 100,
    createdAt: '2026-08-21T14:32:00Z',
    completedAt: '2026-08-21T14:34:12Z',
    videoDuration: '4:15',
    sourceLanguage: 'Hindi',
    downloadUrl: '#download-job-9821',
    stages: INITIAL_STAGES.map((s) => ({
      ...s,
      status: 'completed',
      progressPercent: 100,
      message: 'Completed successfully',
    })),
  },
  {
    id: 'job-9820',
    title: 'Introduction to Quantum Machine Learning Lecture 3',
    youtubeUrl: 'https://www.youtube.com/watch?v=3JZ_D3ELwOQ',
    targetLanguage: 'en',
    targetLanguageLabel: 'English (US)',
    status: 'completed',
    currentStageId: 'remux',
    progressPercent: 100,
    createdAt: '2026-08-21T11:15:00Z',
    completedAt: '2026-08-21T11:18:40Z',
    videoDuration: '8:42',
    sourceLanguage: 'Tamil',
    downloadUrl: '#download-job-9820',
    stages: INITIAL_STAGES.map((s) => ({
      ...s,
      status: 'completed',
      progressPercent: 100,
      message: 'Completed successfully',
    })),
  },
  {
    id: 'job-9818',
    title: 'Organic Farming Techniques in Semi-Arid Regions',
    youtubeUrl: 'https://www.youtube.com/watch?v=21X5lGlDOfg',
    targetLanguage: 'en',
    targetLanguageLabel: 'English (US)',
    status: 'completed',
    currentStageId: 'remux',
    progressPercent: 100,
    createdAt: '2026-08-20T19:40:00Z',
    completedAt: '2026-08-20T19:42:55Z',
    videoDuration: '6:10',
    sourceLanguage: 'Bengali',
    downloadUrl: '#download-job-9818',
    stages: INITIAL_STAGES.map((s) => ({
      ...s,
      status: 'completed',
      progressPercent: 100,
      message: 'Completed successfully',
    })),
  },
];
