'use client';

import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'children'> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      children,
      className = '',
      disabled,
      ...props
    },
    ref
  ) => {
    // Size styles with consistent padding and typography
    const sizeStyles = {
      sm: 'px-3 py-1.5 text-xs rounded-lg gap-1.5 h-8',
      md: 'px-4 py-2 text-sm rounded-lg gap-2 h-10',
      lg: 'px-6 py-3 text-base rounded-lg gap-2.5 h-12',
    };

    // Variant styles matching design system strictly
    const variantStyles = {
      primary:
        'bg-gradient-to-t from-[#2685e6] to-[#3499FD] text-white shadow-sm shadow-[#3499fd]/20 hover:shadow-md hover:shadow-[#3499fd]/30 hover:from-[#2a8df2] hover:to-[#4ca7ff] border-0',
      secondary:
        'bg-[var(--color-surface)] hover:bg-[var(--color-surface-hover)] text-[var(--color-text)] border border-[var(--color-border)] hover:border-[var(--color-accent)]/60 shadow-2xs',
      ghost:
        'bg-transparent hover:bg-[var(--color-surface-hover)] text-[var(--color-text-muted)] hover:text-[var(--color-text)] border-0 shadow-none',
      danger:
        'bg-red-500/10 hover:bg-red-500/20 text-red-500 dark:text-red-400 border border-red-500/20',
    };

    return (
      <motion.button
        ref={ref}
        disabled={disabled || isLoading}
        whileHover={
          disabled || isLoading
            ? {}
            : {
                y: -1,
                transition: { duration: 0.15, ease: 'easeOut' },
              }
        }
        whileTap={
          disabled || isLoading
            ? {}
            : {
                y: 0,
                transition: { duration: 0.05 },
              }
        }
        className={`inline-flex items-center justify-center font-normal font-sans cursor-pointer transition-colors duration-200 select-none outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-bg)] disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="w-4 h-4 animate-spin text-current shrink-0" />
        ) : (
          leftIcon && <span className="inline-flex shrink-0 items-center">{leftIcon}</span>
        )}
        <span>{children}</span>
        {!isLoading && rightIcon && (
          <span className="inline-flex shrink-0 items-center">{rightIcon}</span>
        )}
      </motion.button>
    );
  }
);

Button.displayName = 'Button';
