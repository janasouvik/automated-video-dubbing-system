'use client';

import React from 'react';
import Link from 'next/link';
import { useSession, signOut } from 'next-auth/react';
import {
  Video,
  Plus,
  Clock,
  CheckCircle2,
  AlertCircle,
  Loader2,
  LogOut,
  PanelLeftClose,
  ChevronLeft,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { DubbingJob } from '@/lib/mock-data';

interface SidebarProps {
  jobs: DubbingJob[];
  activeJobId: string | null;
  onSelectJob: (job: DubbingJob | null) => void;
  isOpen: boolean;
  onClose: () => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export function Sidebar({
  jobs,
  activeJobId,
  onSelectJob,
  isOpen,
  onClose,
  isCollapsed,
  onToggleCollapse,
}: SidebarProps) {
  const { data: session } = useSession();

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black/50 backdrop-blur-xs z-40 md:hidden"
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-72 bg-[var(--color-surface)] border-r border-[var(--color-border)] flex flex-col justify-between transition-all duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } ${isCollapsed ? 'md:-translate-x-full' : 'md:translate-x-0'}`}
      >
        {/* Top Header & Logo */}
        <div className="p-4 border-b border-[var(--color-border)]">
          <div className="flex items-center justify-between mb-4">
            <Link
              href="/"
              className="flex items-center gap-2.5 group"
              onClick={() => {
                onSelectJob(null);
                onClose();
              }}
            >
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#2685e6] to-[#3499FD] flex items-center justify-center text-white shadow-sm shadow-[#3499fd]/30">
                <Video className="w-4 h-4" />
              </div>
              <div className="flex items-center gap-1.5">
                <span className="text-base font-medium text-[var(--color-text)]">
                  VanniDub
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-[var(--color-accent-soft)] text-[var(--color-accent)] font-medium">
                  AI
                </span>
              </div>
            </Link>

            {/* Collapse Sidebar Button */}
            <button
              type="button"
              onClick={() => {
                onToggleCollapse();
                onClose();
              }}
              className="w-8 h-8 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] hover:bg-[var(--color-surface-hover)] text-[var(--color-text-muted)] hover:text-[var(--color-text)] flex items-center justify-center transition-colors cursor-pointer"
              title="Collapse sidebar"
              aria-label="Collapse sidebar"
            >
              <PanelLeftClose className="w-4 h-4" />
            </button>
          </div>

          {/* New Dub Primary Button */}
          <Button
            onClick={() => {
              onSelectJob(null);
              onClose();
            }}
            className="w-full justify-start"
            leftIcon={<Plus className="w-4 h-4" />}
          >
            New Dub Project
          </Button>
        </div>

        {/* History / Recent Jobs List */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          <div className="px-2 pb-2 text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider flex items-center justify-between">
            <span>Recent Projects</span>
            <span className="text-[10px] font-mono">{jobs.length}</span>
          </div>

          {jobs.length === 0 ? (
            <div className="px-3 py-8 text-center text-xs text-[var(--color-text-muted)]">
              <Clock className="w-6 h-6 mx-auto mb-2 opacity-40" />
              <p>No dubbing projects yet.</p>
              <p className="text-[11px] opacity-75 mt-0.5">Start by pasting a YouTube URL.</p>
            </div>
          ) : (
            jobs.map((job) => {
              const isSelected = activeJobId === job.id;
              return (
                <button
                  key={job.id}
                  type="button"
                  onClick={() => {
                    onSelectJob(job);
                    onClose();
                  }}
                  className={`w-full text-left px-3 py-2.5 rounded-xl border transition-all duration-150 group cursor-pointer ${
                    isSelected
                      ? 'bg-[var(--color-accent-soft)]/40 border-[var(--color-accent)]/40 shadow-xs'
                      : 'bg-transparent border-transparent hover:bg-[var(--color-surface-hover)] hover:border-[var(--color-border)]'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={`text-xs font-normal truncate max-w-[210px] ${
                        isSelected
                          ? 'text-[var(--color-accent)] font-medium'
                          : 'text-[var(--color-text)]'
                      }`}
                    >
                      {job.title || job.youtubeUrl}
                    </span>

                    {/* Status indicator icon */}
                    <div className="shrink-0">
                      {job.status === 'completed' && (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
                      )}
                      {job.status === 'in_progress' && (
                        <Loader2 className="w-3.5 h-3.5 text-[var(--color-accent)] animate-spin" />
                      )}
                      {job.status === 'failed' && (
                        <AlertCircle className="w-3.5 h-3.5 text-red-500" />
                      )}
                    </div>
                  </div>
                </button>
              );
            })
          )}
        </div>

        {/* Bottom User Area without theme toggle */}
        <div className="p-3 border-t border-[var(--color-border)] bg-[var(--color-surface)] flex items-center justify-between gap-2">
          {/* User info */}
          <div className="flex items-center gap-2.5 min-w-0 flex-1">
            <div className="w-8 h-8 rounded-full bg-[var(--color-accent-soft)] text-[var(--color-accent)] flex items-center justify-center font-medium text-xs shrink-0 border border-[var(--color-accent)]/20">
              {session?.user?.name ? session.user.name.charAt(0).toUpperCase() : 'U'}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-medium text-[var(--color-text)] truncate">
                {session?.user?.name || 'VanniDub User'}
              </p>
              <p className="text-[10px] text-[var(--color-text-muted)] truncate">
                {session?.user?.email || 'demo@vannidub.ai'}
              </p>
            </div>
          </div>

          {/* Sign out action */}
          <button
            type="button"
            onClick={() => signOut({ callbackUrl: '/login' })}
            className="w-8 h-8 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] hover:bg-red-500/10 hover:text-red-500 text-[var(--color-text-muted)] flex items-center justify-center transition-colors cursor-pointer"
            title="Sign Out"
            aria-label="Sign Out"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </aside>
    </>
  );
}
