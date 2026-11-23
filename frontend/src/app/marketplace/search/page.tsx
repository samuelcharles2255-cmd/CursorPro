"use client";

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  Search,
  Filter,
  SlidersHorizontal,
  X,
  MapPin,
  Tag,
  Grid,
  List,
  Sparkles,
} from "lucide-react";
import { fetchListings, fetchCategories, FALLBACK_LISTINGS, FALLBACK_CATEGORIES } from "@/lib/api";
import { Listing, Category } from "@/types";
import { ProductCard } from "@/components/features/marketplace/ProductCard";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassInput } from "@/components/ui/GlassInput";
import { GlassSidebar } from "@/components/layout/GlassSidebar";
import { formatTZS } from "@/lib/utils";

function SearchContent() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("search") || "";

  const [search, setSearch] = useState(initialQuery);
  const [categorySlug, setCategorySlug] = useState<string>("all");
  const [district, setDistrict] = useState<string>("all");
  const [condition, setCondition] = useState<string>("all");
  const [minPrice, setMinPrice] = useState<string>("");
  const [maxPrice, setMaxPrice] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("newest");
  const [listings, setListings] = useState<Listing[]>(FALLBACK_LISTINGS);
  const [categories, setCategories] = useState<Category[]>(FALLBACK_CATEGORIES);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const [lst, cat] = await Promise.all([
          fetchListings({ search }),
          fetchCategories(),
        ]);
        if (lst.results.length > 0) setListings(lst.results);
        if (cat.length > 0) setCategories(cat);
      } catch (e) {
        console.warn("Search load error:", e);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, [search]);

  // Client-side multi-faceted filtering
  const filtered = listings.filter((item) => {
    if (search.trim()) {
      const q = search.toLowerCase();
      const match =
        item.title.toLowerCase().includes(q) ||
        (item.description && item.description.toLowerCase().includes(q)) ||
        (item.ward && item.ward.toLowerCase().includes(q));
      if (!match) return false;
    }
    if (categorySlug !== "all" && item.category_slug !== categorySlug) {
      return false;
    }
    if (district !== "all" && item.district.toLowerCase() !== district.toLowerCase()) {
      return false;
    }
    if (condition !== "all" && item.condition !== condition) {
      return false;
    }
    const priceNum = Number(item.price);
    if (minPrice && priceNum < Number(minPrice)) return false;
    if (maxPrice && priceNum > Number(maxPrice)) return false;
    return true;
  });

  if (sortBy === "price_asc") {
    filtered.sort((a, b) => Number(a.price) - Number(b.price));
  } else if (sortBy === "price_desc") {
    filtered.sort((a, b) => Number(b.price) - Number(a.price));
  } else if (sortBy === "views") {
    filtered.sort((a, b) => (b.views_count || 0) - (a.views_count || 0));
  }

  const clearFilters = () => {
    setSearch("");
    setCategorySlug("all");
    setDistrict("all");
    setCondition("all");
    setMinPrice("");
    setMaxPrice("");
  };

  return (
    <div className="flex-1 flex max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 gap-8">
      <GlassSidebar />

      <main className="flex-1 space-y-6 min-w-0">
        {/* Top Search bar */}
        <div className="p-4 rounded-2xl bg-dark-850/70 border border-white/[0.08] backdrop-blur-xl">
          <div className="relative">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by keywords, model, serial, or location..."
              className="w-full bg-dark-900/80 rounded-xl pl-10 pr-10 py-3 text-sm text-white placeholder:text-zinc-500 border border-white/[0.07] focus:outline-none focus:border-market-500/60"
            />
            {search && (
              <button
                onClick={() => setSearch("")}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Filter bar */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Filter Panel */}
          <aside className="md:col-span-1 p-5 rounded-2xl bg-dark-850/60 border border-white/[0.08] backdrop-blur-xl space-y-5 h-fit">
            <div className="flex items-center justify-between pb-3 border-b border-white/[0.06]">
              <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400 flex items-center gap-1.5">
                <SlidersHorizontal className="w-3.5 h-3.5 text-market-400" />
                Refine Results
              </span>
              <button
                onClick={clearFilters}
                className="text-[11px] text-market-400 hover:underline"
              >
                Clear all
              </button>
            </div>

            {/* Department */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-zinc-300">Department</label>
              <select
                value={categorySlug}
                onChange={(e) => setCategorySlug(e.target.value)}
                className="w-full bg-dark-900 border border-white/[0.09] rounded-xl px-3 py-2 text-xs text-zinc-200 focus:outline-none focus:border-gold-500/50"
              >
                <option value="all">All Departments</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.slug}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* District */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-zinc-300">District (Dar es Salaam)</label>
              <select
                value={district}
                onChange={(e) => setDistrict(e.target.value)}
                className="w-full bg-dark-900 border border-white/[0.09] rounded-xl px-3 py-2 text-xs text-zinc-200 focus:outline-none focus:border-gold-500/50"
              >
                <option value="all">All Districts</option>
                <option value="kinondoni">Kinondoni (Masaki, Oysterbay)</option>
                <option value="ilala">Ilala (Kariakoo, Posta)</option>
                <option value="temeke">Temeke</option>
                <option value="ubungo">Ubungo</option>
                <option value="kigamboni">Kigamboni</option>
              </select>
            </div>

            {/* Condition */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-zinc-300">Condition</label>
              <select
                value={condition}
                onChange={(e) => setCondition(e.target.value)}
                className="w-full bg-dark-900 border border-white/[0.09] rounded-xl px-3 py-2 text-xs text-zinc-200 focus:outline-none focus:border-gold-500/50"
              >
                <option value="all">All Conditions</option>
                <option value="NEW">Brand New</option>
                <option value="LIKE_NEW">Like New / Pristine</option>
                <option value="GOOD">Good Condition</option>
                <option value="REFURBISHED">Refurbished</option>
              </select>
            </div>

            {/* Price Range */}
            <div className="space-y-2">
              <label className="text-xs font-medium text-zinc-300">Price Range (TSh)</label>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="number"
                  placeholder="Min"
                  value={minPrice}
                  onChange={(e) => setMinPrice(e.target.value)}
                  className="w-full bg-dark-900 border border-white/[0.09] rounded-xl px-3 py-1.5 text-xs text-zinc-200 focus:outline-none"
                />
                <input
                  type="number"
                  placeholder="Max"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(e.target.value)}
                  className="w-full bg-dark-900 border border-white/[0.09] rounded-xl px-3 py-1.5 text-xs text-zinc-200 focus:outline-none"
                />
              </div>
            </div>
          </aside>

          {/* Results Area */}
          <div className="md:col-span-3 space-y-4">
            <div className="flex items-center justify-between text-xs text-zinc-400">
              <p>
                Found <span className="font-semibold text-white">{filtered.length}</span> matching listings
                {search && <span> for &ldquo;{search}&rdquo;</span>}
              </p>
              <div className="flex items-center gap-2">
                <span>Sort:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="bg-dark-900 border border-white/[0.09] rounded-lg px-2.5 py-1 text-zinc-200 text-xs focus:outline-none"
                >
                  <option value="newest">Newest First</option>
                  <option value="price_asc">Price: Low to High</option>
                  <option value="price_desc">Price: High to Low</option>
                  <option value="views">Most Viewed</option>
                </select>
              </div>
            </div>

            {filtered.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {filtered.map((item) => (
                  <ProductCard key={item.id} listing={item} />
                ))}
              </div>
            ) : (
              <div className="text-center py-20 rounded-3xl bg-dark-850/40 border border-white/[0.06] p-8 space-y-3">
                <p className="text-base font-semibold text-white">No listings match your criteria</p>
                <p className="text-xs text-zinc-400">
                  Try broadening your search keywords or removing price filters.
                </p>
                <GlassButton variant="outline" size="sm" onClick={clearFilters}>
                  Clear all filters
                </GlassButton>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-zinc-400">Loading search...</div>}>
      <SearchContent />
    </Suspense>
  );
}
