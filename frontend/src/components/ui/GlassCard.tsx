"use client";

import React from "react";
import { motion, HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";

interface GlassCardProps extends HTMLMotionProps<"div"> {
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "gold" | "elevated" | "flat" | "interactive";
  glow?: boolean;
}

export function GlassCard({
  children,
  className,
  variant = "default",
  glow = false,
  ...props
}: GlassCardProps) {
  const variantStyles = {
    default:
      "bg-dark-850/70 border border-white/[0.08] backdrop-blur-xl shadow-glass",
    gold: "bg-dark-850/80 border border-gold-500/25 backdrop-blur-xl shadow-gold-glow/20",
    elevated:
      "bg-dark-800/80 border border-white/[0.12] backdrop-blur-2xl shadow-glass-elevated",
    flat: "bg-dark-900/50 border border-white/[0.05] backdrop-blur-md",
    interactive:
      "bg-dark-850/70 border border-white/[0.08] backdrop-blur-xl hover:border-gold-500/30 hover:bg-dark-800/80 transition-all duration-300 shadow-glass cursor-pointer",
  };

  return (
    <motion.div
      className={cn(
        "relative rounded-2xl overflow-hidden p-6 text-zinc-100",
        variantStyles[variant],
        glow && "before:absolute before:inset-0 before:bg-gradient-to-b before:from-gold-500/[0.04] before:to-transparent before:pointer-events-none",
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
}
