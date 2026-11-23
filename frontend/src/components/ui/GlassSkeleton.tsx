import React from "react";
import { cn } from "@/lib/utils";

interface GlassSkeletonProps {
  className?: string;
}

export function GlassSkeleton({ className }: GlassSkeletonProps) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-xl bg-white/[0.05] border border-white/[0.04]",
        className
      )}
    />
  );
}

export function ProductCardSkeleton() {
  return (
    <div className="rounded-2xl border border-white/[0.06] bg-dark-850/50 p-4 space-y-3.5">
      <GlassSkeleton className="w-full h-48 rounded-xl" />
      <div className="space-y-2">
        <GlassSkeleton className="h-4 w-3/4" />
        <GlassSkeleton className="h-3 w-1/2" />
      </div>
      <div className="flex items-center justify-between pt-2 border-t border-white/[0.05]">
        <GlassSkeleton className="h-5 w-24" />
        <GlassSkeleton className="h-4 w-16 rounded-full" />
      </div>
    </div>
  );
}
