'use client';

import React from 'react';
import Link from 'next/link';
import { PanelLeft, Home, ChevronRight, Sparkles } from 'lucide-react';
import { ThemeToggle } from '@/components/ThemeToggle';

interface TopBarProps {
  onToggleSidebar: () => void;
  isSidebarCollapsed?: boolean;
  activeTitle?: string;
}

export function TopBar({
  onToggleSidebar,
  isSidebarCollapsed,
  activeTitle,
}: TopBarProps) {
  return (
    <header className="sticky top-0 z-30 h-14 bg-[var(--color-bg)]/80 backdrop-blur-md border-b border-[var(--color-border)] px-4 sm:px-6 flex items-center justify-between transition-colors">
      {/* Left side: sidebar toggle + breadcrumb */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          type="button"
          onClick={onToggleSidebar}
          className={`w-8 h-8 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] flex items-center justify-center text-[var(--color-text)] hover:bg-[var(--color-surface-hover)] transition-colors cursor-pointer ${
            isSidebarCollapsed ? 'flex' : 'flex md:hidden'
          }`}
          title={isSidebarCollapsed ? 'Expand sidebar' : 'Toggle sidebar'}
          aria-label={isSidebarCollapsed ? 'Expand sidebar' : 'Toggle sidebar'}
        >
          <PanelLeft className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-2 text-xs text-[var(--color-text-muted)] min-w-0">
          <Link
            href="/"
            className="hover:text-[var(--color-text)] transition-colors flex items-center gap-1"
          >
            <Home className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Home</span>
          </Link>
          <ChevronRight className="w-3 h-3 text-[var(--color-text-muted)]/50" />
          <span className="font-medium text-[var(--color-text)] truncate">
            {activeTitle || 'New Dubbing Job'}
          </span>
        </div>
      </div>

      {/* Right side: Pipeline mode indicator + ThemeToggle */}
      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[var(--color-accent-soft)] text-[var(--color-accent)] text-xs font-normal border border-[var(--color-accent)]/20">
          <Sparkles className="w-3 h-3" />
          <span>Local Engine Active</span>
        </div>
        <ThemeToggle />
      </div>
    </header>
  );
}
