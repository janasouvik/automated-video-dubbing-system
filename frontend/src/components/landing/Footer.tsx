'use client';

import React from 'react';
import Link from 'next/link';
import { Video } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t border-[var(--color-border)] bg-[var(--color-surface)] py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Logo + Copyright */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#2685e6] to-[#3499FD] flex items-center justify-center text-white">
              <Video className="w-4 h-4" />
            </div>
            <div>
              <span className="text-sm font-medium text-[var(--color-text)]">
                VanniDub AI
              </span>
              <p className="text-xs text-[var(--color-text-muted)]">
                © {new Date().getFullYear()} VanniDub AI. Automated Video Dubbing Pipeline.
              </p>
            </div>
          </div>

          {/* Links */}
          <div className="flex items-center gap-6 text-xs text-[var(--color-text-muted)]">
            <a
              href="#hero"
              className="hover:text-[var(--color-text)] transition-colors"
            >
              Home
            </a>
            <a
              href="#how-it-works"
              className="hover:text-[var(--color-text)] transition-colors"
            >
              Pipeline
            </a>
            <a
              href="#features"
              className="hover:text-[var(--color-text)] transition-colors"
            >
              Features
            </a>
            <a
              href="#overview"
              className="hover:text-[var(--color-text)] transition-colors"
            >
              Overview
            </a>
            <Link
              href="/dashboard"
              className="hover:text-[var(--color-text)] transition-colors font-medium text-[var(--color-accent)]"
            >
              Dashboard
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
