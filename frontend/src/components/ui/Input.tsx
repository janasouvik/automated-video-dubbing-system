'use client';

import React from 'react';
import { AlertCircle } from 'lucide-react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, leftIcon, rightIcon, className = '', id, required, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full space-y-1.5 text-left">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-xs font-normal text-[var(--color-text-muted)] tracking-wide uppercase"
          >
            {label}
            {required && <span className="text-[var(--color-accent)] ml-1">*</span>}
          </label>
        )}
        <div className="relative flex items-center">
          {leftIcon && (
            <div className="absolute left-3.5 flex items-center pointer-events-none text-[var(--color-text-muted)]">
              {leftIcon}
            </div>
          )}
          <input
            id={inputId}
            ref={ref}
            required={required}
            className={`w-full h-11 px-3.5 text-sm rounded-lg bg-[var(--color-input-bg)] text-[var(--color-input-text)] border transition-all duration-200 placeholder:text-[#64748B] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed ${
              leftIcon ? 'pl-10' : ''
            } ${rightIcon || error ? 'pr-10' : ''} ${
              error
                ? 'border-red-500/60 focus:ring-red-500'
                : 'border-[var(--color-input-border)] hover:border-[var(--color-accent)]/50'
            } ${className}`}
            {...props}
          />
          {error ? (
            <div className="absolute right-3.5 flex items-center pointer-events-none text-red-500">
              <AlertCircle className="w-4 h-4" />
            </div>
          ) : (
            rightIcon && (
              <div className="absolute right-3.5 flex items-center pointer-events-none text-[var(--color-text-muted)]">
                {rightIcon}
              </div>
            )
          )}
        </div>
        {error ? (
          <p className="text-xs text-red-500 font-normal mt-1">{error}</p>
        ) : helperText ? (
          <p className="text-xs text-[var(--color-text-muted)] font-normal mt-1">{helperText}</p>
        ) : null}
      </div>
    );
  }
);

Input.displayName = 'Input';
