'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Video, ArrowLeft } from 'lucide-react';
import { ThemeToggle } from '@/components/ThemeToggle';
import { scaleIn } from '@/lib/motion';

interface AuthLayoutProps {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}

export function AuthLayout({ title, subtitle, children }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col justify-between bg-transparent px-4 py-8 relative overflow-hidden">
      {/* Background Accent (Light Mode only) */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] bg-[var(--color-accent)]/10 blur-[100px] rounded-full pointer-events-none -z-10 dark:hidden" />

      {/* Top Bar */}
      <div className="max-w-6xl w-full mx-auto flex items-center justify-between">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </Link>
        <ThemeToggle />
      </div>

      {/* Centered Auth Card */}
      <div className="w-full max-w-md mx-auto my-8">
        <motion.div
          variants={scaleIn}
          initial="hidden"
          animate="visible"
          className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 shadow-xl shadow-black/5"
        >
          {/* Logo & Header */}
          <div className="text-center mb-8">
            <Link
              href="/"
              className="inline-flex items-center gap-2.5 mb-4 group"
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#2685e6] to-[#3499FD] flex items-center justify-center text-white shadow-sm shadow-[#3499fd]/30">
                <Video className="w-5 h-5 stroke-[2]" />
              </div>
            </Link>
            <h1 className="text-2xl font-medium text-[var(--color-text)] tracking-tight">
              {title}
            </h1>
            <p className="text-sm text-[var(--color-text-muted)] mt-1.5 font-normal">
              {subtitle}
            </p>
          </div>

          {children}
        </motion.div>
      </div>

      {/* Bottom Footer */}
      <div className="text-center text-xs text-[var(--color-text-muted)]">
        <span>© {new Date().getFullYear()} VanniDub AI • All rights reserved</span>
      </div>
    </div>
  );
}
