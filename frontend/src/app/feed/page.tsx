"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ShoppingBag,
  Briefcase,
  Newspaper,
  Search,
  Sparkles,
  ChevronRight,
  TrendingUp,
  MapPin,
  CheckCircle2,
  Phone,
  Flame,
  Radio,
  Clock,
  ArrowUpRight,
} from "lucide-react";
import { fetchListings, fetchCategories, fetchJobs, FALLBACK_LISTINGS } from "@/lib/api";
import { Listing, Job, Category } from "@/types";
import { SafeImage } from "@/components/ui/SafeImage";
import { ProductCard } from "@/components/features/marketplace/ProductCard";
import { JobCard } from "@/components/features/jobs/JobCard";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { formatTZS } from "@/lib/utils";

// Top Creators / Merchants matching reference image
const TOP_CREATORS = [
  {
    id: 1,
    name: "Hak Muchoi",
    handle: "@hakmuchoi",
    category: "Lifestyle",
    isLive: true,
    metric: "200K followers",
    image: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80",
    role: "Verified Merchant",
  },
  {
    id: 2,
    name: "Tiffea Manyo",
    handle: "@tiffea",
    category: "Fashion",
    isLive: false,
    metric: "91K followers",
    image: "https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=400&q=80",
    role: "Horology Specialist",
  },
  {
    id: 3,
    name: "Jich Ahlalupa",
    handle: "@jich_tech",
    category: "Tech",
    isLive: false,
    metric: "1.2M views",
    image: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80",
    role: "Hardware Curator",
  },
  {
    id: 4,
    name: "Lumina Studio",
    handle: "@lumina_tz",
    category: "Electronics",
    isLive: true,
    metric: "450K trade",
    image: "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80",
    role: "Pro Merchant",
  },
];

// News & Tech editorial feed matching reference image
const NEWS_ITEMS = [
  {
    id: 1,
    title: "SheaTrees: Sustainable Agrotech Scaling across Mbeya",
    tag: "Nature & Tech",
    time: "10:39 AM",
    image: "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=400&q=80",
    readTime: "4 min read",
  },
  {
    id: 2,
    title: "This Feed: Machine Intelligence Reshaping East Africa Banking",
    tag: "Future of Work",
    time: "08:14 AM",
    image: "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=400&q=80",
    readTime: "6 min read",
  },
  {
    id: 3,
    title: "Mkk Malawi: Cross-Border Digital Escrow Standard Established",
    tag: "Fintech",
    time: "15:22 PM",
    image: "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=400&q=80",
    readTime: "3 min read",
  },
];

