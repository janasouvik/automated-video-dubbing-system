'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Check, X, Users, Globe, BookOpen } from 'lucide-react';
import { slideUp, staggerContainer } from '@/lib/motion';

export function Overview() {
  const audiences = [
    {
      icon: Users,
      title: 'Content Creators',
      desc: 'Reach global non-native audiences on YouTube without paying thousands to dubbing agencies.',
    },
    {
      icon: BookOpen,
      title: 'Educators & Academics',
      desc: 'Translate lecture series and technical workshops into accessible English seamlessly.',
    },
    {
      icon: Globe,
      title: 'Global Organizations',
      desc: 'Localize product demos, support guides, and announcements with guaranteed video fidelity.',
    },
  ];

  return (
    <section id="overview" className="py-24 bg-[var(--color-surface)]/50 border-y border-[var(--color-border)]">
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
              Overview & Impact
            </span>
          </motion.div>
          <motion.h2 variants={slideUp} className="text-3xl sm:text-4xl text-[var(--color-text)] mb-4">
            Democratizing Global Video Accessibility
          </motion.h2>
          <motion.p variants={slideUp} className="text-base text-[var(--color-text-muted)]">
            Over 80% of regional educational and technical videos lack accessible English audio. VanniDub AI eliminates the manual overhead of translation and studio re-recording.
          </motion.p>
        </motion.div>

        {/* Comparison Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
          {/* Traditional Workflow */}
          <motion.div
            whileHover={{
              rotateX: 8,
              y: -2,
              scale: 0.99,
              transition: { duration: 0.25, ease: 'easeOut' },
            }}
            style={{ transformOrigin: 'bottom center', transformStyle: 'preserve-3d' }}
            className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 md:p-8 hover-push-top hover:border-red-400/80 transition-colors duration-200 cursor-pointer"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 rounded-lg bg-red-500/10 text-red-500 flex items-center justify-center">
                <X className="w-4 h-4" />
              </div>
              <h3 className="text-lg font-medium text-[var(--color-text)]">
                Traditional Dubbing Workflow
              </h3>
            </div>
            <ul className="space-y-4 text-sm text-[var(--color-text-muted)]">
              <li className="flex items-start gap-3">
                <X className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                <span>Manual transcription and subtitle timecoding taking hours per video.</span>
              </li>
              <li className="flex items-start gap-3">
                <X className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                <span>Hiring voiceover talent or manual studio recording sessions.</span>
              </li>
              <li className="flex items-start gap-3">
                <X className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                <span>Full video re-encoding introducing compression artifacts and high render times.</span>
              </li>
              <li className="flex items-start gap-3">
                <X className="w-4 h-4 text-red-400 mt-0.5 shrink-0" />
                <span>Cloud-dependent tools with privacy concerns and expensive per-minute pricing.</span>
              </li>
            </ul>
          </motion.div>

          {/* VanniDub AI Automated Pipeline */}
          <motion.div
            whileHover={{
              rotateX: 8,
              y: -2,
              scale: 0.99,
              transition: { duration: 0.25, ease: 'easeOut' },
            }}
            style={{ transformOrigin: 'bottom center', transformStyle: 'preserve-3d' }}
            className="rounded-2xl border-2 border-[var(--color-accent)]/60 bg-[var(--color-surface)] p-6 md:p-8 relative shadow-lg shadow-[var(--color-accent)]/5 hover-push-top hover:border-[var(--color-accent)] transition-colors duration-200 cursor-pointer"
          >
            <div className="absolute top-4 right-4 text-xs px-2.5 py-1 rounded-full bg-[var(--color-accent-soft)] text-[var(--color-accent)] font-medium">
              VanniDub Pipeline
            </div>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 rounded-lg bg-[var(--color-accent)] text-white flex items-center justify-center shadow-sm">
                <Check className="w-4 h-4 stroke-[2.5]" />
              </div>
              <h3 className="text-lg font-medium text-[var(--color-text)]">
                VanniDub AI Automated Pipeline
              </h3>
            </div>
            <ul className="space-y-4 text-sm text-[var(--color-text)]">
              <li className="flex items-start gap-3">
                <Check className="w-4 h-4 text-[var(--color-accent)] mt-0.5 shrink-0" />
                <span>Automatic Whisper speech-to-text with millisecond timestamp alignment.</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="w-4 h-4 text-[var(--color-accent)] mt-0.5 shrink-0" />
                <span>Contextual translation via IndicTrans2/NLLB preserving conversational tone.</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="w-4 h-4 text-[var(--color-accent)] mt-0.5 shrink-0" />
                <span>Stream-copy remuxing: zero video re-encoding, preserving 100% original quality.</span>
              </li>
              <li className="flex items-start gap-3">
                <Check className="w-4 h-4 text-[var(--color-accent)] mt-0.5 shrink-0" />
                <span>Runs entirely on your local infrastructure with live progress telemetry.</span>
              </li>
            </ul>
          </motion.div>
        </div>

        {/* Who it's for */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {audiences.map((aud) => {
            const Icon = aud.icon;
            return (
              <motion.div
                key={aud.title}
                whileHover={{
                  rotateX: 8,
                  y: -2,
                  scale: 0.99,
                  transition: { duration: 0.25, ease: 'easeOut' },
                }}
                style={{ transformOrigin: 'bottom center', transformStyle: 'preserve-3d' }}
                className="p-5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] hover-push-top hover:border-[var(--color-accent)]/80 transition-colors duration-200 cursor-pointer"
              >
                <div className="w-9 h-9 rounded-lg bg-[var(--color-accent-soft)] text-[var(--color-accent)] flex items-center justify-center mb-3">
                  <Icon className="w-4 h-4" />
                </div>
                <h4 className="text-base font-medium text-[var(--color-text)] mb-1">
                  {aud.title}
                </h4>
                <p className="text-xs text-[var(--color-text-muted)] leading-relaxed">
                  {aud.desc}
                </p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
