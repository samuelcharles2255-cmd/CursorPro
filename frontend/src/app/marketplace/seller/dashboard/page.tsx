"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  TrendingUp,
  ShoppingBag,
  Eye,
  MessageSquare,
  DollarSign,
  PlusCircle,
  MoreVertical,
  CheckCircle2,
  Clock,
  ArrowUpRight,
  ShieldCheck,
  AlertCircle,
  RefreshCw,
  Trash2,
  Edit3,
} from "lucide-react";
import { fetchListings, FALLBACK_LISTINGS } from "@/lib/api";
import { Listing } from "@/types";
import { formatTZS, formatCondition, formatDate } from "@/lib/utils";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassCard } from "@/components/ui/GlassCard";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassSidebar } from "@/components/layout/GlassSidebar";

export default function SellerDashboardPage() {
  const [listings, setListings] = useState<Listing[]>(FALLBACK_LISTINGS);
  const [timeframe, setTimeframe] = useState<"7d" | "30d" | "90d">("30d");
  const [notification, setNotification] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      const res = await fetchListings({ my_listings: "true" });
      if (res.results.length > 0) setListings(res.results);
    }
    load();
  }, []);

  const handleMarkSold = (id: number) => {
    setListings(
      listings.map((item) => (item.id === id ? { ...item, status: "SOLD" } : item))
    );
    setNotification("Listing marked as SOLD and moved to completed inventory.");
    setTimeout(() => setNotification(null), 3000);
  };

  const handleRenew = (id: number) => {
    setNotification("Listing renewed for 30 active days in Kariakoo & Dar es Salaam feeds.");
    setTimeout(() => setNotification(null), 3000);
  };

  const handleDelete = (id: number) => {
    setListings(listings.filter((item) => item.id !== id));
    setNotification("Listing removed from active showroom.");
    setTimeout(() => setNotification(null), 3000);
  };

  const totalValue = listings.reduce((sum, item) => sum + Number(item.price), 0);
  const totalViews = listings.reduce((sum, item) => sum + (item.views_count || 120), 0);

  return (
    <div className="flex-1 flex max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 gap-8">
      <GlassSidebar />

      <main className="flex-1 space-y-8 min-w-0">
        {/* Toast */}
        {notification && (
          <div className="fixed top-20 right-6 z-50 p-4 rounded-xl bg-market-500 text-dark-950 font-bold shadow-green-glow flex items-center gap-2 text-xs">
            <CheckCircle2 className="w-4 h-4" />
            <span>{notification}</span>
          </div>
        )}

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-3 py-1 rounded-full bg-market-500/15 border border-market-500/30 text-market-300 text-xs font-semibold">
                Merchant Command Center
              </span>
              <span className="text-xs text-zinc-500">Live Analytics</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-serif font-medium text-white">
              Seller Performance &amp; Inventory
            </h1>
            <p className="text-xs sm:text-sm text-zinc-400">
              Track catalog views, active client inquiries, and transaction escrow payouts.
            </p>
          </div>

          <Link href="/marketplace/create-listing">
            <button className="min-h-[44px] px-5 rounded-2xl bg-market-600 hover:bg-market-500 text-dark-950 font-bold text-xs inline-flex items-center gap-2 shadow-green-glow transition-all active:scale-98">
              <PlusCircle className="w-4 h-4" />
              Create New Listing
            </button>
          </Link>
        </div>

        {/* 4 Glass Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <GlassCard variant="default" className="p-5 space-y-2">
            <div className="flex items-center justify-between text-zinc-400 text-xs">
              <span>Catalog Value</span>
              <DollarSign className="w-4 h-4 text-gold-400" />
            </div>
            <p className="text-2xl font-bold font-sans text-white">
              {formatTZS(totalValue)}
            </p>
            <p className="text-[11px] text-emerald-400 flex items-center gap-1">
              <TrendingUp className="w-3 h-3" /> +14.8% inventory value this month
            </p>
          </GlassCard>

          <GlassCard variant="default" className="p-5 space-y-2">
            <div className="flex items-center justify-between text-zinc-400 text-xs">
              <span>Active Items</span>
              <ShoppingBag className="w-4 h-4 text-indigo-400" />
            </div>
            <p className="text-2xl font-bold font-sans text-white">
              {listings.length}
            </p>
            <p className="text-[11px] text-zinc-400">
              {listings.filter((i) => i.status === "ACTIVE").length} active in public feeds
            </p>
          </GlassCard>

          <GlassCard variant="default" className="p-5 space-y-2">
            <div className="flex items-center justify-between text-zinc-400 text-xs">
              <span>Showroom Impressions</span>
              <Eye className="w-4 h-4 text-emerald-400" />
            </div>
            <p className="text-2xl font-bold font-sans text-white">
              {totalViews.toLocaleString()}
            </p>
            <p className="text-[11px] text-emerald-400 flex items-center gap-1">
              <TrendingUp className="w-3 h-3" /> +24% buyer discovery rate
            </p>
          </GlassCard>

          <GlassCard variant="default" className="p-5 space-y-2">
            <div className="flex items-center justify-between text-zinc-400 text-xs">
              <span>Active Inquiries</span>
              <MessageSquare className="w-4 h-4 text-gold-400" />
            </div>
            <p className="text-2xl font-bold font-sans text-white">
              18
            </p>
            <p className="text-[11px] text-gold-300">
              Avg response time: 12 minutes
            </p>
          </GlassCard>
        </div>

        {/* Analytics Chart & Engagement Section */}
        <div className="p-6 sm:p-8 rounded-3xl bg-dark-850/70 border border-white/[0.08] backdrop-blur-xl space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold text-white">Buyer Engagement & Traffic</h2>
              <p className="text-xs text-zinc-400">Daily buyer visits and click-through inquiries</p>
            </div>
            <div className="flex items-center gap-1 bg-dark-900/80 p-1 rounded-xl border border-white/[0.06] text-xs">
              {(["7d", "30d", "90d"] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setTimeframe(t)}
                  className={`px-3 py-1 rounded-lg uppercase text-[10px] font-semibold transition-all ${
                    timeframe === t
                      ? "bg-market-500 text-dark-950 font-bold shadow-green-glow"
                      : "text-zinc-400 hover:text-white"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* SVG Clean Luxury Area Chart */}
          <div className="w-full h-48 sm:h-56 relative pt-4">
            <svg className="w-full h-full overflow-visible" viewBox="0 0 800 200" preserveAspectRatio="none">
              <defs>
                <linearGradient id="marketGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity="0.35" />
                  <stop offset="100%" stopColor="#10b981" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              {/* Grid Lines */}
              <line x1="0" y1="40" x2="800" y2="40" stroke="rgba(255,255,255,0.05)" strokeDasharray="4 4" />
              <line x1="0" y1="100" x2="800" y2="100" stroke="rgba(255,255,255,0.05)" strokeDasharray="4 4" />
              <line x1="0" y1="160" x2="800" y2="160" stroke="rgba(255,255,255,0.05)" strokeDasharray="4 4" />

              {/* Area path */}
              <path
                d="M 0 170 Q 150 140 280 90 T 520 60 T 800 30 L 800 200 L 0 200 Z"
                fill="url(#marketGradient)"
              />
              {/* Curve line */}
              <path
                d="M 0 170 Q 150 140 280 90 T 520 60 T 800 30"
                fill="none"
                stroke="#10b981"
                strokeWidth="2.5"
                strokeLinecap="round"
              />
              {/* Data points */}
              <circle cx="280" cy="90" r="4" fill="#ffffff" stroke="#10b981" strokeWidth="2" />
              <circle cx="520" cy="60" r="4" fill="#ffffff" stroke="#10b981" strokeWidth="2" />
              <circle cx="800" cy="30" r="5" fill="#10b981" />
            </svg>
            <div className="flex justify-between text-[11px] text-zinc-500 pt-3 border-t border-white/[0.05]">
              <span>Nov 1</span>
              <span>Nov 8</span>
              <span>Nov 15</span>
              <span>Nov 23 (Today)</span>
            </div>
          </div>
        </div>

        {/* Inventory Management Table */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-serif text-white">Active Showroom Inventory</h2>
            <span className="text-xs text-zinc-500">{listings.length} items cataloged</span>
          </div>

          <div className="rounded-3xl bg-dark-850/70 border border-white/[0.08] backdrop-blur-xl overflow-hidden shadow-glass">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-dark-900/80 border-b border-white/[0.06] text-zinc-400 uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="py-3.5 px-4">Item Details</th>
                    <th className="py-3.5 px-4">Price</th>
                    <th className="py-3.5 px-4">Condition</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4">Views</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.04] text-zinc-300">
                  {listings.map((item) => (
                    <tr key={item.id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-3">
                          <img
                            src={
                              item.primary_image_url ||
                              "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=200&q=80"
                            }
                            alt=""
                            className="w-10 h-10 rounded-lg object-cover bg-dark-900 flex-shrink-0"
                          />
                          <div className="min-w-0 max-w-xs">
                            <p className="font-semibold text-white truncate">{item.title}</p>
                            <p className="text-[11px] text-zinc-500 truncate">
                              {item.ward ? `${item.ward}, ` : ""}
                              {item.district}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-4 font-sans font-semibold text-gold-400">
                        {formatTZS(item.price)}
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="text-[11px] text-zinc-400">
                          {formatCondition(item.condition)}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                            item.status === "ACTIVE"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : "bg-zinc-800 text-zinc-400"
                          }`}
                        >
                          {item.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 font-mono text-zinc-400">
                        {item.views_count || 142}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          {item.status === "ACTIVE" && (
                            <button
                              onClick={() => handleMarkSold(item.id)}
                              className="px-2.5 py-1 rounded-lg bg-white/[0.04] hover:bg-emerald-500/20 text-emerald-400 text-[11px] font-medium transition-colors"
                              title="Mark as Sold"
                            >
                              Mark Sold
                            </button>
                          )}
                          <button
                            onClick={() => handleRenew(item.id)}
                            className="p-1.5 rounded-lg text-zinc-400 hover:text-gold-300 hover:bg-white/[0.05]"
                            title="Renew 30 Days"
                          >
                            <RefreshCw className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleDelete(item.id)}
                            className="p-1.5 rounded-lg text-zinc-400 hover:text-rose-400 hover:bg-white/[0.05]"
                            title="Remove"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