export default function BaseHomePage() {
  const [activeChip, setActiveChip] = useState<string>("all");
  const [listings, setListings] = useState<Listing[]>(FALLBACK_LISTINGS);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [lstData, jobData] = await Promise.all([
          fetchListings({ page_size: 6 }),
          fetchJobs({ page_size: 6 }),
        ]);
        if (lstData.results.length > 0) setListings(lstData.results);
        if (jobData.length > 0) setJobs(jobData);
      } catch (err) {
        console.warn("Home load fallback:", err);
      }
    }
    load();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    if (activeChip === "jobs") {
      window.location.href = `/jobs?search=${encodeURIComponent(searchQuery)}`;
    } else {
      window.location.href = `/marketplace/search?search=${encodeURIComponent(searchQuery)}`;
    }
  };

  return (
    <div className="min-h-screen bg-dark-950 text-zinc-100 pb-20">
      {/* Container matching mobile / desktop discovery layout */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 pt-4 sm:pt-6 space-y-6 sm:space-y-8">
        {/* ========================================================= */}
        {/* 1. HORIZONTAL CATEGORY PILLS (MATCHING REFERENCE IMAGE)   */}
        {/* ========================================================= */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar pt-1">
          {[
            { id: "all", label: "All Feed", accent: "default" },
            { id: "news", label: "News & Tech", accent: "default" },
            { id: "jobs", label: "Jobs", accent: "jobs" },
            { id: "market", label: "Marketplace (Biashara)", accent: "market" },
            { id: "trending", label: "Trending & Updates", accent: "default" },
          ].map((chip) => {
            const isSelected = activeChip === chip.id;
            const accentClass =
              chip.accent === "market" && isSelected
                ? "bg-market-500 text-dark-950 font-bold shadow-green-glow"
                : chip.accent === "jobs" && isSelected
                ? "bg-navy-600 text-white font-bold shadow-navy-glow"
                : isSelected
                ? "bg-white text-dark-950 font-bold"
                : "bg-dark-850/80 hover:bg-dark-800 text-zinc-400 hover:text-zinc-200 border border-white/[0.08]";

            return (
              <button
                key={chip.id}
                onClick={() => setActiveChip(chip.id)}
                className={`min-h-[44px] px-5 py-2.5 rounded-full text-xs whitespace-nowrap transition-all duration-200 select-none ${accentClass}`}
              >
                {chip.label}
              </button>
            );
          })}
        </div>

        {/* Promotional Showcase Callout */}
        <div className="flex items-center justify-between p-3.5 sm:p-4 rounded-2xl bg-gradient-to-r from-market-950/70 via-dark-900 to-navy-950/70 border border-white/[0.08] backdrop-blur-xl gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <span className="w-8 h-8 rounded-xl bg-market-500/20 text-market-400 flex items-center justify-center font-bold text-xs flex-shrink-0">
              <Sparkles className="w-4 h-4" />
            </span>
            <div className="min-w-0">
              <p className="text-xs font-bold text-white truncate">
                New to The City? Explore the Platform Showcase
              </p>
              <p className="text-[11px] text-zinc-400 truncate">
                See how 100% Escrow Protection and 770+ verified jobs work together.
              </p>
            </div>
          </div>
          <Link
            href="/landing"
            className="flex-shrink-0 min-h-[36px] px-3.5 py-1.5 rounded-xl bg-white/[0.08] hover:bg-white/[0.15] text-xs font-semibold text-white inline-flex items-center gap-1.5 border border-white/[0.1] transition-all"
          >
            <span>Tour Platform</span>
            <ArrowUpRight className="w-3.5 h-3.5 text-market-400" />
          </Link>
        </div>

        {/* Quick Search Input */}
        <form onSubmit={handleSearch} className="relative">
          <Search className="w-4 h-4 text-zinc-400 absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search across marketplace, jobs, and market intelligence..."
            className="w-full min-h-[48px] bg-dark-900/90 border border-white/[0.09] rounded-2xl pl-11 pr-24 py-2.5 text-xs text-white placeholder:text-zinc-500 focus:outline-none focus:border-cyan-500/50 transition-colors"
          />
          <button
            type="submit"
            className="absolute right-2 top-1/2 -translate-y-1/2 min-h-[36px] px-3.5 rounded-xl bg-white/[0.08] hover:bg-white/[0.15] text-xs font-semibold text-white transition-colors"
          >
            Explore
          </button>
        </form>

        {/* ========================================================= */}
        {/* 2. HERO BANNER CARD (EXACTLY MATCHING REFERENCE IMAGE)    */}
        {/* ========================================================= */}
        <div className="relative rounded-3xl overflow-hidden border border-white/[0.1] bg-dark-900 shadow-glass-elevated">
          {/* Main 3D / AI Feature Artwork */}
          <div className="relative aspect-[16/9] sm:aspect-[21/9] w-full overflow-hidden bg-gradient-to-r from-cyan-950 via-dark-900 to-indigo-950">
            <SafeImage
              src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80"
              alt="AI and The Future of Work in East Africa"
              aspectRatio="aspect-full"
              className="w-full h-full object-cover mix-blend-screen opacity-70"
            />

            {/* Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-dark-950 via-dark-950/40 to-transparent" />

            {/* Badges & Headline at the bottom */}
            <div className="absolute bottom-5 left-5 right-5 sm:bottom-8 sm:left-8 space-y-2.5 z-10">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 text-[11px] font-bold uppercase tracking-wider backdrop-blur-md">
                  <Flame className="w-3.5 h-3.5 fill-rose-400" />
                  TRENDING
                </span>
                <span className="px-3 py-1 rounded-full bg-black/60 text-zinc-300 text-[11px] font-mono backdrop-blur-md">
                  2.1M views
                </span>
              </div>

              <h2 className="text-2xl sm:text-4xl font-sans font-bold text-white tracking-tight leading-tight">
                AI &amp; The Future of Work in Tanzania
              </h2>
              <p className="text-xs sm:text-sm text-zinc-300 max-w-xl line-clamp-2">
                How distributed commerce, verified peer-to-peer trade, and executive tech roles are converging.
              </p>
            </div>
          </div>
        </div>

        {/* ========================================================= */}
        {/* 3. SECTION: TOP CREATORS (MATCHING REFERENCE IMAGE)       */}
        {/* ========================================================= */}
        <section className="space-y-3.5">
          <div className="flex items-center justify-between">
            <h3 className="text-base sm:text-lg font-bold text-white tracking-tight font-sans">
              Top Creators &amp; Verified Sellers
            </h3>
            <Link
              href="/marketplace/search"
              className="min-h-[44px] inline-flex items-center gap-1 text-xs text-zinc-400 hover:text-white font-medium"
            >
              See all <ChevronRight className="w-3.5 h-3.5 text-zinc-500" />
            </Link>
          </div>

          {/* Horizontal Creator Cards matching reference photo */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
            {TOP_CREATORS.map((c) => (
              <div
                key={c.id}
                className="group relative rounded-2xl bg-dark-850/80 border border-white/[0.08] hover:border-cyan-500/40 p-3 sm:p-4 flex flex-col justify-between overflow-hidden shadow-glass hover:shadow-cyan-500/10 transition-all"
              >
                {/* Image Container with Badges */}
                <div className="relative aspect-[3/4] w-full rounded-xl overflow-hidden bg-dark-900 mb-3">
                  <SafeImage
                    src={c.image}
                    alt={c.name}
                    aspectRatio="aspect-[3/4]"
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-dark-950/80 via-transparent to-black/20" />

                  {/* LIVE / Category badges at the top */}
                  <div className="absolute top-2 left-2 flex items-center gap-1">
                    {c.isLive && (
                      <span className="px-2 py-0.5 rounded-full bg-amber-500/90 text-dark-950 text-[10px] font-bold flex items-center gap-1">
                        <Radio className="w-2.5 h-2.5 animate-pulse" /> LIVE
                      </span>
                    )}
                    <span className="px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 text-[10px] font-semibold border border-cyan-500/30 backdrop-blur-md">
                      {c.category}
                    </span>
                  </div>
                </div>

                {/* Creator Details */}
                <div className="space-y-0.5">
                  <p className="text-xs sm:text-sm font-bold text-white truncate">{c.name}</p>
                  <p className="text-[11px] text-zinc-400 font-mono">{c.metric}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ========================================================= */}
        {/* 4. SECTION: NEWS & TECH (MATCHING REFERENCE IMAGE)        */}
        {/* ========================================================= */}
        <section className="space-y-3.5">
          <div className="flex items-center justify-between">
            <h3 className="text-base sm:text-lg font-bold text-white tracking-tight font-sans">
              News &amp; Tech
            </h3>
            <Link
              href="/"
              className="min-h-[44px] inline-flex items-center gap-1 text-xs text-zinc-400 hover:text-white font-medium"
            >
              See all <ChevronRight className="w-3.5 h-3.5 text-zinc-500" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
            {NEWS_ITEMS.map((item) => (
              <div
                key={item.id}
                className="group rounded-2xl bg-dark-850/70 border border-white/[0.08] hover:border-white/[0.18] p-3 sm:p-4 flex flex-col justify-between overflow-hidden transition-all shadow-glass"
              >
                <div className="relative aspect-[16/10] w-full rounded-xl overflow-hidden bg-dark-900 mb-3">
                  <SafeImage
                    src={item.image}
                    alt={item.title}
                    aspectRatio="aspect-[16/10]"
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-2 left-2">
                    <span className="px-2 py-0.5 rounded-full bg-black/60 text-cyan-300 text-[10px] font-semibold backdrop-blur-md border border-white/[0.1]">
                      {item.tag}
                    </span>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <p className="text-xs sm:text-sm font-semibold text-white group-hover:text-cyan-300 transition-colors line-clamp-2">
                    {item.title}
                  </p>
                  <div className="flex items-center justify-between text-[11px] text-zinc-500 pt-1">
                    <span>{item.time}</span>
                    <span>{item.readTime}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ========================================================= */}
        {/* 5. SECTION: MARKETPLACE (VIBRANT GREEN ACCENT)            */}
        {/* ========================================================= */}
        <section className="space-y-4 pt-4 border-t border-white/[0.06]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-market-500 shadow-green-glow" />
              <h3 className="text-base sm:text-lg font-bold text-white tracking-tight font-sans">
                Marketplace · Verified Peer-to-Peer Trade
              </h3>
            </div>
            <Link
              href="/marketplace"
              className="min-h-[44px] inline-flex items-center gap-1 text-xs text-market-400 hover:text-market-300 font-semibold"
            >
              Enter Market <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Clean P2P Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {listings.slice(0, 3).map((item) => (
              <ProductCard key={item.id} listing={item} />
            ))}
          </div>
        </section>

        {/* ========================================================= */}
        {/* 6. SECTION: JOBS (NAVY / DARK BLUE ACCENT)               */}
        {/* ========================================================= */}
        <section className="space-y-4 pt-4 border-t border-white/[0.06]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-navy-500 shadow-navy-glow" />
              <h3 className="text-base sm:text-lg font-bold text-white tracking-tight font-sans">
                Jobs · 770+ Verified Corporate Positions
              </h3>
            </div>
            <Link
              href="/jobs"
              className="min-h-[44px] inline-flex items-center gap-1 text-xs text-navy-400 hover:text-navy-300 font-semibold"
            >
              View All Jobs <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Jobs Cards in Navy styling */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {jobs.slice(0, 3).map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
