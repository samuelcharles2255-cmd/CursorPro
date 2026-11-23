import React from "react";
import { cn } from "@/lib/utils";

interface GlassBadgeProps {
  children: React.ReactNode;
  variant?: "default" | "gold" | "success" | "warning" | "indigo" | "outline" | "market" | "navy";
  size?: "sm" | "md";
  className?: string;
}

export function GlassBadge({
  children,
  variant = "default",
  size = "sm",
  className,
}: GlassBadgeProps) {
  const variants = {
    default: "bg-white/[0.06] text-zinc-300 border-white/[0.1]",
    gold: "bg-gold-500/[0.12] text-gold-300 border-gold-500/30",
    success: "bg-emerald-500/[0.12] text-emerald-300 border-emerald-500/30",
    warning: "bg-amber-500/[0.12] text-amber-300 border-amber-500/30",
    indigo: "bg-indigo-500/[0.12] text-indigo-300 border-indigo-500/30",
    outline: "bg-transparent text-zinc-300 border-white/[0.15]",
    market: "bg-market-500/[0.15] text-market-300 border-market-500/30",
    navy: "bg-navy-950/70 text-navy-200 border-navy-700/50",
  };

  const sizes = {
    sm: "text-[11px] px-2.5 py-0.5 rounded-full font-medium tracking-wide",
    md: "text-xs px-3 py-1 rounded-full font-medium tracking-wide",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 border backdrop-blur-md select-none",
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </span>
  );
}
