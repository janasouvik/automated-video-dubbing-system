'use client';

import React, { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion, useScroll, useTransform } from 'framer-motion';
import {
  Sparkles,
  ArrowRight,
  Play,
  Volume2,
  Layers,
  Zap,
  CheckCircle2,
  Subtitles,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { slideUp, staggerContainer } from '@/lib/motion';

export function Hero() {
  const router = useRouter();
  const [url, setUrl] = useState('');

  // Scroll animation for popup/popdown on scroll down and up
  const diagramRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: diagramRef,
    offset: ['start end', 'center center', 'end start'],
  });

  const scale = useTransform(scrollYProgress, [0, 0.45, 0.85, 1], [0.88, 1, 1, 0.92]);
  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.85, 1], [0.35, 1, 1, 0.5]);
  const y = useTransform(scrollYProgress, [0, 0.45, 0.85, 1], [50, 0, 0, -30]);

  const handleQuickStart = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      router.push(`/dashboard?url=${encodeURIComponent(url.trim())}`);
    } else {
      router.push('/dashboard');
    }
  };

  return (
    <section
      id="hero"
      className="relative pt-32 pb-20 md:pt-40 md:pb-28 overflow-hidden"
    >
      {/* Subtle Background Glow (Light Mode only) */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-[var(--color-accent)]/10 blur-[120px] rounded-full pointer-events-none -z-10 dark:hidden" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="text-center max-w-3xl mx-auto"
        >
          {/* Tag badge */}
          <motion.div variants={slideUp} className="inline-flex items-center gap-2 mb-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-accent-soft)] border border-[var(--color-accent)]/20 text-[var(--color-accent)] text-xs font-normal">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Local Speech Synthesis & Remux Engine</span>
            </div>
          </motion.div>

          {/* Main Headline */}
          <motion.h1
            variants={slideUp}
            className="text-4xl sm:text-5xl md:text-6xl tracking-tight text-[var(--color-text)] leading-[1.1] mb-6"
          >
            Automated Video Dubbing with{' '}
            <span className="text-[var(--color-accent)]">Natural AI Speech</span>
          </motion.h1>

          {/* Subheading */}
          <motion.p
            variants={slideUp}
            className="text-base sm:text-lg text-[var(--color-text-muted)] max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            Paste a YouTube URL. Our automated pipeline extracts audio, transcribes with Whisper,
            translates contextually, synthesizes expressive English speech, and remuxes into the original
            video track without re-encoding.
          </motion.p>

          {/* URL Input CTA Form */}
          <motion.form
            variants={slideUp}
            onSubmit={handleQuickStart}
            className="max-w-xl mx-auto mb-8"
          >
            <div className="p-1.5 rounded-xl bg-[var(--color-input-bg)] border border-[var(--color-input-border)] shadow-lg shadow-black/10 flex flex-col sm:flex-row gap-2 focus-within:border-[var(--color-accent)] focus-within:ring-2 focus-within:ring-[var(--color-accent)]/30 transition-all duration-200">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="flex-1 px-4 py-2.5 text-sm bg-transparent text-[var(--color-input-text)] placeholder:text-[#64748B] focus:outline-none"
              />
              <Button
                type="submit"
                size="md"
                rightIcon={<ArrowRight className="w-4 h-4" />}
                className="shrink-0"
              >
                Dub Video
              </Button>
            </div>
          </motion.form>

          {/* Value Badges */}
          <motion.div
            variants={slideUp}
            className="flex flex-wrap items-center justify-center gap-6 text-xs text-[var(--color-text-muted)]"
          >
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-[var(--color-accent)]" />
              <span>Zero Video Quality Loss</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-[var(--color-accent)]" />
              <span>Time-Stretched TTS Sync</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-[var(--color-accent)]" />
              <span>Local Pipeline Speed</span>
            </div>
          </motion.div>
        </motion.div>

        {/* Hero Visual: Pipeline Architecture Diagram with Inverted Theme & Scroll Pop-up/Pop-down Animation */}
        <motion.div
          ref={diagramRef}
          style={{ scale, opacity, y }}
          className="mt-14 max-w-4xl mx-auto transition-shadow duration-300"
        >
          {/* Outer Window Container: Sleek Dark Terminal UI */}
          <div className="relative rounded-2xl border border-[#1E293B] bg-[#0A0E17] text-white p-5 md:p-8 shadow-2xl shadow-black/25 overflow-hidden">
            {/* Header of mock window */}
            <div className="flex items-center justify-between pb-4 mb-6 border-b border-[#1E293B]">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-400/90" />
                <div className="w-3 h-3 rounded-full bg-amber-400/90" />
                <div className="w-3 h-3 rounded-full bg-emerald-400/90" />
                <span className="ml-2 text-xs font-mono text-zinc-400">
                  pipeline-stream // worker-01 (live)
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs px-2.5 py-1 rounded-md bg-[#132238] text-sky-400 border border-sky-500/20 font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse" />
                Stream Copy Mode
              </div>
            </div>

            {/* Pipeline Stage Cards Flow (Stable cards without hover movement) */}
            <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 relative select-none">
              {/* Step 1 */}
              <div className="p-3.5 rounded-xl border border-[#1E293B] bg-[#111724] text-white flex flex-col justify-between">
                <div>
                  <div className="w-7 h-7 rounded-lg bg-[#1B273D] text-sky-400 flex items-center justify-center mb-2.5">
                    <Play className="w-3.5 h-3.5" />
                  </div>
                  <div className="text-xs font-medium text-white">1. Audio Fetch</div>
                  <div className="text-[11px] text-zinc-400 mt-0.5">yt-dlp stream extraction</div>
                </div>
                <div className="mt-3 text-[10px] text-emerald-400 font-medium flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Ready
                </div>
              </div>

              {/* Step 2 */}
              <div className="p-3.5 rounded-xl border border-[#1E293B] bg-[#111724] text-white flex flex-col justify-between">
                <div>
                  <div className="w-7 h-7 rounded-lg bg-[#1B273D] text-sky-400 flex items-center justify-center mb-2.5">
                    <Subtitles className="w-3.5 h-3.5" />
                  </div>
                  <div className="text-xs font-medium text-white">2. Transcribe</div>
                  <div className="text-[11px] text-zinc-400 mt-0.5">Whisper time-aligned ASR</div>
                </div>
                <div className="mt-3 text-[10px] text-emerald-400 font-medium flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Ready
                </div>
              </div>

              {/* Step 3 */}
              <div className="p-3.5 rounded-xl border border-[#1E293B] bg-[#111724] text-white flex flex-col justify-between">
                <div>
                  <div className="w-7 h-7 rounded-lg bg-[#1B273D] text-sky-400 flex items-center justify-center mb-2.5">
                    <Layers className="w-3.5 h-3.5" />
                  </div>
                  <div className="text-xs font-medium text-white">3. Translate</div>
                  <div className="text-[11px] text-zinc-400 mt-0.5">IndicTrans2 / NLLB Context</div>
                </div>
                <div className="mt-3 text-[10px] text-emerald-400 font-medium flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Ready
                </div>
              </div>

              {/* Step 4 (Active Stage) */}
              <div className="p-3.5 rounded-xl border-2 border-sky-500/80 bg-[#0E223D] text-white flex flex-col justify-between shadow-md shadow-sky-500/10">
                <div>
                  <div className="w-7 h-7 rounded-lg bg-sky-500 text-white flex items-center justify-center mb-2.5 shadow-xs">
                    <Volume2 className="w-3.5 h-3.5" />
                  </div>
                  <div className="text-xs font-medium text-white">4. Synthesize</div>
                  <div className="text-[11px] text-zinc-300 mt-0.5">Edge TTS + Time Stretch</div>
                </div>
                <div className="mt-3 text-[10px] text-sky-400 font-medium flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-ping" /> Active
                </div>
              </div>

              {/* Step 5 */}
              <div className="p-3.5 rounded-xl border border-[#1E293B] bg-[#111724] text-white flex flex-col justify-between">
                <div>
                  <div className="w-7 h-7 rounded-lg bg-[#1B273D] text-sky-400 flex items-center justify-center mb-2.5">
                    <Zap className="w-3.5 h-3.5" />
                  </div>
                  <div className="text-xs font-medium text-white">5. Remux</div>
                  <div className="text-[11px] text-zinc-400 mt-0.5">FFmpeg stream copy</div>
                </div>
                <div className="mt-3 text-[10px] text-zinc-500 font-medium">
                  Pending
                </div>
              </div>
            </div>

            {/* Bottom Telemetry Bar */}
            <div className="mt-5 p-3 rounded-xl bg-[#080B12] border border-[#1E293B] text-zinc-400 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs font-mono">
              <div className="flex items-center gap-3">
                <span className="text-zinc-500">Source Video:</span>
                <span className="text-white text-[11px] truncate max-w-[200px] sm:max-w-xs font-sans">
                  youtube.com/watch?v=demo_pipeline
                </span>
              </div>
              <div className="flex items-center gap-4 text-zinc-400">
                <span>FPS: <strong className="text-white font-normal">Original 60fps</strong></span>
                <span>Video Track: <strong className="text-emerald-400 font-normal">Lossless Copied</strong></span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
