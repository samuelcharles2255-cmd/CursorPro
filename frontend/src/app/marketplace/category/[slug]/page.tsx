"use client";

import React, { useState, useEffect, use } from "react";
import Link from "next/link";
import { ChevronRight, Filter, SlidersHorizontal, ArrowLeft } from "lucide-react";
import { fetchListings, fetchCategories, FALLBACK_CATEGORIES, FALLBACK_LISTINGS } from "@/lib/api";
import { Listing, Category } from "@/types";
import { ProductCard } from "@/components/features/marketplace/ProductCard";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassSidebar } from "@/components/layout/GlassSidebar";

interface CategoryPageProps {
  params: Promise<{ slug: string }>;
}

export default function CategoryPage({ params }: CategoryPageProps) {
  const { slug } = use(params);
  const [category, setCategory] = useState<Category | null>(null);
  const [listings, setListings] = useState<Listing[]>([]);
  const [subcatFilter, setSubcatFilter] = useState<string>("all");
  const [conditionFilter, setConditionFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("newest");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const cats = await fetchCategories();
        const currentCat = cats.find((c) => c.slug === slug) || FALLBACK_CATEGORIES.find((c) => c.slug === slug) || null;
        setCategory(currentCat);

        const res = await fetchListings({ category_slug: slug });
        setListings(res.results.filter((i) => !currentCat || i.category_slug === slug || i.category === currentCat.id));
      } catch (e) {
        console.warn("Category load error:", e);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [slug]);

  let filtered = listings.filter((item) => {
    if (conditionFilter !== "all" && item.condition !== conditionFilter) return false;
    return true;
  });

  if (sortBy === "price_asc") {
    filtered.sort((a, b) => Number(a.price) - Number(b.price));
  } else if (sortBy === "price_desc") {
    filtered.sort((a, b) => Number(b.price) - Number(a.price));
  } else if (sortBy === "views") {
    filtered.sort((a, b) => (b.views_count || 0) - (a.views_count || 0));
  }

  const catName = category ? category.name : slug.replace(/-/g, " ");

  return (
    <div className="flex-1 flex max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 gap-8">
      <GlassSidebar />

      <main className="flex-1 space-y-8 min-w-0">
        {/* Breadcrumb & Return */}
        <div className="flex items-center gap-2 text-xs text-zinc-400">
          <Link href="/marketplace" className="hover:text-white flex items-center gap-1">
            <ArrowLeft className="w-3.5 h-3.5" />
            Marketplace
          </Link>
          <ChevronRight className="w-3.5 h-3.5 text-zinc-600" />
          <span className="text-zinc-200 capitalize font-medium">{catName}</span>
        </div>

        {/* Category Header Card */}
        <div className="p-8 rounded-3xl bg-dark-850/70 border border-white/[0.08] backdrop-blur-xl relative overflow-hidden shadow-glass">
          <div className="max-w-2xl space-y-2">
            <span className="px-3 py-1 rounded-full bg-market-500/15 border border-market-500/30 text-market-300 text-xs font-semibold">
              Verified Department
            </span>
            <h1 className="text-3xl sm:text-4xl font-serif font-medium text-white capitalize">
              {catName}
            </h1>
            <p className="text-xs sm:text-sm text-zinc-400 leading-relaxed">
              {category?.description || "Browse all verified listings in this department across Dar es Salaam."}
            </p>
          </div>

          {/* Subcategory Pills */}
          {category?.subcategories && category.subcategories.length > 0 && (
            <div className="flex flex-wrap items-center gap-2 pt-6 mt-6 border-t border-white/[0.06]">
              <span className="text-xs text-zinc-500 font-medium mr-1">Subcategories:</span>
              <button
                onClick={() => setSubcatFilter("all")}
                className={`min-h-[44px] px-4 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  subcatFilter === "all"
                    ? "bg-market-500 text-dark-950 shadow-green-glow"
                    : "bg-white/[0.05] text-zinc-400 hover:text-white"
                }`}
              >
                All
              </button>
              {category.subcategories.map((sub) => (
                <button
                  key={sub.id}
                  onClick={() => setSubcatFilter(sub.slug)}
                  className={`min-h-[44px] px-4 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                    subcatFilter === sub.slug
                      ? "bg-market-500 text-dark-950 shadow-green-glow"
                      : "bg-white/[0.05] text-zinc-400 hover:text-white"
                  }`}
                >
                  {sub.name}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Filter & Sorting Controls */}
        <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-dark-850/50 border border-white/[0.07] text-xs">
          <div className="flex items-center gap-2">
            <span className="text-zinc-400">Condition:</span>
            <select
              value={conditionFilter}
              onChange={(e) => setConditionFilter(e.target.value)}
              className="bg-dark-900 border border-white/[0.09] rounded-lg px-2.5 py-1 text-zinc-200 focus:outline-none"
            >
              <option value="all">All Conditions</option>
              <option value="NEW">Brand New</option>
              <option value="LIKE_NEW">Like New</option>
              <option value="GOOD">Good Condition</option>
              <option value="REFURBISHED">Refurbished</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-zinc-400">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-dark-900 border border-white/[0.09] rounded-lg px-2.5 py-1 text-zinc-200 focus:outline-none"
            >
              <option value="newest">Newest First</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
              <option value="views">Most Viewed</option>
            </select>
          </div>
        </div>

        {/* Products Grid */}
        <div className="space-y-4">
          <p className="text-xs text-zinc-400 font-medium">
            Showing {filtered.length} listings in {catName}
          </p>

          {filtered.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {filtered.map((item) => (
                <ProductCard key={item.id} listing={item} />
              ))}
            </div>
          ) : (
            <div className="text-center py-16 rounded-3xl bg-dark-850/40 border border-white/[0.06] p-8 space-y-3">
              <p className="text-base font-semibold text-white">No items found</p>
              <p className="text-xs text-zinc-400">
                There are currently no listings matching this filter in {catName}.
              </p>
              <Link href="/marketplace/create-listing">
                <GlassButton variant="gold" size="sm" className="mt-2">
                  Be the first to list here
                </GlassButton>
              </Link>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
