"use client";

import React, { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { MapPin, ShoppingBag, Heart, MessageSquare, ArrowUpRight, Phone, ShieldCheck } from "lucide-react";
import { Listing } from "@/types";
import { formatTZS, formatCondition } from "@/lib/utils";
import { useCart } from "@/lib/cart";
import { SafeImage } from "@/components/ui/SafeImage";

interface ProductCardProps {
  listing: Listing;
}

export function ProductCard({ listing }: ProductCardProps) {
  const { addToCart } = useCart();
  const [isFavorited, setIsFavorited] = useState(false);
  const [addedToast, setAddedToast] = useState(false);

  const priceNum =
    typeof listing.price === "string" ? parseFloat(listing.price) : listing.price;

  const defaultImg =
    "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80";
  const imageSrc =
    listing.primary_image_url ||
    (listing.images && listing.images[0]?.image) ||
    defaultImg;

  // Optimistic favorite toggle (HCI Rule 4)
  const toggleFavorite = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsFavorited(!isFavorited);
  };

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    addToCart({
      id: listing.id,
      listing_id: listing.id,
      title: listing.title,
      price: priceNum,
      image: imageSrc,
    });
    setAddedToast(true);
    setTimeout(() => setAddedToast(false), 2000);
  };

  const whatsappPhone = listing.seller_phone ? listing.seller_phone.replace(/[^0-9]/g, "") : "255755123456";
  const whatsappUrl = `https://wa.me/${whatsappPhone}?text=${encodeURIComponent(
    `Hello! Inquiring about '${listing.title}' on The City Marketplace (${formatTZS(priceNum)}).`
  )}`;

  return (
    <article
      className="group relative rounded-2xl bg-white dark:bg-dark-850/90 border border-slate-200/90 dark:border-white/[0.08] hover:border-market-500/50 shadow-p2p-card hover:shadow-p2p-hover flex flex-col justify-between overflow-hidden transition-all duration-200 min-w-0"
    >
      {/* 1. Media Preview Container (HCI Rule 1: Zero CLS with SafeImage aspect-[4/3]) */}
      <div className="relative aspect-[4/3] w-full bg-slate-100 dark:bg-dark-900 overflow-hidden">
        <SafeImage
          src={imageSrc}
          alt={listing.title}
          fallbackType="product"
          aspectRatio="aspect-[4/3]"
          className="w-full h-full object-cover group-hover:scale-102 transition-transform duration-300"
        />

        {/* Condition Tag (Multi-cue: text + border) */}
        <div className="absolute top-2.5 left-2.5 z-10">
          <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold tracking-wide bg-white/95 dark:bg-dark-900/90 text-slate-800 dark:text-zinc-200 shadow-sm border border-slate-200/80 dark:border-white/[0.1] backdrop-blur-md">
            {formatCondition(listing.condition)}
          </span>
        </div>

        {/* Optimistic Favorite Toggle (HCI Rule 2: Minimum 44x44px target) */}
        <button
          onClick={toggleFavorite}
          className="absolute top-2.5 right-2.5 z-10 min-h-[44px] min-w-[44px] p-2 rounded-full bg-white/90 dark:bg-dark-900/90 hover:bg-white text-slate-600 dark:text-zinc-300 shadow-sm border border-slate-200/60 dark:border-white/[0.1] flex items-center justify-center transition-all"
          aria-label={isFavorited ? "Remove from saved items" : "Save item"}
        >
          <Heart
            className={`w-4 h-4 transition-colors ${
              isFavorited ? "fill-rose-500 text-rose-500" : "hover:text-rose-400"
            }`}
          />
        </button>

        {/* Negotiable Tag */}
        {listing.is_negotiable && (
          <div className="absolute bottom-2.5 right-2.5 z-10">
            <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-market-500 text-dark-950 shadow-sm">
              Inamaongezi
            </span>
          </div>
        )}
      </div>

      {/* 2. Card Content (HCI Rule 1: 3-4 scannable chunks, min-w-0, line-clamp-2) */}
      <div className="p-4 flex-1 flex flex-col justify-between space-y-3">
        <div className="space-y-1.5 min-w-0">
          {/* Location & Seller Scannable */}
          <div className="flex items-center gap-1.5 text-[11px] text-slate-500 dark:text-zinc-400 truncate">
            <MapPin className="w-3.5 h-3.5 text-market-600 dark:text-market-400 flex-shrink-0" />
            <span className="truncate">
              {listing.ward ? `${listing.ward}, ` : ""}
              {listing.district || "Dar es Salaam"}
            </span>
            <span>·</span>
            <span className="text-slate-400 dark:text-zinc-500 truncate">
              {listing.seller_name || "Verified Seller"}
            </span>
          </div>

          {/* Title */}
          <Link href={`/marketplace/listing/${listing.slug || listing.id}`} className="block">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white group-hover:text-market-600 dark:group-hover:text-market-400 transition-colors line-clamp-2 leading-snug">
              {listing.title}
            </h3>
          </Link>
        </div>

        {/* 3. Hairline Divider & Price Metric */}
        <div className="pt-3 border-t border-slate-100 dark:border-white/[0.06] flex items-center justify-between gap-2">
          <div className="min-w-0">
            <p className="text-[10px] font-medium uppercase tracking-wider text-slate-400 dark:text-zinc-500">
              Bei / Asking Price
            </p>
            <p className="text-base sm:text-lg font-bold font-sans text-market-600 dark:text-market-400 tracking-tight truncate">
              {formatTZS(priceNum)}
            </p>
          </div>

          {/* 4. Motor Ergonomics: 44x44px Touch Targets for Primary Actions */}
          <div className="flex items-center gap-1.5 flex-shrink-0">
            {/* WhatsApp Quick Action */}
            <a
              href={whatsappUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="min-h-[44px] min-w-[44px] p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 hover:bg-emerald-100 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/40 flex items-center justify-center transition-colors"
              title="Chat on WhatsApp"
              aria-label="Direct WhatsApp Chat"
            >
              <Phone className="w-4 h-4" />
            </a>

            {/* Add to Cart Button */}
            <button
              onClick={handleAddToCart}
              className="min-h-[44px] min-w-[44px] p-2.5 rounded-xl bg-slate-900 hover:bg-market-600 text-white dark:bg-white/[0.08] dark:hover:bg-market-500 dark:hover:text-dark-950 flex items-center justify-center transition-colors"
              title="Add to Cart"
              aria-label="Add to Cart"
            >
              <ShoppingBag className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Added to Bag Toast confirmation */}
      {addedToast && (
        <div className="absolute inset-x-0 bottom-0 py-1.5 bg-market-600 text-white text-[11px] font-semibold text-center z-20 animate-fadeIn">
          Item added to bag ✓
        </div>
      )}
    </article>
  );
}
