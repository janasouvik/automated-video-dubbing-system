'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Zap,
  ShieldCheck,
  Activity,
  Sparkles,
  Timer,
  GitBranch,
  ChevronLeft,
  ChevronRight,
  ArrowRight,
  CheckCircle2,
} from 'lucide-react';
import { slideUp, staggerContainer } from '@/lib/motion';

export function Features() {
  const features = [
    {
      id: 'zero-reencode',
      icon: Zap,
      badge: 'Performance',
      title: 'Zero Video Re-encoding',
      subtitle: 'FFmpeg Lossless Stream Copy',
      description:
        'Uses FFmpeg stream-copying to swap audio tracks directly in the MP4 container, maintaining 100% original visual bitrates with instantaneous render times.',
      stats: '10x Faster Turnaround',
    },
    {
      id: 'local-privacy',
      icon: ShieldCheck,
      badge: 'Security',
      title: 'Local Privacy & Control',
      subtitle: 'Self-Hosted AI Execution',
      description:
        'All AI models execute directly on your local system or self-hosted GPU instance, keeping proprietary videos safe from third-party cloud loggers.',
      stats: '100% Data Sovereignty',
    },
    {
      id: 'realtime-telemetry',
      icon: Activity,
      badge: 'Observability',
      title: 'Live Stage Telemetry',
      subtitle: 'Stage-by-Stage Diagnostics',
      description:
        'Continuous status reporting with progress percentages, real-time stage transitions, and detailed failure diagnostics for every dubbing job.',
      stats: '5-Stage Granular Tracking',
    },
    {
      id: 'contextual-translation',
      icon: Sparkles,
      badge: 'AI Precision',
      title: 'Conversational Phrasing',
      subtitle: 'IndicTrans2 & NLLB Engines',
      description:
        'State-of-the-art translation engines preserve cultural idioms and conversational tone rather than clumsy word-by-word literal translations.',
      stats: 'Human-Grade Translation',
    },
    {
      id: 'time-stretching',
      icon: Timer,
      badge: 'Synchronization',
      title: 'Dynamic Time-Stretching',
      subtitle: 'Frame-Accurate Voice Alignment',
      description:
        'Synthesized speech audio clips are smoothly accelerated or padded to match the precise timestamp bounds of each speaker segment.',
      stats: 'Millisecond Sync Precision',
    },
    {
      id: 'modular-arch',
      icon: GitBranch,
      badge: 'Extensibility',
      title: 'Future-Proof Architecture',
      subtitle: 'Diarization & Voice Cloning Ready',
      description:
        'Modular pipeline built for quick drop-in integration of pyannote.audio speaker diarization and Coqui XTTS voice cloning models.',
      stats: 'Plugin-Ready ML Pipeline',
    },
  ];

  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState<'left' | 'right'>('right');

  const total = features.length;

  const handlePrev = useCallback(() => {
    setDirection('left');
    setCurrentIndex((prev) => (prev === 0 ? total - 1 : prev - 1));
  }, [total]);

  const handleNext = useCallback(() => {
    setDirection('right');
    setCurrentIndex((prev) => (prev === total - 1 ? 0 : prev + 1));
  }, [total]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') handlePrev();
      if (e.key === 'ArrowRight') handleNext();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handlePrev, handleNext]);

  const prevIndex = (currentIndex - 1 + total) % total;
  const nextIndex = (currentIndex + 1) % total;

  const currentFeature = features[currentIndex];
  const prevFeature = features[prevIndex];
  const nextFeature = features[nextIndex];

  const CurrentIcon = currentFeature.icon;
  const PrevIcon = prevFeature.icon;
  const NextIcon = nextFeature.icon;

  return (
    <section id="features" className="py-24 overflow-hidden relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
          variants={staggerContainer}
          className="text-center max-w-3xl mx-auto mb-16"
        >
          <motion.div variants={slideUp} className="inline-flex items-center gap-2 mb-3">
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-accent)]">
              Core Capabilities
            </span>
          </motion.div>
          <motion.h2 variants={slideUp} className="text-3xl sm:text-4xl text-[var(--color-text)] mb-4">
            Engineered for Precision & Speed
          </motion.h2>
          <motion.p variants={slideUp} className="text-base text-[var(--color-text-muted)]">
            Explore the core architectural breakthroughs powering lossless, real-time video translation.
          </motion.p>
        </motion.div>

        {/* 3D Carousel Stage with Left/Right Blurred Previews */}
        <div className="relative max-w-5xl mx-auto flex items-center justify-center my-8 min-h-[380px]">
          {/* Previous Card Preview (Blurred on Left) */}
          <div
            onClick={handlePrev}
            className="hidden md:block absolute -left-8 lg:left-0 w-80 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 filter blur-[3.5px] opacity-45 scale-90 -rotate-3 cursor-pointer hover:opacity-75 hover:blur-[2px] transition-all duration-300 z-10 select-none shadow-lg"
            title="Click to view previous feature"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-xl bg-[var(--color-accent-soft)] text-[var(--color-accent)] flex items-center justify-center">
                <PrevIcon className="w-5 h-5" />
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[var(--color-surface-hover)] text-[var(--color-text-muted)] border border-[var(--color-border)]">
                {prevFeature.badge}
              </span>
            </div>
            <h3 className="text-base font-medium text-[var(--color-text)] mb-1 truncate">
              {prevFeature.title}
            </h3>
            <p className="text-xs font-mono text-[var(--color-accent)] mb-2">
              {prevFeature.subtitle}
            </p>
            <p className="text-xs text-[var(--color-text-muted)] line-clamp-3 leading-relaxed">
              {prevFeature.description}
            </p>
          </div>

          {/* Center Card (Sharp, Focused, Interactive) */}
          <AnimatePresence mode="wait">
            <motion.div
              key={currentFeature.id}
              initial={{
                opacity: 0,
                x: direction === 'right' ? 60 : -60,
                scale: 0.94,
              }}
              animate={{
                opacity: 1,
                x: 0,
                scale: 1,
              }}
              exit={{
                opacity: 0,
                x: direction === 'right' ? -60 : 60,
                scale: 0.94,
              }}
              transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
              className="relative w-full max-w-lg rounded-3xl border-2 border-[var(--color-accent)] bg-[var(--color-surface)] p-8 sm:p-10 shadow-2xl shadow-[var(--color-accent)]/15 z-20"
            >
              {/* Card Top Bar */}
              <div className="flex items-center justify-between mb-6">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-[#2685e6] to-[#3499FD] text-white flex items-center justify-center shadow-md shadow-[#3499fd]/30">
                  <CurrentIcon className="w-7 h-7" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono px-3 py-1 rounded-full bg-[var(--color-accent-soft)] text-[var(--color-accent)] font-medium border border-[var(--color-accent)]/20">
                    {currentFeature.badge}
                  </span>
                  <span className="text-xs font-mono text-[var(--color-text-muted)]">
                    0{currentIndex + 1} / 0{total}
                  </span>
                </div>
              </div>

              {/* Title & Subtitle */}
              <h3 className="text-2xl font-medium text-[var(--color-text)] mb-1.5 tracking-tight">
                {currentFeature.title}
              </h3>
              <p className="text-xs font-mono text-[var(--color-accent)] mb-4">
                {currentFeature.subtitle}
              </p>

              {/* Description */}
              <p className="text-sm text-[var(--color-text-muted)] leading-relaxed mb-6">
                {currentFeature.description}
              </p>

              {/* Stats Highlight Bar */}
              <div className="pt-4 border-t border-[var(--color-border)] flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-medium text-emerald-500">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>{currentFeature.stats}</span>
                </div>
                <div className="text-[11px] text-[var(--color-text-muted)] flex items-center gap-1 font-mono">
                  <span>Use ← → keys</span>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>

          {/* Next Card Preview (Blurred on Right) */}
          <div
            onClick={handleNext}
            className="hidden md:block absolute -right-8 lg:right-0 w-80 rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 filter blur-[3.5px] opacity-45 scale-90 rotate-3 cursor-pointer hover:opacity-75 hover:blur-[2px] transition-all duration-300 z-10 select-none shadow-lg"
            title="Click to view next feature"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 rounded-xl bg-[var(--color-accent-soft)] text-[var(--color-accent)] flex items-center justify-center">
                <NextIcon className="w-5 h-5" />
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[var(--color-surface-hover)] text-[var(--color-text-muted)] border border-[var(--color-border)]">
                {nextFeature.badge}
              </span>
            </div>
            <h3 className="text-base font-medium text-[var(--color-text)] mb-1 truncate">
              {nextFeature.title}
            </h3>
            <p className="text-xs font-mono text-[var(--color-accent)] mb-2">
              {nextFeature.subtitle}
            </p>
            <p className="text-xs text-[var(--color-text-muted)] line-clamp-3 leading-relaxed">
              {nextFeature.description}
            </p>
          </div>
        </div>

        {/* Controls: Left / Right Navigation Buttons & Dots Indicator */}
        <div className="flex flex-col items-center justify-center gap-4 mt-8">
          <div className="flex items-center gap-4">
            {/* Left Button */}
            <button
              type="button"
              onClick={handlePrev}
              className="w-11 h-11 rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] hover:bg-[var(--color-surface-hover)] text-[var(--color-text)] flex items-center justify-center transition-all duration-200 hover:scale-105 active:scale-95 hover:border-[var(--color-accent)] shadow-sm cursor-pointer"
              aria-label="Previous feature"
              title="Previous feature (or left arrow key)"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>

            {/* Pagination Indicator Dots */}
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[var(--color-surface)] border border-[var(--color-border)] shadow-2xs">
              {features.map((feat, idx) => (
                <button
                  key={feat.id}
                  type="button"
                  onClick={() => {
                    setDirection(idx > currentIndex ? 'right' : 'left');
                    setCurrentIndex(idx);
                  }}
                  className={`h-2 rounded-full transition-all duration-300 cursor-pointer ${
                    idx === currentIndex
                      ? 'w-6 bg-[var(--color-accent)] shadow-xs shadow-[#3499fd]/40'
                      : 'w-2 bg-[var(--color-border)] hover:bg-[var(--color-text-muted)]'
                  }`}
                  aria-label={`Jump to feature ${idx + 1}`}
                />
              ))}
            </div>

            {/* Right Button */}
            <button
              type="button"
              onClick={handleNext}
              className="w-11 h-11 rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] hover:bg-[var(--color-surface-hover)] text-[var(--color-text)] flex items-center justify-center transition-all duration-200 hover:scale-105 active:scale-95 hover:border-[var(--color-accent)] shadow-sm cursor-pointer"
              aria-label="Next feature"
              title="Next feature (or right arrow key)"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
