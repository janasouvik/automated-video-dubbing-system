'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Video,
  Play,
  ArrowRight,
  Languages,
  Download,
  RotateCcw,
  Sparkles,
  AlertCircle,
  CheckCircle2,
  Film,
  Volume2,
  ExternalLink,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { ProgressStageTracker } from './ProgressStageTracker';
import {
  DubbingJob,
  INITIAL_STAGES,
  PipelineStageInfo,
  StageId,
} from '@/lib/mock-data';

interface NewJobViewProps {
  initialUrl?: string;
  onJobCreated?: (job: DubbingJob) => void;
}

export function NewJobView({ initialUrl = '', onJobCreated }: NewJobViewProps) {
  const [url, setUrl] = useState(initialUrl);
  const [targetLanguage, setTargetLanguage] = useState('en');
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [job, setJob] = useState<DubbingJob | null>(null);

  useEffect(() => {
    if (initialUrl && !job && !isProcessing) {
      setUrl(initialUrl);
    }
  }, [initialUrl, job, isProcessing]);

  // Stage simulation step progression
  useEffect(() => {
    if (!isProcessing || !job) return;

    const stageSequence: {
      stageId: StageId;
      durationMs: number;
      messages: string[];
    }[] = [
      {
        stageId: 'fetch',
        durationMs: 2500,
        messages: ['Connecting to yt-dlp...', 'Extracting raw audio stream...', 'Isolating visual track...'],
      },
      {
        stageId: 'transcribe',
        durationMs: 3200,
        messages: ['Loading Whisper model...', 'Detecting language...', 'Generating timestamped segments...'],
      },
      {
        stageId: 'translate',
        durationMs: 2800,
        messages: ['Running IndicTrans2 / NLLB...', 'Aligning contextual phrasing...', 'Refining sentence bounds...'],
      },
      {
        stageId: 'synthesize',
        durationMs: 3500,
        messages: ['Generating neural speech via edge-tts...', 'Applying time-stretching...', 'Balancing vocal pitch...'],
      },
      {
        stageId: 'remux',
        durationMs: 2200,
        messages: ['Executing FFmpeg stream copy...', 'Swapping audio channel in MP4...', 'Finalizing output container...'],
      },
    ];

    let currentStepIdx = 0;
    let messageIdx = 0;

    const interval = setInterval(() => {
      setJob((prevJob) => {
        if (!prevJob) return null;

        const currentConfig = stageSequence[currentStepIdx];
        if (!currentConfig) {
          // Completed all stages!
          clearInterval(interval);
          setIsProcessing(false);
          const completedJob: DubbingJob = {
            ...prevJob,
            status: 'completed',
            progressPercent: 100,
            completedAt: new Date().toISOString(),
            stages: prevJob.stages.map((s) => ({
              ...s,
              status: 'completed',
              progressPercent: 100,
              message: 'Finished successfully',
            })),
          };
          if (onJobCreated) {
            onJobCreated(completedJob);
          }
          return completedJob;
        }

        const currentStageId = currentConfig.stageId;
        const currentMsg = currentConfig.messages[messageIdx % currentConfig.messages.length];
        messageIdx++;

        // Update stages
        const updatedStages = prevJob.stages.map((s, idx) => {
          if (idx < currentStepIdx) {
            return { ...s, status: 'completed' as const, progressPercent: 100, message: 'Done' };
          }
          if (idx === currentStepIdx) {
            const stepProgress = Math.min(95, 20 + messageIdx * 25);
            return {
              ...s,
              status: 'in_progress' as const,
              progressPercent: stepProgress,
              message: currentMsg,
            };
          }
          return { ...s, status: 'pending' as const, progressPercent: 0, message: 'Queued' };
        });

        const overallPercent = Math.min(
          99,
          Math.round(((currentStepIdx + messageIdx / 4) / stageSequence.length) * 100)
        );

        return {
          ...prevJob,
          currentStageId,
          progressPercent: overallPercent,
          stages: updatedStages,
        };
      });

      if (messageIdx >= stageSequence[currentStepIdx]?.messages.length) {
        currentStepIdx++;
        messageIdx = 0;
      }
    }, 800);

    return () => clearInterval(interval);
  }, [isProcessing, job?.id, onJobCreated]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      setError('Please provide a valid YouTube URL');
      return;
    }

    if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
      setError('Please provide a valid YouTube link (e.g., https://www.youtube.com/watch?v=...)');
      return;
    }

    setError(null);
    setIsProcessing(true);

    // Extract title or mock
    const newJob: DubbingJob = {
      id: 'job-' + Math.floor(1000 + Math.random() * 9000),
      title: 'YouTube Dubbed Video — ' + (url.split('v=')[1]?.slice(0, 8) || 'Project'),
      youtubeUrl: url.trim(),
      targetLanguage,
      targetLanguageLabel: targetLanguage === 'en' ? 'English (US)' : 'Other',
      status: 'in_progress',
      currentStageId: 'fetch',
      progressPercent: 5,
      createdAt: new Date().toISOString(),
      videoDuration: '3:45',
      sourceLanguage: 'Detected Audio',
      downloadUrl: '#download-video',
      stages: INITIAL_STAGES.map((s, idx) => ({
        ...s,
        status: idx === 0 ? 'in_progress' : 'pending',
        progressPercent: idx === 0 ? 10 : 0,
        message: idx === 0 ? 'Connecting to yt-dlp extractor...' : undefined,
      })),
    };

    setJob(newJob);
  };

  const handleReset = () => {
    setJob(null);
    setIsProcessing(false);
    setUrl('');
    setError(null);
  };

  const handleDownload = () => {
    // TODO: Wire to backend /api/v1/jobs/{job.id}/download
    alert('Dubbed video download initiated! In production, this pulls the lossless remuxed MP4 from the backend.');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* View Header */}
      {!job && (
        <div className="text-center max-w-2xl mx-auto pt-6">
          <div className="w-12 h-12 rounded-2xl bg-[var(--color-accent-soft)] text-[var(--color-accent)] flex items-center justify-center mx-auto mb-4 border border-[var(--color-accent)]/20 shadow-sm">
            <Video className="w-6 h-6" />
          </div>
          <h2 className="text-2xl sm:text-3xl font-medium text-[var(--color-text)] tracking-tight">
            Start a New Dubbing Job
          </h2>
          <p className="text-sm text-[var(--color-text-muted)] mt-2 font-normal">
            Enter a YouTube link to transcribe, translate, and synthesize natural English speech with lossless video remuxing.
          </p>
        </div>
      )}

      {/* Input Form Card (shown when no job or completed) */}
      {!job && (
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 sm:p-8 shadow-sm"
        >
          <form onSubmit={handleSubmit} className="space-y-6">
            <Input
              label="YouTube Video URL"
              type="url"
              placeholder="https://www.youtube.com/watch?v=..."
              value={url}
              onChange={(e) => {
                setUrl(e.target.value);
                if (error) setError(null);
              }}
              error={error || undefined}
              leftIcon={<Video className="w-4 h-4" />}
              helperText="Supports any public or unlisted YouTube video URL"
              required
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Target Language */}
              <div className="space-y-1.5 text-left">
                <label className="block text-xs font-normal text-[var(--color-text-muted)] uppercase tracking-wide">
                  Target Language
                </label>
                <div className="relative">
                  <div className="absolute left-3.5 top-1/2 -translate-y-1/2 flex items-center pointer-events-none text-[var(--color-text-muted)]">
                    <Languages className="w-4 h-4" />
                  </div>
                  <select
                    value={targetLanguage}
                    onChange={(e) => setTargetLanguage(e.target.value)}
                    className="w-full h-11 pl-10 pr-4 text-sm rounded-lg bg-[var(--color-input-bg)] text-[var(--color-input-text)] border border-[var(--color-input-border)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent cursor-pointer"
                  >
                    <option value="en">English (US) — Natural Neural</option>
                    <option value="es" disabled>
                      Spanish (Coming Soon)
                    </option>
                    <option value="fr" disabled>
                      French (Coming Soon)
                    </option>
                    <option value="de" disabled>
                      German (Coming Soon)
                    </option>
                  </select>
                </div>
              </div>

              {/* Engine Mode */}
              <div className="space-y-1.5 text-left">
                <label className="block text-xs font-normal text-[var(--color-text-muted)] uppercase tracking-wide">
                  Remuxing Mode
                </label>
                <div className="w-full h-11 px-3.5 rounded-lg bg-[var(--color-surface-hover)] text-[var(--color-text)] border border-[var(--color-border)] flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-[var(--color-accent)]" />
                    <span>Lossless Stream Copy</span>
                  </span>
                  <span className="text-[10px] font-mono text-emerald-500 font-medium">
                    Zero Re-encode
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-2">
              <Button
                type="submit"
                size="lg"
                className="w-full"
                rightIcon={<ArrowRight className="w-4 h-4" />}
              >
                Launch Dubbing Pipeline
              </Button>
            </div>
          </form>
        </motion.div>
      )}

      {/* Live Pipeline Tracker View */}
      {job && (
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="space-y-6"
        >
          {/* Job Overview Card */}
          <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-mono text-[var(--color-accent)] bg-[var(--color-accent-soft)] px-2 py-0.5 rounded-md">
                  {job.id}
                </span>
                <span className="text-xs text-[var(--color-text-muted)]">
                  {job.targetLanguageLabel}
                </span>
              </div>
              <h3 className="text-base font-medium text-[var(--color-text)] truncate max-w-lg">
                {job.title}
              </h3>
              <a
                href={job.youtubeUrl}
                target="_blank"
                rel="noreferrer"
                className="text-xs text-[var(--color-accent)] hover:underline inline-flex items-center gap-1 mt-0.5 font-mono"
              >
                <span>{job.youtubeUrl}</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {job.status === 'completed' && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={handleReset}
                  leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
                >
                  New Dub
                </Button>
              )}
            </div>
          </div>

          {/* 5-Stage Live Tracker Component */}
          <ProgressStageTracker
            stages={job.stages}
            currentStageId={job.currentStageId}
            overallProgress={job.progressPercent}
          />

          {/* Completed State: Video Player Preview & Download Action */}
          {job.status === 'completed' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-2xl border border-emerald-500/30 bg-emerald-500/5 p-6 sm:p-8 space-y-6"
            >
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-[var(--color-border)]">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-md shadow-emerald-500/20">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="text-lg font-medium text-[var(--color-text)]">
                      Dubbing Complete!
                    </h4>
                    <p className="text-xs text-[var(--color-text-muted)]">
                      Your video has been dubbed into English and remuxed with zero video quality loss.
                    </p>
                  </div>
                </div>

                <Button
                  size="lg"
                  onClick={handleDownload}
                  leftIcon={<Download className="w-4 h-4" />}
                >
                  Download Dubbed Video
                </Button>
              </div>

              {/* Video Player Preview Mockup */}
              <div className="relative aspect-video rounded-xl bg-black overflow-hidden border border-[var(--color-border)] flex items-center justify-center group shadow-lg">
                <div className="text-center p-6 space-y-3">
                  <div className="w-16 h-16 rounded-full bg-white/10 backdrop-blur-md text-white flex items-center justify-center mx-auto group-hover:scale-110 transition-transform cursor-pointer">
                    <Play className="w-8 h-8 fill-current ml-1" />
                  </div>
                  <p className="text-sm font-medium text-white">
                    Dubbed Video Preview (English Audio Track)
                  </p>
                  <p className="text-xs text-white/60 font-mono">
                    Audio swapped via FFmpeg stream copy • 100% video track fidelity
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </motion.div>
      )}
    </div>
  );
}
