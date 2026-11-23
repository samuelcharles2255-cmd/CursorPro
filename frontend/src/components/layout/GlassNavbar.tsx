"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShoppingBag,
  Briefcase,
  Layers,
  Search,
  MessageSquare,
  PlusCircle,
  Menu,
  X,
  User as UserIcon,
  ShieldCheck,
  ChevronDown,
  Bell,
  Sparkles,
} from "lucide-react";
import { useCart } from "@/lib/cart";
import { useAuth } from "@/lib/auth";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";

export function GlassNavbar() {
  const pathname = usePathname();
  const { itemCount } = useCart();
  const { user, isAuthenticated, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);

  const isMarketplace = pathname.startsWith("/marketplace");
  const isJobs = pathname.startsWith("/jobs");

  return (
    <header className="sticky top-0 z-40 w-full border-b border-white/[0.08] bg-dark-950/85 backdrop-blur-2xl transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          {/* Logo & Platform Name: The City */}
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-3 group">
              <div className="relative w-10 h-10 rounded-2xl bg-gradient-to-tr from-market-500 via-emerald-400 to-navy-500 p-[1.5px] shadow-green-glow/20 flex-shrink-0 transition-transform group-hover:scale-105">
                <div className="w-full h-full rounded-[14px] bg-dark-950 flex items-center justify-center">
                  <div className="flex items-center justify-center font-serif text-lg font-bold tracking-tighter leading-none select-none">
                    <span className="text-market-400 font-black">T</span>
                    <span className="text-white font-extrabold -ml-0.5">C</span>
                  </div>
                </div>
              </div>
              <div className="flex flex-col">
                <span className="text-base sm:text-lg font-serif font-bold tracking-tight text-white group-hover:text-market-300 transition-colors leading-none">
                  The City<span className="text-market-400">.</span>
                </span>
                <span className="text-[10px] text-zinc-400 font-medium tracking-wide mt-0.5">
                  Marketplace &amp; Jobs
                </span>
              </div>
            </Link>

            {/* Desktop Branch Nav with Distinct Accent Colors */}
            <nav
              aria-label="Branch Navigation"
              className="hidden md:flex items-center gap-1.5 p-1 rounded-2xl bg-dark-900/70 border border-white/[0.07] backdrop-blur-md"
            >
              <Link
                href="/"
                className={`min-h-[44px] px-3.5 rounded-xl text-xs font-semibold inline-flex items-center transition-all ${
                  pathname === "/"
                    ? "bg-white/[0.1] text-white shadow-sm border border-white/[0.1]"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]"
                }`}
              >
                Feed
              </Link>

              <Link
                href="/landing"
                className={`min-h-[44px] px-3.5 rounded-xl text-xs font-semibold inline-flex items-center gap-1.5 transition-all ${
                  pathname === "/landing"
                    ? "bg-white/[0.1] text-white shadow-sm border border-white/[0.1]"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]"
                }`}
              >
                <Sparkles className="w-3.5 h-3.5 text-market-400" />
                <span>Showcase</span>
              </Link>

              {/* Marketplace Branch: Vibrant Green Accent */}
              <Link
                href="/marketplace"
                className={`min-h-[44px] px-3.5 rounded-xl text-xs font-semibold inline-flex items-center gap-1.5 transition-all ${
                  isMarketplace
                    ? "bg-market-500/20 text-market-300 border border-market-500/40 shadow-green-glow"
                    : "text-zinc-400 hover:text-market-300 hover:bg-market-500/10"
                }`}
              >
                <ShoppingBag className="w-4 h-4 text-market-400" />
                <span>Marketplace</span>
                <span className="w-2 h-2 rounded-full bg-market-400 animate-pulse ml-0.5" />
              </Link>

              {/* Jobs Branch: Navy / Dark Blue Accent */}
              <Link
                href="/jobs"
                className={`min-h-[44px] px-3.5 rounded-xl text-xs font-semibold inline-flex items-center gap-1.5 transition-all ${
                  isJobs
                    ? "bg-navy-600/30 text-navy-200 border border-navy-500/50 shadow-navy-glow"
                    : "text-zinc-400 hover:text-navy-300 hover:bg-navy-900/30"
                }`}
              >
                <Briefcase className="w-4 h-4 text-navy-400" />
                <span>Jobs</span>
                <span className="px-1.5 py-0.5 rounded-full bg-navy-500/20 text-[10px] text-navy-300 font-mono">
                  770+
                </span>
              </Link>
            </nav>
          </div>

          {/* Right Action Icons & Auth */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Quick Search */}
            <Link
              href={isJobs ? "/jobs" : "/marketplace/search"}
              className="min-h-[44px] min-w-[44px] px-3 rounded-xl text-zinc-400 hover:text-zinc-100 hover:bg-white/[0.06] border border-transparent hover:border-white/[0.08] transition-all hidden sm:inline-flex items-center gap-2 text-xs"
              title="Search"
              aria-label="Search items or positions"
            >
              <Search className="w-4 h-4 text-zinc-400" />
              <span className="text-zinc-500">Search...</span>
            </Link>

            {/* Notification Bell matching reference image */}
            <button
              className="relative min-h-[44px] min-w-[44px] p-2.5 rounded-xl text-zinc-300 hover:text-white hover:bg-white/[0.06] border border-white/[0.06] transition-all flex items-center justify-center"
              title="Notifications"
              aria-label="View notifications"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-2.5 right-2.5 w-2 h-2 rounded-full bg-cyan-400 ring-2 ring-dark-950 animate-pulse" />
            </button>

            {/* In-App Messages */}
            <Link
              href="/marketplace/messages"
              className="relative min-h-[44px] min-w-[44px] p-2.5 rounded-xl text-zinc-300 hover:text-white hover:bg-white/[0.06] border border-white/[0.06] transition-all flex items-center justify-center"
              title="Messages"
              aria-label="Messages"
            >
              <MessageSquare className="w-4 h-4" />
            </Link>

            {/* Shopping Cart Pill */}
            <Link
              href="/marketplace/cart"
              className="relative min-h-[44px] min-w-[44px] p-2.5 rounded-xl text-zinc-300 hover:text-white hover:bg-white/[0.06] border border-white/[0.06] transition-all flex items-center justify-center"
              title="View Cart"
              aria-label="View Cart"
            >
              <ShoppingBag className="w-4 h-4" />
              {itemCount > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-market-500 text-dark-950 font-bold text-[11px] flex items-center justify-center shadow-green-glow">
                  {itemCount}
                </span>
              )}
            </Link>

            {/* Post Listing CTA (Seller) */}
            <Link href="/marketplace/create-listing" className="hidden lg:block">
              <button className="min-h-[44px] px-4 py-2 rounded-xl bg-market-600 hover:bg-market-500 text-white font-semibold text-xs inline-flex items-center gap-1.5 shadow-green-glow transition-all active:scale-98">
                <PlusCircle className="w-4 h-4" />
                Post Item
              </button>
            </Link>

            {/* User Profile / Auth Avatar Pill matching reference image */}
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                  className="min-h-[44px] flex items-center gap-2 p-1.5 pr-2.5 rounded-2xl bg-dark-900/80 border border-white/[0.09] hover:border-white/[0.2] transition-all text-xs"
                  aria-expanded={userDropdownOpen}
                  aria-label="User account menu"
                >
                  <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-market-500 flex items-center justify-center text-dark-950 font-bold overflow-hidden">
                    <img
                      src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80"
                      alt="User avatar"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <span className="hidden lg:block text-zinc-200 font-semibold max-w-[120px] truncate">
                    {user?.name || user?.username}
                  </span>
                  <ChevronDown className="w-3.5 h-3.5 text-zinc-400" />
                </button>

                <AnimatePresence>
                  {userDropdownOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      className="absolute right-0 mt-2 w-56 rounded-2xl bg-dark-850/95 border border-white/[0.1] p-2 shadow-glass-elevated backdrop-blur-2xl z-50 text-xs"
                    >
                      <div className="px-3 py-2 border-b border-white/[0.06] mb-1">
                        <p className="font-semibold text-white truncate">{user?.name || user?.username}</p>
                        <p className="text-zinc-500 truncate text-[11px]">{user?.email}</p>
                      </div>
                      <Link
                        href="/marketplace/seller/dashboard"
                        onClick={() => setUserDropdownOpen(false)}
                        className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-zinc-300 hover:text-market-300 hover:bg-market-500/10 transition-colors"
                      >
                        <Layers className="w-4 h-4 text-market-400" />
                        Seller Dashboard
                      </Link>
                      <Link
                        href="/jobs/applications"
                        onClick={() => setUserDropdownOpen(false)}
                        className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-zinc-300 hover:text-navy-300 hover:bg-navy-900/30 transition-colors"
                      >
                        <Briefcase className="w-4 h-4 text-navy-400" />
                        Job Applications
                      </Link>
                      <Link
                        href="/marketplace/moderation"
                        onClick={() => setUserDropdownOpen(false)}
                        className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-zinc-300 hover:text-white hover:bg-white/[0.06] transition-colors"
                      >
                        <ShieldCheck className="w-4 h-4 text-emerald-400" />
                        Moderation Desk
                      </Link>
                      <Link
                        href="/profile"
                        onClick={() => setUserDropdownOpen(false)}
                        className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-zinc-300 hover:text-white hover:bg-white/[0.06] transition-colors"
                      >
                        <UserIcon className="w-4 h-4" />
                        Profile Settings
                      </Link>
                      <div className="border-t border-white/[0.06] mt-1 pt-1">
                        <button
                          onClick={() => {
                            logout();
                            setUserDropdownOpen(false);
                          }}
                          className="w-full text-left px-3 py-2 rounded-lg text-rose-400 hover:bg-rose-500/10 transition-colors"
                        >
                          Sign out
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link href="/auth/login">
                  <GlassButton variant="ghost" size="sm" className="min-h-[44px]">
                    Sign in
                  </GlassButton>
                </Link>
                <Link href="/auth/register" className="hidden sm:block">
                  <GlassButton variant="gold" size="sm" className="min-h-[44px]">
                    Join
                  </GlassButton>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
