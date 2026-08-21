'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Check,
  Loader2,
  AlertCircle,
  Clock,
  DownloadCloud,
  Mic,
  Languages,
  Volume2,
  Film,
} from 'lucide-react';
import { PipelineStageInfo, StageStatus } from '@/lib/mock-data';

interface ProgressStageTrackerProps {
  stages: PipelineStageInfo[];
  currentStageId: string;
  overallProgress: number;
}

const stageIcons: Record<string, React.ElementType> = {
  fetch: DownloadCloud,
  transcribe: Mic,
  translate: Languages,
  synthesize: Volume2,
  remux: Film,
};

export function ProgressStageTracker({
  stages,
  currentStageId,
  overallProgress,
}: ProgressStageTrackerProps) {
  return (
    <div className="w-full rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6 md:p-8">
      {/* Top Header & Overall Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-base font-medium text-[var(--color-text)]">
              Dubbing Pipeline Progress
            </h3>
            <p className="text-xs text-[var(--color-text-muted)] mt-0.5">
              Live telemetry through local pipeline workers
            </p>
          </div>
          <div className="text-right">
            <span className="text-xl font-medium text-[var(--color-accent)] font-mono">
              {Math.round(overallProgress)}%
            </span>
          </div>
        </div>

        {/* Outer track */}
        <div className="w-full h-2 rounded-full bg-[var(--color-border)] overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-[#2685e6] to-[#3499FD] rounded-full"
            initial={{ width: '0%' }}
            animate={{ width: `${Math.min(100, Math.max(0, overallProgress))}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Vertical Pipeline Stage Flow */}
      <div className="relative space-y-6">
        {stages.map((stage, idx) => {
          const Icon = stageIcons[stage.id] || Clock;
          const isCompleted = stage.status === 'completed';
          const isInProgress = stage.status === 'in_progress';
          const isFailed = stage.status === 'failed';
          const isPending = stage.status === 'pending';
          const isLast = idx === stages.length - 1;

          return (
            <div key={stage.id} className="relative flex items-start gap-4 group">
              {/* Connecting Vertical Line */}
              {!isLast && (
                <div
                  className="absolute left-5 top-10 bottom-0 w-0.5 -ml-[1px] bg-[var(--color-border)] z-0"
                  aria-hidden="true"
                >
                  <motion.div
                    className="w-full bg-[var(--color-accent)]"
                    initial={{ height: '0%' }}
                    animate={{
                      height: isCompleted ? '100%' : isInProgress ? '50%' : '0%',
                    }}
                    transition={{ duration: 0.4, ease: 'easeInOut' }}
                  />
                </div>
              )}

              {/* Status Node Icon */}
              <div className="relative z-10 shrink-0">
                {isCompleted ? (
                  <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="w-10 h-10 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-sm shadow-emerald-500/20"
                  >
                    <Check className="w-5 h-5 stroke-[2.5]" />
                  </motion.div>
                ) : isInProgress ? (
                  <div className="relative w-10 h-10 rounded-full bg-[var(--color-accent)] text-white flex items-center justify-center shadow-md shadow-[#3499fd]/30">
                    {/* Pulsing ring animation */}
                    <motion.div
                      className="absolute inset-0 rounded-full border-2 border-[var(--color-accent)]"
                      animate={{
                        scale: [1, 1.35, 1],
                        opacity: [0.8, 0, 0.8],
                      }}
                      transition={{
                        duration: 1.8,
                        repeat: Infinity,
                        ease: 'easeInOut',
                      }}
                    />
                    <Loader2 className="w-5 h-5 animate-spin" />
                  </div>
                ) : isFailed ? (
                  <div className="w-10 h-10 rounded-full bg-red-500 text-white flex items-center justify-center">
                    <AlertCircle className="w-5 h-5" />
                  </div>
                ) : (
                  <div className="w-10 h-10 rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text-muted)] flex items-center justify-center">
                    <Icon className="w-4 h-4" />
                  </div>
                )}
              </div>

              {/* Stage Details */}
              <div className="flex-1 min-w-0 pt-1 pb-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 mb-1">
                  <div className="flex items-center gap-2">
                    <h4
                      className={`text-sm font-medium ${
                        isInProgress
                          ? 'text-[var(--color-accent)]'
                          : isCompleted
                          ? 'text-[var(--color-text)]'
                          : 'text-[var(--color-text-muted)]'
                      }`}
                    >
                      {stage.name}
                    </h4>
                    <span className="text-[11px] font-mono px-1.5 py-0.5 rounded bg-[var(--color-surface-hover)] border border-[var(--color-border)] text-[var(--color-text-muted)]">
                      {stage.tool}
                    </span>
                  </div>

                  {/* Status Badge */}
                  <div>
                    {isCompleted && (
                      <span className="inline-flex items-center text-[11px] font-medium text-emerald-500">
                        Complete
                      </span>
                    )}
                    {isInProgress && (
                      <span className="inline-flex items-center gap-1.5 text-[11px] font-medium text-[var(--color-accent)]">
                        <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-accent)] animate-ping" />
                        In Progress ({stage.progressPercent}%)
                      </span>
                    )}
                    {isPending && (
                      <span className="text-[11px] text-[var(--color-text-muted)]/70">
                        Pending
                      </span>
                    )}
                    {isFailed && (
                      <span className="text-[11px] font-medium text-red-500">
                        Failed
                      </span>
                    )}
                  </div>
                </div>

                <p className="text-xs text-[var(--color-text-muted)] mb-1">
                  {stage.description}
                </p>

                {/* Live Message if in progress or completed */}
                {(isInProgress || stage.message) && (
                  <p className="text-[11px] font-mono text-[var(--color-text-muted)]/90 bg-[var(--color-surface-hover)] px-2.5 py-1 rounded-md border border-[var(--color-border)] mt-1.5 inline-block">
                    {stage.message || 'Processing...'}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
