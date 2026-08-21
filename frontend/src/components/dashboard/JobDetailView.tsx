'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  Play,
  Download,
  CheckCircle2,
  ExternalLink,
  Clock,
  Globe,
  Volume2,
  Film,
  Sparkles,
  RotateCcw,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { DubbingJob } from '@/lib/mock-data';

interface JobDetailViewProps {
  job: DubbingJob;
  onNewJob: () => void;
}

export function JobDetailView({ job, onNewJob }: JobDetailViewProps) {
  const handleDownload = () => {
    // TODO: Wire to backend download endpoint /api/v1/jobs/{job.id}/download
    alert(`Downloading dubbed video: ${job.title}`);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header Info */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[var(--color-border)]">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-mono text-[var(--color-accent)] bg-[var(--color-accent-soft)] px-2 py-0.5 rounded-md">
              {job.id}
            </span>
            <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-500">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Completed
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-medium text-[var(--color-text)]">
            {job.title}
          </h2>
          <a
            href={job.youtubeUrl}
            target="_blank"
            rel="noreferrer"
            className="text-xs text-[var(--color-accent)] hover:underline inline-flex items-center gap-1 mt-1 font-mono"
          >
            <span>{job.youtubeUrl}</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <Button
            variant="secondary"
            size="sm"
            onClick={onNewJob}
            leftIcon={<RotateCcw className="w-3.5 h-3.5" />}
          >
            New Project
          </Button>
          <Button
            size="sm"
            onClick={handleDownload}
            leftIcon={<Download className="w-4 h-4" />}
          >
            Download MP4
          </Button>
        </div>
      </div>

      {/* Video Player Preview Mockup */}
      <div className="relative aspect-video rounded-2xl bg-black overflow-hidden border border-[var(--color-border)] flex items-center justify-center group shadow-xl">
        <div className="text-center p-6 space-y-3">
          <div className="w-16 h-16 rounded-full bg-white/10 backdrop-blur-md text-white flex items-center justify-center mx-auto group-hover:scale-110 transition-transform cursor-pointer">
            <Play className="w-8 h-8 fill-current ml-1" />
          </div>
          <p className="text-sm font-medium text-white">
            Click to Play Dubbed Audio Preview
          </p>
          <p className="text-xs text-white/60 font-mono">
            Original Video Stream • English Neural Voiceover
          </p>
        </div>
      </div>

      {/* Pipeline Technical Telemetry Card */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]">
          <div className="flex items-center gap-2 text-xs text-[var(--color-text-muted)] mb-1">
            <Globe className="w-4 h-4 text-[var(--color-accent)]" />
            <span>Translation Engine</span>
          </div>
          <p className="text-sm font-medium text-[var(--color-text)]">
            IndicTrans2 Contextual
          </p>
          <p className="text-[11px] text-[var(--color-text-muted)] mt-0.5">
            {job.sourceLanguage || 'Detected'} → {job.targetLanguageLabel}
          </p>
        </div>

        <div className="p-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]">
          <div className="flex items-center gap-2 text-xs text-[var(--color-text-muted)] mb-1">
            <Volume2 className="w-4 h-4 text-[var(--color-accent)]" />
            <span>Voice Synthesis</span>
          </div>
          <p className="text-sm font-medium text-[var(--color-text)]">
            edge-tts Natural Neural
          </p>
          <p className="text-[11px] text-[var(--color-text-muted)] mt-0.5">
            Time-stretched speech alignment
          </p>
        </div>

        <div className="p-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]">
          <div className="flex items-center gap-2 text-xs text-[var(--color-text-muted)] mb-1">
            <Film className="w-4 h-4 text-[var(--color-accent)]" />
            <span>Video Remux Mode</span>
          </div>
          <p className="text-sm font-medium text-emerald-500">
            FFmpeg Stream Copy
          </p>
          <p className="text-[11px] text-[var(--color-text-muted)] mt-0.5">
            Zero re-encoding / 100% quality
          </p>
        </div>
      </div>

      {/* Transcript Sample Accordion */}
      <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6">
        <h4 className="text-sm font-medium text-[var(--color-text)] mb-3 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-[var(--color-accent)]" />
          <span>Synthesized Dialogue Segments Sample</span>
        </h4>
        <div className="space-y-2 text-xs">
          <div className="p-3 rounded-lg bg-[var(--color-surface-hover)] border border-[var(--color-border)] flex items-start justify-between gap-4 font-mono">
            <div>
              <span className="text-[var(--color-accent)]">[00:00 - 00:04]</span>{' '}
              <span className="text-[var(--color-text)]">
                &ldquo;Welcome back everyone. Today we are exploring the architecture of automated neural dubbing.&rdquo;
              </span>
            </div>
            <span className="text-[10px] text-emerald-500 shrink-0 font-sans">Synced</span>
          </div>

          <div className="p-3 rounded-lg bg-[var(--color-surface-hover)] border border-[var(--color-border)] flex items-start justify-between gap-4 font-mono">
            <div>
              <span className="text-[var(--color-accent)]">[00:05 - 00:11]</span>{' '}
              <span className="text-[var(--color-text)]">
                &ldquo;By isolating the video track and swapping the audio stream, we preserve visual fidelity completely.&rdquo;
              </span>
            </div>
            <span className="text-[10px] text-emerald-500 shrink-0 font-sans">Synced</span>
          </div>
        </div>
      </div>
    </div>
  );
}
