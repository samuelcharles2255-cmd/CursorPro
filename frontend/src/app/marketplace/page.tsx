"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  ShoppingBag,
  Search,
  SlidersHorizontal,
  MapPin,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  PlusCircle,
  Truck,
  CheckCircle2,
  X,
  Phone,
  Tag,
} from "lucide-react";
import { fetchListings, fetchCategories, FALLBACK_LISTINGS, FALLBACK_CATEGORIES } from "@/lib/api";
import { Listing, Category } from "@/types";
import { ProductCard } from "@/components/features/marketplace/ProductCard";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassSidebar } from "@/components/layout/GlassSidebar";
import { GlassModal } from "@/components/ui/GlassModal";

export default function MarketplaceHomePage() {
  const [listings, setListings] = useState<Listing[]>(FALLBACK_LISTINGS);
  const [categories, setCategories] = useState<Category[]>(FALLBACK_CATEGORIES);
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [selectedDistrict, setSelectedDistrict] = useState<string>("all");
  const [selectedCondition, setSelectedCondition] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [isFilterDrawerOpen, setIsFilterDrawerOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const [lst, cat] = await Promise.all([
          fetchListings(),
          fetchCategories(),
        ]);
        if (lst.results.length > 0) setListings(lst.results);
        if (cat.length > 0) setCategories(cat);
      } catch (e) {
        console.warn("Marketplace fetch fallback:", e);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, []);

  // Filter listings
  const filteredListings = listings.filter((item) => {
    if (activeCategory !== "all" && item.category_slug !== activeCategory) {
      return false;
    }
    if (selectedDistrict !== "all" && item.district?.toLowerCase() !== selectedDistrict.toLowerCase()) {
      return false;
    }
    if (selectedCondition !== "all" && item.condition !== selectedCondition) {
      return false;
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const match =
        item.title.toLowerCase().includes(q) ||
        (item.description && item.description.toLowerCase().includes(q)) ||
        (item.ward && item.ward.toLowerCase().includes(q));
      if (!match) return false;
    }
    return true;
  });

  return (
    <div className="flex-1 flex max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 gap-8">
      {/* Sidebar for desktop navigation */}
      <GlassSidebar />

      <main className="flex-1 space-y-8 min-w-0">
        {/* ========================================================= */}
        {/* 1. HIGH-CONTRAST DARK ANCHOR HERO BANNER                  */}
        {/* ========================================================= */}
        <section className="relative rounded-3xl bg-dark-900 border border-white/[0.1] p-6 sm:p-10 overflow-hidden shadow-glass-elevated">
          {/* Subtle green ambient spotlight */}
          <div className="absolute top-0 right-0 w-80 h-80 bg-market-500/[0.1] rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 max-w-2xl space-y-4">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-market-500/15 border border-market-500/30 text-market-300 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-market-400 animate-pulse" />
              Community Peer-to-Peer Trade · Dar es Salaam &amp; Tanzania
            </div>

            <h1 className="text-3xl sm:text-5xl font-serif font-bold text-white tracking-tight leading-tight">
              A Cleaner, Safer Way to Buy &amp; Sell.
            </h1>

            <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed max-w-xl">
              Buy directly from verified neighbours and merchants with physical inspection in Masaki, Kariakoo, and express courier delivery across Tanzania.
            </p>

            {/* Quick Search & Post Bar */}
            <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-zinc-400 absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search laptops, cameras, phones, vehicles in Dar..."
                  className="w-full min-h-[48px] bg-dark-950/90 border border-white/[0.12] rounded-2xl pl-11 pr-4 py-2.5 text-xs text-white placeholder:text-zinc-500 focus:outline-none focus:border-market-500/60 transition-colors"
                />
              </div>

              <Link href="/marketplace/create-listing">
                <button className="min-h-[48px] px-5 rounded-2xl bg-market-600 hover:bg-market-500 text-dark-950 font-bold text-xs inline-flex items-center justify-center gap-2 shadow-green-glow transition-all active:scale-98 w-full sm:w-auto">
                  <PlusCircle className="w-4 h-4" />
                  Post Your Item Free
                </button>
              </Link>
            </div>
          </div>
        </section>

        {/* ========================================================= */}
        {/* 2. PROGRESSIVE DISCLOSURE: 5-7 CATEGORY CHIPS             */}
        {/* ========================================================= */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-zinc-400">
              Popular Categories
            </span>
            <button
              onClick={() => setIsFilterDrawerOpen(true)}
              className="min-h-[44px] px-3 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] text-xs text-zinc-300 border border-white/[0.06] inline-flex items-center gap-1.5 transition-colors"
              aria-label="Open filter settings"
            >
              <SlidersHorizontal className="w-3.5 h-3.5 text-market-400" />
              <span>Filters</span>
            </button>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
            <button
              onClick={() => setActiveCategory("all")}
              className={`min-h-[44px] px-4 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                activeCategory === "all"
                  ? "bg-market-500 text-dark-950 font-bold shadow-green-glow"
                  : "bg-dark-850 text-zinc-400 hover:text-white border border-white/[0.07]"
              }`}
            >
              All Items ({listings.length})
            </button>

            {categories.slice(0, 6).map((cat) => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.slug)}
                className={`min-h-[44px] px-4 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  activeCategory === cat.slug
                    ? "bg-market-500 text-dark-950 font-bold shadow-green-glow"
                    : "bg-dark-850 text-zinc-400 hover:text-white border border-white/[0.07]"
                }`}
              >
                {cat.name}
              </button>
            ))}
          </div>
        </section>

        {/* ========================================================= */}
        {/* 3. ACTIVE FILTERS & LOCATION CHIPS BAR                    */}
        {/* ========================================================= */}
        <section className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-2xl bg-dark-900/60 border border-white/[0.06] text-xs">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-zinc-500 font-medium flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5 text-market-400" />
              District:
            </span>
            {["all", "Kinondoni", "Ilala", "Temeke", "Ubungo"].map((dist) => (
              <button
                key={dist}
                onClick={() => setSelectedDistrict(dist)}
                className={`min-h-[36px] px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  selectedDistrict.toLowerCase() === dist.toLowerCase()
                    ? "bg-white/[0.12] text-white border border-white/[0.15]"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {dist === "all" ? "All Dar" : dist}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <span className="text-zinc-500 font-medium">Condition:</span>
            <select
              value={selectedCondition}
              onChange={(e) => setSelectedCondition(e.target.value)}
              className="bg-dark-850 border border-white/[0.08] rounded-xl px-2.5 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-market-500"
            >
              <option value="all">All Conditions</option>
              <option value="NEW">Brand New</option>
              <option value="LIKE_NEW">Like New</option>
              <option value="GOOD">Good Working</option>
              <option value="REFURBISHED">Refurbished</option>
            </select>
          </div>
        </section>

        {/* ========================================================= */}
        {/* 4. BRIGHT, AIRY P2P CONTENT FEED                         */}
        {/* ========================================================= */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-white font-sans">
                Community Listings
              </h2>
              <p className="text-xs text-zinc-400">
                Showing {filteredListings.length} verified items available for trade
              </p>
            </div>
            {activeCategory !== "all" && (
              <button
                onClick={() => {
                  setActiveCategory("all");
                  setSelectedDistrict("all");
                  setSelectedCondition("all");
                }}
                className="text-xs text-market-400 hover:underline flex items-center gap-1 font-medium"
              >
                <X className="w-3.5 h-3.5" /> Reset filters
              </button>
            )}
          </div>

          {/* Product Grid */}
          {filteredListings.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredListings.map((item) => (
                <ProductCard key={item.id} listing={item} />
              ))}
            </div>
          ) : (
            <div className="text-center py-20 rounded-3xl bg-dark-850/40 border border-white/[0.06] p-8 space-y-3">
              <ShoppingBag className="w-10 h-10 text-zinc-600 mx-auto" />
              <p className="text-base font-semibold text-white">No items found</p>
              <p className="text-xs text-zinc-400 max-w-sm mx-auto">
                No items match your selected filters. Try choosing &ldquo;All Dar&rdquo; or clearing your category.
              </p>
              <button
                onClick={() => {
                  setActiveCategory("all");
                  setSelectedDistrict("all");
                  setSelectedCondition("all");
                }}
                className="px-4 py-2 rounded-xl bg-market-600 text-dark-950 font-bold text-xs inline-flex items-center gap-1.5 shadow-green-glow"
              >
                View All Listings
              </button>
            </div>
          )}
        </section>

        {/* ========================================================= */}
        {/* 5. HIGH-CONTRAST DARK ANCHOR TRUST FOOTER BANNER          */}
        {/* ========================================================= */}
        <section className="p-6 sm:p-8 rounded-3xl bg-dark-900 border border-white/[0.08] shadow-glass space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-xs">
            <div className="flex items-start gap-3">
              <div className="p-2.5 rounded-xl bg-market-500/15 text-market-400 flex-shrink-0">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <div>
                <p className="font-bold text-white text-sm">Escrow Protection</p>
                <p className="text-zinc-400 text-xs mt-0.5">
                  Money is held securely until you inspect the device in person or at delivery.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2.5 rounded-xl bg-cyan-500/15 text-cyan-400 flex-shrink-0">
                <Truck className="w-5 h-5" />
              </div>
              <div>
                <p className="font-bold text-white text-sm">Kariakoo &amp; Upcountry</p>
                <p className="text-zinc-400 text-xs mt-0.5">
                  Same-day courier across Dar es Salaam, or bus parcel delivery to Mbeya, Arusha, Mwanza.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="p-2.5 rounded-xl bg-emerald-500/15 text-emerald-400 flex-shrink-0">
                <Phone className="w-5 h-5" />
              </div>
              <div>
                <p className="font-bold text-white text-sm">Direct WhatsApp &amp; Chat</p>
                <p className="text-zinc-400 text-xs mt-0.5">
                  Negotiate directly with sellers in Swahili or English with one tap.
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Slide-over Filter Drawer (HCI Rule 2 & 3) */}
      <GlassModal
        isOpen={isFilterDrawerOpen}
        onClose={() => setIsFilterDrawerOpen(false)}
        title="Refine Marketplace Feed"
        description="Select criteria to filter local peer-to-peer items"
      >
        <div className="space-y-4 pt-2 text-xs">
          <div>
            <label className="font-semibold text-zinc-300 block mb-1.5">Department</label>
            <select
              value={activeCategory}
              onChange={(e) => setActiveCategory(e.target.value)}
              className="w-full min-h-[44px] bg-dark-900 border border-white/[0.1] rounded-xl px-3 py-2 text-zinc-200"
            >
              <option value="all">All Departments</option>
              {categories.map((c) => (
                <option key={c.id} value={c.slug}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="font-semibold text-zinc-300 block mb-1.5">Dar es Salaam District</label>
            <select
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
              className="w-full min-h-[44px] bg-dark-900 border border-white/[0.1] rounded-xl px-3 py-2 text-zinc-200"
            >
              <option value="all">All Districts</option>
              <option value="Kinondoni">Kinondoni (Masaki, Oysterbay, Sinza)</option>
              <option value="Ilala">Ilala (Kariakoo, Posta)</option>
              <option value="Temeke">Temeke</option>
              <option value="Ubungo">Ubungo</option>
              <option value="Kigamboni">Kigamboni</option>
            </select>
          </div>

          <div className="pt-2 flex justify-end gap-2">
            <button
              onClick={() => {
                setActiveCategory("all");
                setSelectedDistrict("all");
                setSelectedCondition("all");
                setIsFilterDrawerOpen(false);
              }}
              className="min-h-[44px] px-4 rounded-xl text-zinc-400 hover:text-white"
            >
              Clear
            </button>
            <button
              onClick={() => setIsFilterDrawerOpen(false)}
              className="min-h-[44px] px-5 rounded-xl bg-market-600 text-dark-950 font-bold"
            >
              Apply Filter
            </button>
          </div>
        </div>
      </GlassModal>
    </div>
  );
}
