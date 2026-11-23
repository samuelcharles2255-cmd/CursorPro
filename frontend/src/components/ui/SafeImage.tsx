"use client";

import React, { useState } from "react";
import { ImageOff, ShoppingBag, Building2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface SafeImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  fallbackType?: "product" | "company" | "generic";
  aspectRatio?: string; // e.g. "aspect-[4/3]" or "aspect-square"
  containerClassName?: string;
}

export function SafeImage({
  src,
  alt = "Image preview",
  fallbackType = "product",
  aspectRatio = "aspect-[4/3]",
  className,
  containerClassName,
  ...props
}: SafeImageProps) {
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const fallbackIcons = {
    product: ShoppingBag,
    company: Building2,
    generic: ImageOff,
  };

  const IconComponent = fallbackIcons[fallbackType] || ImageOff;

  return (
    <div
      className={cn(
        "relative w-full overflow-hidden bg-zinc-900/40 select-none",
        aspectRatio,
        containerClassName
      )}
    >
      {/* Loading Skeleton */}
      {isLoading && !hasError && (
        <div className="absolute inset-0 bg-zinc-800/40 animate-pulse" />
      )}

      {!hasError && src ? (
        <img
          src={src}
          alt={alt}
          onError={() => {
            setHasError(true);
            setIsLoading(false);
          }}
          onLoad={() => setIsLoading(false)}
          className={cn(
            "w-full h-full object-cover transition-opacity duration-300",
            isLoading ? "opacity-0" : "opacity-100",
            className
          )}
          {...props}
        />
      ) : (
        /* Graceful Neutral Surface with Centered Icon */
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-zinc-900/60 border border-white/[0.04] text-zinc-500 p-4">
          <IconComponent className="w-8 h-8 opacity-40 mb-1" />
          <span className="text-[11px] font-medium tracking-wide opacity-50 truncate max-w-[80%] text-center">
            {alt || "Preview unavailable"}
          </span>
        </div>
      )}
    </div>
  );
}
