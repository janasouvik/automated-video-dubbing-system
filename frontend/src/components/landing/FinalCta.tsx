'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, Video } from 'lucide-react';
import { Button } from '@/components/ui/Button';

export function FinalCta() {
  return (
    <section className="py-20 relative overflow-hidden">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <div className="relative rounded-3xl border border-[var(--color-border)] bg-gradient-to-b from-[var(--color-surface)] to-[var(--color-surface-hover)] p-10 md:p-16 shadow-xl shadow-black/5 overflow-hidden">
          {/* Subtle Glow */}
          <div className="absolute -top-24 -right-24 w-96 h-96 bg-[var(--color-accent)]/15 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-[var(--color-accent)]/10 rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--color-accent-soft)] text-[var(--color-accent)] text-xs font-normal mb-6">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Ready for Local Video Dubbing</span>
            </div>

            <h2 className="text-3xl sm:text-4xl text-[var(--color-text)] mb-4 leading-tight">
              Start Dubbing Your Videos in Seconds
            </h2>

            <p className="text-base text-[var(--color-text-muted)] mb-8 leading-relaxed">
              Experience the power of local AI transcription, contextual translation, and zero-loss audio remuxing on your YouTube links today.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/signup" className="w-full sm:w-auto">
                <Button
                  size="lg"
                  rightIcon={<ArrowRight className="w-4 h-4" />}
                  className="w-full sm:w-auto"
                >
                  Get Started Free
                </Button>
              </Link>
              <Link href="/dashboard" className="w-full sm:w-auto">
                <Button
                  variant="secondary"
                  size="lg"
                  leftIcon={<Video className="w-4 h-4" />}
                  className="w-full sm:w-auto"
                >
                  Launch Dashboard
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
