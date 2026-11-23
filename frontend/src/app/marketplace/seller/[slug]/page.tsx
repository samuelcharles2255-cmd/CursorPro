"use client";

import React, { useState, useEffect, use } from "react";
import Link from "next/link";
import {
  MapPin,
  ShieldCheck,
  CheckCircle2,
  Phone,
  MessageSquare,
  Share2,
  Star,
  Clock,
  ShoppingBag,
  ArrowLeft,
  Calendar,
  Award,
} from "lucide-react";
import { fetchListings, FALLBACK_LISTINGS } from "@/lib/api";
import { Listing } from "@/types";
import { ProductCard } from "@/components/features/marketplace/ProductCard";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassSidebar } from "@/components/layout/GlassSidebar";

interface SellerProfileProps {
  params: Promise<{ slug: string }>;
}

export default function SellerProfilePage({ params }: SellerProfileProps) {
  const { slug } = use(params);
  const [listings, setListings] = useState<Listing[]>(FALLBACK_LISTINGS);
  const [isFollowing, setIsFollowing] = useState(false);
  const [activeTab, setActiveTab] = useState<"inventory" | "reviews" | "about">("inventory");

  useEffect(() => {
    async function load() {
      const res = await fetchListings();
      setListings(res.results);
    }
    load();
  }, []);

  const sellerName = slug === "lumina_tech" ? "Lumina Luxury Tech & Goods" : slug.replace(/_/g, " ");

  return (
    <div className="flex-1 flex max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 gap-8">
      <GlassSidebar />

      <main className="flex-1 space-y-8 min-w-0">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-xs text-zinc-400">
          <Link href="/marketplace" className="hover:text-white flex items-center gap-1">
            <ArrowLeft className="w-3.5 h-3.5" />
            Marketplace
          </Link>
          <span>/</span>
          <span className="text-zinc-200 font-medium">Merchant Profile</span>
        </div>

        {/* Merchant Header Hero */}
        <div className="rounded-3xl bg-dark-850/80 border border-white/[0.09] overflow-hidden backdrop-blur-2xl shadow-glass-elevated">
          {/* Banner cover */}
          <div className="h-44 sm:h-56 bg-gradient-to-r from-market-950/50 via-dark-800 to-emerald-950/40 relative">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_var(--tw-gradient-stops))] from-market-500/15 via-transparent to-transparent" />
          </div>

          {/* Profile details bar */}
          <div className="p-6 sm:p-8 -mt-16 sm:-mt-20 relative z-10 flex flex-col sm:flex-row sm:items-end justify-between gap-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-end gap-5">
              <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-3xl bg-dark-900 border-2 border-market-500/40 p-1 shadow-green-glow/20 flex-shrink-0">
                <div className="w-full h-full rounded-2xl bg-gradient-to-br from-market-600/40 to-emerald-500/20 flex items-center justify-center text-market-300 text-3xl font-serif font-bold">
                  {sellerName[0]}
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center gap-2 flex-wrap">
                  <h1 className="text-2xl sm:text-3xl font-serif font-medium text-white">
                    {sellerName}
                  </h1>
                  <GlassBadge variant="market" size="sm" className="gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-market-400" />
                    Verified Pro Merchant
                  </GlassBadge>
                </div>
                <p className="text-xs text-zinc-400 flex items-center gap-2 flex-wrap">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-market-400" /> Masaki & Kariakoo, Dar es Salaam
                  </span>
                  <span>·</span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5 text-zinc-500" /> Member since 2024
                  </span>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2.5">
              <GlassButton
                variant={isFollowing ? "outline" : "market"}
                size="sm"
                onClick={() => setIsFollowing(!isFollowing)}
              >
                {isFollowing ? "Following Merchant" : "Follow Store"}
              </GlassButton>
              <Link href="/marketplace/messages">
                <GlassButton variant="secondary" size="sm" className="gap-1.5">
                  <MessageSquare className="w-4 h-4" />
                  Chat
                </GlassButton>
              </Link>
            </div>
          </div>

          {/* Stats Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 border-t border-white/[0.06] bg-dark-900/60 p-4 text-center text-xs">
            <div className="p-2 border-r border-white/[0.05]">
              <p className="text-lg font-bold text-white font-sans">{listings.length}</p>
              <p className="text-zinc-500 text-[11px] uppercase tracking-wider">Active Listings</p>
            </div>
            <div className="p-2 border-r border-white/[0.05]">
              <div className="flex items-center justify-center gap-1 text-market-400 font-bold text-lg">
                <Star className="w-4 h-4 fill-market-400 text-market-400" />
                <span>4.98</span>
              </div>
              <p className="text-zinc-500 text-[11px] uppercase tracking-wider">Trust Score (124 reviews)</p>
            </div>
            <div className="p-2 border-r border-white/[0.05]">
              <p className="text-lg font-bold text-emerald-400 font-sans">&lt; 15 mins</p>
              <p className="text-zinc-500 text-[11px] uppercase tracking-wider">Avg Response Time</p>
            </div>
            <div className="p-2">
              <p className="text-lg font-bold text-white font-sans">100%</p>
              <p className="text-zinc-500 text-[11px] uppercase tracking-wider">Escrow Fulfillment</p>
            </div>
          </div>
        </div>

        {/* Tab selection */}
        <div className="flex items-center gap-2 border-b border-white/[0.08] pb-3 text-xs font-medium">
          <button
            onClick={() => setActiveTab("inventory")}
            className={`pb-2 px-1 relative transition-colors ${
              activeTab === "inventory" ? "text-market-300 font-semibold" : "text-zinc-400 hover:text-white"
            }`}
          >
            Store Inventory ({listings.length})
            {activeTab === "inventory" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-market-500 shadow-green-glow" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("reviews")}
            className={`pb-2 px-1 relative transition-colors ${
              activeTab === "reviews" ? "text-market-300 font-semibold" : "text-zinc-400 hover:text-white"
            }`}
          >
            Verified Client Reviews (124)
            {activeTab === "reviews" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-market-500 shadow-green-glow" />
            )}
          </button>
          <button
            onClick={() => setActiveTab("about")}
            className={`pb-2 px-1 relative transition-colors ${
              activeTab === "about" ? "text-market-300 font-semibold" : "text-zinc-400 hover:text-white"
            }`}
          >
            Store Bio & Escrow Escort
            {activeTab === "about" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-market-500 shadow-green-glow" />
            )}
          </button>
        </div>

        {/* Inventory View */}
        {activeTab === "inventory" && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {listings.map((item) => (
              <ProductCard key={item.id} listing={item} />
            ))}
          </div>
        )}

        {/* Reviews View */}
        {activeTab === "reviews" && (
          <div className="space-y-4">
            {[
              {
                author: "Amani M.",
                role: "Fintech Executive",
                date: "2 days ago",
                comment:
                  "Purchased the MacBook Pro M3 Max. The seller met at their Masaki office, verified serial on Apple Support, and accepted payment through the escrow protocol. Seamless transaction.",
                rating: 5,
              },
              {
                author: "David K.",
                role: "Architectural Lead",
                date: "1 week ago",
                comment:
                  "Verified Rolex Submariner with full papers. Flawless condition as described. Will trade with Lumina again.",
                rating: 5,
              },
            ].map((rev, idx) => (
              <div
                key={idx}
                className="p-5 rounded-2xl bg-dark-850/60 border border-white/[0.07] backdrop-blur-md space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-white">{rev.author}</span>
                    <span className="text-zinc-500">· {rev.role}</span>
                  </div>
                  <span className="text-zinc-500 text-[11px]">{rev.date}</span>
                </div>
                <div className="flex text-gold-400 gap-0.5">
                  {"★".repeat(rev.rating)}
                </div>
                <p className="text-zinc-300 leading-relaxed">{rev.comment}</p>
              </div>
            ))}
          </div>
        )}

        {/* About View */}
        {activeTab === "about" && (
          <div className="p-8 rounded-3xl bg-dark-850/60 border border-white/[0.07] backdrop-blur-md space-y-4 text-xs sm:text-sm text-zinc-300 leading-relaxed">
            <h3 className="text-lg font-serif font-medium text-white">About Lumina Luxury Tech</h3>
            <p>
              Established in Dar es Salaam, Lumina specializes in authorized flagship workstation hardware, Swiss horology, and high-end automotive consignments.
            </p>
            <p>
              Every high-value electronic device undergoes a 42-point hardware and battery health diagnostic before listing. In-person showroom appointments are hosted in Masaki.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
