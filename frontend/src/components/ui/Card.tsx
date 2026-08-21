'use client';

import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

export interface CardProps extends HTMLMotionProps<'div'> {
  hoverEffect?: boolean;
  className?: string;
  children?: React.ReactNode;
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ hoverEffect = false, className = '', children, ...props }, ref) => {
    return (
      <motion.div
        ref={ref}
        whileHover={
          hoverEffect
            ? {
                y: -4,
                rotate: [0, -1.2, 1.2, -0.8, 0.8, 0],
                transition: { duration: 0.35, ease: 'easeInOut' },
              }
            : undefined
        }
        className={`bg-[var(--color-surface)] border border-[var(--color-border)] rounded-2xl p-6 transition-all duration-200 cursor-pointer ${
          hoverEffect
            ? 'hover-shake-card hover:border-[var(--color-accent)]/80 hover:shadow-xl hover:shadow-[var(--color-accent)]/10'
            : ''
        } ${className}`}
        {...props}
      >
        {children}
      </motion.div>
    );
  }
);

Card.displayName = 'Card';
