"use client";

import React from "react";
import { motion, HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";

interface GlassButtonProps extends HTMLMotionProps<"button"> {
  children: React.ReactNode;
  className?: string;
  variant?: "gold" | "secondary" | "outline" | "ghost" | "danger" | "market" | "navy";
  size?: "sm" | "md" | "lg" | "icon";
  isLoading?: boolean;
}

export function GlassButton({
  children,
  className,
  variant = "gold",
  size = "md",
  isLoading = false,
  disabled,
  ...props
}: GlassButtonProps) {
  const base =
    "relative inline-flex items-center justify-center font-medium rounded-xl transition-all duration-200 select-none disabled:opacity-50 disabled:pointer-events-none active:scale-[0.98]";

  const sizes = {
    sm: "text-xs px-3.5 py-1.5 gap-1.5",
    md: "text-sm px-5 py-2.5 gap-2",
    lg: "text-base px-6 py-3.5 gap-2.5",
    icon: "p-2.5",
  };

  const variants = {
    gold: "bg-gradient-to-r from-gold-500 via-gold-400 to-gold-500 text-dark-950 font-semibold shadow-gold-glow/40 hover:shadow-gold-glow hover:brightness-105 border border-gold-300/40",
    secondary:
      "bg-white/[0.06] hover:bg-white/[0.1] text-zinc-100 border border-white/[0.12] backdrop-blur-md shadow-glass-sm",
    outline:
      "bg-transparent hover:bg-gold-500/[0.08] text-gold-400 border border-gold-500/40 hover:border-gold-400 transition-colors",
    ghost: "bg-transparent hover:bg-white/[0.06] text-zinc-300 hover:text-white",
    danger:
      "bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30",
    market:
      "bg-gradient-to-r from-market-600 via-market-500 to-market-600 text-dark-950 font-bold shadow-green-glow hover:shadow-green-glow hover:brightness-105 border border-market-400/50",
    navy:
      "bg-gradient-to-r from-navy-800 via-navy-600 to-navy-700 text-white font-semibold shadow-navy-glow hover:shadow-navy-glow hover:brightness-110 border border-navy-400/40",
  };

  return (
    <motion.button
      whileTap={{ scale: disabled || isLoading ? 1 : 0.98 }}
      className={cn(base, sizes[size], variants[variant], className)}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="flex items-center gap-2">
          <svg
            className="animate-spin h-4 w-4 text-current"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8v8H4z"
            />
          </svg>
          <span>Processing...</span>
        </span>
      ) : (
        children
      )}
    </motion.button>
  );
}
