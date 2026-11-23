"use client";

import React, { forwardRef } from "react";
import { cn } from "@/lib/utils";

export interface GlassInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
  suffix?: React.ReactNode;
}

export const GlassInput = forwardRef<HTMLInputElement, GlassInputProps>(
  ({ className, type = "text", label, error, icon, suffix, ...props }, ref) => {
    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label className="block text-xs font-medium tracking-wide uppercase text-zinc-400">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {icon && (
            <div className="absolute left-3.5 text-zinc-400 pointer-events-none flex items-center">
              {icon}
            </div>
          )}
          <input
            type={type}
            className={cn(
              "w-full rounded-xl bg-dark-900/60 border border-white/[0.09] px-4 py-2.5 text-sm text-zinc-100 placeholder:text-zinc-500 backdrop-blur-md transition-all duration-200 focus:outline-none focus:border-gold-500/50 focus:ring-1 focus:ring-gold-500/30",
              icon && "pl-10",
              suffix && "pr-10",
              error && "border-rose-500/60 focus:border-rose-500",
              className
            )}
            ref={ref}
            {...props}
          />
          {suffix && (
            <div className="absolute right-3.5 text-zinc-400 flex items-center">
              {suffix}
            </div>
          )}
        </div>
        {error && <p className="text-xs text-rose-400 mt-1">{error}</p>}
      </div>
    );
  }
);

GlassInput.displayName = "GlassInput";
