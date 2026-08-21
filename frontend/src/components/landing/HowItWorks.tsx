'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { DownloadCloud, Mic, Languages, Volume2, Film, CheckCircle2 } from 'lucide-react';
import { slideUp, staggerContainer } from '@/lib/motion';

export function HowItWorks() {
  const stages = [
    {
      step: '01',
      title: 'Audio Fetch & Demuxing',
      tool: 'yt-dlp + FFmpeg',
      description:
        'Extracts the clean audio stream directly from the YouTube link into local workspace storage, isolating the visual stream for lossless downstream remuxing.',
      icon: DownloadCloud,
      highlight: 'Ultra-fast direct stream download',
    },
    {
      step: '02',
      title: 'Speech-to-Text Transcription',
      tool: 'OpenAI Whisper',
      description:
        'Converts original spoken speech into millisecond-accurate timestamped text segments with automatic punctuation and language detection.',
      icon: Mic,
      highlight: 'Segment-level timestamping',
    },
    {
      step: '03',
      title: 'Contextual AI Translation',
      tool: 'IndicTrans2 / NLLB',
      description:
        'Translates spoken dialogues into natural, conversational English idioms rather than awkward literal word substitutions, preserving the original tone.',
      icon: Languages,
      highlight: 'Conversational nuance preserved',
    },
    {
      step: '04',
      title: 'Neural Speech Synthesis',
      tool: 'edge-tts + Time-Stretching',
      description:
        'Generates human-like expressive English voiceovers, dynamically stretching or compressing audio duration to precisely align with speaker on-screen cuts.',
      icon: Volume2,
      highlight: 'Natural cadence & pacing sync',
    },
    {
      step: '05',
      title: 'Lossless Video Remuxing',
      tool: 'FFmpeg Stream Copy',
      description:
        'Muxes the final synthesized English audio directly into the original video container. No video re-encoding means 100% original quality and near-instant completion.',
      icon: Film,
      highlight: 'Zero visual quality loss',
    },
  ];

  return (
    <section id="how-it-works" className="py-24 bg-[var(--color-surface)]/50 border-y border-[var(--color-border)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
          variants={staggerContainer}
          className="text-center max-w-3xl mx-auto mb-16"
        >
          <motion.div variants={slideUp} className="inline-flex items-center gap-2 mb-3">
            <span className="text-xs font-medium uppercase tracking-wider text-[var(--color-accent)]">
              Architecture Breakdown
            </span>
          </motion.div>
          <motion.h2 variants={slideUp} className="text-3xl sm:text-4xl text-[var(--color-text)] mb-4">
            How VanniDub AI Works
          </motion.h2>
          <motion.p variants={slideUp} className="text-base text-[var(--color-text-muted)]">
            A battle-tested 5-stage automated pipeline engineered for speed, privacy, and natural conversational cadence.
          </motion.p>
        </motion.div>

        {/* 5 Stages Grid / Timeline */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 lg:gap-6">
          {stages.map((stage, idx) => {
            const Icon = stage.icon;
            return (
              <motion.div
                key={stage.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                whileHover={{
                  y: -4,
                  rotate: [0, -1.2, 1.2, -0.8, 0.8, 0],
                  transition: { duration: 0.35, ease: 'easeInOut' },
                }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: idx * 0.1 }}
                className="relative rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5 flex flex-col justify-between hover-shake-card hover:border-[var(--color-accent)]/80 hover:shadow-xl hover:shadow-[var(--color-accent)]/10 transition-colors duration-200 group cursor-pointer"
              >
                <div>
                  {/* Step & Icon Bar */}
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-mono font-medium text-[var(--color-accent)] bg-[var(--color-accent-soft)] px-2 py-0.5 rounded-md">
                      {stage.step}
                    </span>
                    <div className="w-8 h-8 rounded-xl bg-[var(--color-surface-hover)] border border-[var(--color-border)] flex items-center justify-center text-[var(--color-text-muted)] group-hover:text-[var(--color-accent)] transition-colors">
                      <Icon className="w-4 h-4" />
                    </div>
                  </div>

                  {/* Title & Tool */}
                  <h3 className="text-base font-medium text-[var(--color-text)] mb-1">
                    {stage.title}
                  </h3>
                  <p className="text-xs font-mono text-[var(--color-accent)] mb-3">
                    {stage.tool}
                  </p>

                  {/* Description */}
                  <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">
                    {stage.description}
                  </p>
                </div>

                {/* Highlight chip */}
                <div className="mt-5 pt-3 border-t border-[var(--color-border)] flex items-center gap-1.5 text-[11px] text-[var(--color-text-muted)]">
                  <CheckCircle2 className="w-3 h-3 text-[var(--color-accent)] shrink-0" />
                  <span className="truncate">{stage.highlight}</span>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
