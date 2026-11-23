"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, ShoppingBag, Plus, Briefcase, User, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";

export function MobileBottomNav() {
  const pathname = usePathname();

  const isHome = pathname === "/";
  const isMarket = pathname.startsWith("/marketplace") && !pathname.includes("/create-listing");
  const isJobs = pathname.startsWith("/jobs");
  const isCreate = pathname.includes("/create-listing");
  const isProfile = pathname.startsWith("/profile") || pathname.startsWith("/auth");

  return (
    <nav
      aria-label="Mobile Bottom Navigation"
      className="fixed bottom-0 left-0 right-0 z-50 md:hidden bg-dark-950/95 backdrop-blur-2xl border-t border-white/[0.08] px-2 shadow-glass-elevated"
      style={{ paddingBottom: "max(env(safe-area-inset-bottom, 0px), 8px)" }}
    >
      <div className="flex items-center justify-around h-16 max-w-md mx-auto">
        {/* 1. Home */}
        <Link
          href="/"
          className={cn(
            "flex flex-col items-center justify-center min-w-[48px] min-h-[48px] px-2 rounded-xl text-[10px] font-medium transition-colors",
            isHome ? "text-white font-semibold" : "text-zinc-400 hover:text-zinc-200"
          )}
          aria-label="Home Overview"
        >
          <Home className={cn("w-5 h-5 mb-0.5", isHome && "text-white")} />
          <span>Home</span>
        </Link>

        {/* 2. Marketplace (Green Accent) */}
        <Link
          href="/marketplace"
          className={cn(
            "flex flex-col items-center justify-center min-w-[48px] min-h-[48px] px-2 rounded-xl text-[10px] font-medium transition-colors",
            isMarket ? "text-market-400 font-semibold" : "text-zinc-400 hover:text-zinc-200"
          )}
          aria-label="Marketplace"
        >
          <ShoppingBag className={cn("w-5 h-5 mb-0.5", isMarket && "text-market-400")} />
          <span>Market</span>
        </Link>

        {/* 3. Center Action Button: Plus / Create */}
        <Link
          href="/marketplace/create-listing"
          className="flex items-center justify-center -mt-5 min-w-[48px] min-h-[48px]"
          aria-label="Create New Listing or Post"
        >
          <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-market-600 via-market-500 to-emerald-400 text-dark-950 flex items-center justify-center shadow-green-glow active:scale-95 transition-transform border-2 border-dark-950">
            <Plus className="w-6 h-6 stroke-[2.5]" />
          </div>
        </Link>

        {/* 4. Jobs (Navy Accent) */}
        <Link
          href="/jobs"
          className={cn(
            "flex flex-col items-center justify-center min-w-[48px] min-h-[48px] px-2 rounded-xl text-[10px] font-medium transition-colors",
            isJobs ? "text-navy-400 font-semibold" : "text-zinc-400 hover:text-zinc-200"
          )}
          aria-label="Jobs"
        >
          <Briefcase className={cn("w-5 h-5 mb-0.5", isJobs && "text-navy-400")} />
          <span>Jobs</span>
        </Link>

        {/* 5. Profile */}
        <Link
          href="/profile"
          className={cn(
            "flex flex-col items-center justify-center min-w-[48px] min-h-[48px] px-2 rounded-xl text-[10px] font-medium transition-colors",
            isProfile ? "text-white font-semibold" : "text-zinc-400 hover:text-zinc-200"
          )}
          aria-label="User Profile and Settings"
        >
          <User className={cn("w-5 h-5 mb-0.5", isProfile && "text-white")} />
          <span>Profile</span>
        </Link>
      </div>
    </nav>
  );
}
