"use client";

import React, { useState, useEffect, use } from "react";
import Link from "next/link";
import {
  MapPin,
  ShieldCheck,
  Truck,
  MessageSquare,
  ShoppingBag,
  Share2,
  Heart,
  ChevronRight,
  ArrowLeft,
  CheckCircle2,
  Clock,
  Phone,
  HelpCircle,
  Eye,
} from "lucide-react";
import { fetchListingBySlug, fetchListings, startConversation, FALLBACK_LISTINGS } from "@/lib/api";
import { Listing } from "@/types";
import { formatTZS, formatCondition, formatDate, getConditionColor } from "@/lib/utils";
import { useCart } from "@/lib/cart";
import { useAuth } from "@/lib/auth";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassModal } from "@/components/ui/GlassModal";
import { GlassInput } from "@/components/ui/GlassInput";
import { ProductCard } from "@/components/features/marketplace/ProductCard";
import { SafeImage } from "@/components/ui/SafeImage";

interface ListingDetailPageProps {
  params: Promise<{ slug: string }>;
}

export default function ListingDetailPage({ params }: ListingDetailPageProps) {
  const { slug } = use(params);
  const [listing, setListing] = useState<Listing | null>(null);
  const [relatedListings, setRelatedListings] = useState<Listing[]>([]);
  const [activeImage, setActiveImage] = useState<string>("");
  const [isOfferModalOpen, setIsOfferModalOpen] = useState(false);
  const [isChatModalOpen, setIsChatModalOpen] = useState(false);
  const [offerAmount, setOfferAmount] = useState("");
  const [chatMessage, setChatMessage] = useState("");
  const [isFavorite, setIsFavorite] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  const { addToCart } = useCart();
  const { token } = useAuth();

  useEffect(() => {
    async function load() {
      const item = await fetchListingBySlug(slug);
      if (item) {
        setListing(item);
        const mainImg =
          item.primary_image_url ||
          (item.images && item.images[0]?.image) ||
          "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1200&q=80";
        setActiveImage(mainImg);
      }
      const related = await fetchListings({ page_size: 3 });
      setRelatedListings(related.results.filter((i) => i.slug !== slug).slice(0, 3));
    }
    load();
  }, [slug]);

  if (!listing) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center space-y-4">
        <p className="text-zinc-400">Loading fine listing details...</p>
      </div>
    );
  }

  const priceNum = typeof listing.price === "string" ? parseFloat(listing.price) : listing.price;
  const imageGallery =
    listing.images && listing.images.length > 0
      ? listing.images.map((img) => img.image)
      : [activeImage || "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1200&q=80"];

  const handleMakeOffer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) {
      setNotification("Please sign in to transmit formal offers to verified merchants.");
      setTimeout(() => setNotification(null), 4000);
      return;
    }
    try {
      await startConversation(
        listing.id,
        `Official Offer Transmitted: ${formatTZS(offerAmount)} TZS. Inquiring regarding inspection & escrow checkout.`,
        token
      );
      setIsOfferModalOpen(false);
      setNotification(`Offer of ${formatTZS(offerAmount)} transmitted to seller via Atrium Escrow.`);
      setTimeout(() => setNotification(null), 4000);
    } catch (err: any) {
      setNotification(err.message || "Failed to transmit offer. Please retry.");
      setTimeout(() => setNotification(null), 4000);
    }
  };

  const handleSendChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) {
      setNotification("Please sign in to send direct inquiries to the merchant.");
      setTimeout(() => setNotification(null), 4000);
      return;
    }
    try {
      await startConversation(listing.id, chatMessage, token);
      setIsChatModalOpen(false);
      setChatMessage("");
      setNotification("Direct inquiry dispatched to merchant. Check your Messages thread.");
      setTimeout(() => setNotification(null), 4000);
    } catch (err: any) {
      setNotification(err.message || "Failed to dispatch message.");
      setTimeout(() => setNotification(null), 4000);
    }
  };

  const whatsappPhone = listing.seller_phone ? listing.seller_phone.replace(/[^0-9]/g, "") : "255755123456";
  const whatsappUrl = `https://wa.me/${whatsappPhone}?text=${encodeURIComponent(
    `Hello, I am inquiring about your listing '${listing.title}' priced at ${formatTZS(priceNum)} on The City.`
  )}`;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-12">
      {/* Toast Notification */}
      {notification && (
        <div className="fixed top-20 right-6 z-50 p-4 rounded-xl bg-market-600 text-dark-950 font-semibold shadow-green-glow flex items-center gap-2 text-xs">
          <CheckCircle2 className="w-4 h-4" />
          <span>{notification}</span>
        </div>
      )}

      {/* Breadcrumb Navigation */}
      <div className="flex items-center gap-2 text-xs text-zinc-400">
        <Link href="/marketplace" className="hover:text-white flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" />
          Marketplace
        </Link>
        <ChevronRight className="w-3.5 h-3.5 text-zinc-600" />
        {listing.category_slug && (
          <>
            <Link
              href={`/marketplace/category/${listing.category_slug}`}
              className="hover:text-white capitalize"
            >
              {listing.category_name || listing.category_slug}
            </Link>
            <ChevronRight className="w-3.5 h-3.5 text-zinc-600" />
          </>
        )}
        <span className="text-zinc-300 truncate max-w-[240px]">{listing.title}</span>
      </div>

      {/* Main Product Showcase Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12">
        {/* Left: Image Gallery */}
        <div className="lg:col-span-7 space-y-4">
          <div className="relative aspect-[4/3] w-full rounded-3xl bg-dark-900 border border-white/[0.08] overflow-hidden shadow-glass">
            <SafeImage
              src={activeImage}
              alt={listing.title}
              aspectRatio="aspect-[4/3]"
              className="w-full h-full object-cover object-center"
              containerClassName="w-full h-full"
            />
            {/* Condition badge */}
            <div className="absolute top-4 left-4 z-10">
              <span
                className={`text-xs font-semibold uppercase tracking-wider px-3 py-1 rounded-full border backdrop-blur-md ${getConditionColor(
                  listing.condition
                )}`}
              >
                {formatCondition(listing.condition)}
              </span>
            </div>
            {/* View count */}
            <div className="absolute top-4 right-4 z-10 flex items-center gap-1.5 text-xs text-zinc-300 bg-black/60 px-3 py-1 rounded-full backdrop-blur-md">
              <Eye className="w-3.5 h-3.5 text-market-400" />
              <span>{listing.views_count || 142} views</span>
            </div>
          </div>

          {/* Thumbnails row */}
          <div className="flex items-center gap-3 overflow-x-auto pb-2">
            {imageGallery.map((img, idx) => (
              <button
                key={idx}
                onClick={() => setActiveImage(img)}
                className={`relative w-20 h-20 rounded-xl overflow-hidden border transition-all flex-shrink-0 ${
                  activeImage === img
                    ? "border-market-500 ring-2 ring-market-500/40"
                    : "border-white/[0.1] hover:border-white/[0.25] opacity-70 hover:opacity-100"
                }`}
              >
                <SafeImage
                  src={img}
                  alt="thumbnail"
                  aspectRatio="aspect-square"
                  className="w-full h-full object-cover"
                />
              </button>
            ))}
          </div>

          {/* Specifications Table */}
          <div className="p-6 rounded-3xl bg-dark-850/60 border border-white/[0.07] backdrop-blur-xl space-y-4">
            <h3 className="text-base font-semibold text-white font-sans flex items-center gap-2">
              <span>Verified Specifications</span>
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-dark-900/60 border border-white/[0.05] flex justify-between">
                <span className="text-zinc-400">Condition</span>
                <span className="text-white font-medium">{formatCondition(listing.condition)}</span>
              </div>
              <div className="p-3 rounded-xl bg-dark-900/60 border border-white/[0.05] flex justify-between">
                <span className="text-zinc-400">Location</span>
                <span className="text-white font-medium">
                  {listing.ward ? `${listing.ward}, ` : ""}
                  {listing.district ? `${listing.district}, ` : ""}
                  {listing.region}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-dark-900/60 border border-white/[0.05] flex justify-between">
                <span className="text-zinc-400">Pricing Mode</span>
                <span className="text-market-400 font-medium">
                  {listing.is_negotiable ? "Negotiable / Bei Inamaongezi" : "Fixed Price"}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-dark-900/60 border border-white/[0.05] flex justify-between">
                <span className="text-zinc-400">Escrow Security</span>
                <span className="text-emerald-400 font-medium">100% Guaranteed</span>
              </div>
              {/* Dynamic attributes if present */}
              {listing.attributes &&
                listing.attributes.map((attr, i) => (
                  <div
                    key={i}
                    className="p-3 rounded-xl bg-dark-900/60 border border-white/[0.05] flex justify-between"
                  >
                    <span className="text-zinc-400">{attr.name}</span>
                    <span className="text-white font-medium">{attr.value}</span>
                  </div>
                ))}
            </div>
          </div>

          {/* Description */}
          <div className="p-6 rounded-3xl bg-dark-850/60 border border-white/[0.07] backdrop-blur-xl space-y-3">
            <h3 className="text-base font-semibold text-white">Full Item Description</h3>
            <div className="text-xs sm:text-sm text-zinc-300 leading-relaxed whitespace-pre-line">
              {listing.description}
            </div>
          </div>
        </div>

        {/* Right: Buy, Offer & Seller Column */}
        <div className="lg:col-span-5 space-y-6">
          {/* Main Pricing & Action Card */}
          <div className="p-6 sm:p-8 rounded-3xl bg-dark-850/80 border border-white/[0.1] backdrop-blur-2xl shadow-glass-elevated space-y-6">
            <div>
              <p className="text-xs uppercase tracking-wider text-zinc-400 mb-1">
                Verified Listing Price
              </p>
              <div className="flex items-baseline gap-3">
                <p className="text-3xl sm:text-4xl font-bold font-sans text-market-400 tracking-tight">
                  {formatTZS(priceNum)}
                </p>
                {listing.is_negotiable && (
                  <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-market-500/15 text-market-300 border border-market-500/30">
                    Bei Inamaongezi
                  </span>
                )}
              </div>
            </div>

            <div className="space-y-3">
              {/* Add to Cart / Buy Button */}
              <button
                onClick={() => {
                  addToCart({
                    id: listing.id,
                    listing_id: listing.id,
                    title: listing.title,
                    price: priceNum,
                    image: activeImage,
                  });
                  setNotification("Item added to your trade bag.");
                  setTimeout(() => setNotification(null), 3000);
                }}
                className="w-full min-h-[48px] px-5 rounded-2xl bg-market-600 hover:bg-market-500 text-dark-950 font-bold text-sm flex items-center justify-center gap-2 shadow-green-glow transition-all active:scale-98"
              >
                <ShoppingBag className="w-5 h-5" />
                Add to Cart &amp; Checkout
              </button>

              {/* Make an Offer Button */}
              {listing.is_negotiable && (
                <button
                  type="button"
                  onClick={() => setIsOfferModalOpen(true)}
                  className="w-full min-h-[44px] px-5 rounded-xl bg-market-500/10 hover:bg-market-500/20 text-market-300 border border-market-500/30 text-xs font-semibold flex items-center justify-center transition-colors"
                >
                  Make a Counter Offer
                </button>
              )}

              {/* Start In-App Chat */}
              <button
                type="button"
                onClick={() => setIsChatModalOpen(true)}
                className="w-full min-h-[44px] px-5 rounded-xl bg-white/[0.06] hover:bg-white/[0.1] text-zinc-200 border border-white/[0.08] text-xs font-semibold flex items-center justify-center gap-2 transition-colors"
              >
                <MessageSquare className="w-4 h-4 text-zinc-300" />
                In-App Seller Chat
              </button>

              {/* Direct WhatsApp Contact */}
              <a
                href={whatsappUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full block"
              >
                <button
                  type="button"
                  className="w-full min-h-[44px] px-4 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-400 font-semibold text-xs flex items-center justify-center gap-2 transition-colors"
                >
                  <Phone className="w-4 h-4" />
                  Chat Directly on WhatsApp ({whatsappPhone})
                </button>
              </a>
            </div>

            {/* Delivery & Logistics notes */}
            <div className="pt-4 border-t border-white/[0.06] space-y-3 text-xs text-zinc-400">
              <div className="flex items-center gap-2.5">
                <Truck className="w-4 h-4 text-market-400 flex-shrink-0" />
                <span>
                  Delivery: Available across {listing.region || "Dar es Salaam"} & express courier upcountry.
                </span>
              </div>
              <div className="flex items-center gap-2.5">
                <MapPin className="w-4 h-4 text-market-400 flex-shrink-0" />
                <span>
                  Direct Pickup: In-person inspection available at {listing.ward || listing.district || "Masaki"}.
                </span>
              </div>
              <div className="flex items-center gap-2.5">
                <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span>Escrow Protected: Money remains guarded until item meets description.</span>
              </div>
            </div>
          </div>

          {/* Seller Profile Card */}
          <div className="p-6 rounded-3xl bg-dark-850/60 border border-white/[0.08] backdrop-blur-xl space-y-4">
            <span className="text-xs font-semibold tracking-wider uppercase text-zinc-400">
              Verified Merchant
            </span>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-market-600/30 to-market-400/20 border border-market-500/30 flex items-center justify-center text-market-300 font-bold text-sm">
                  {listing.seller_name ? listing.seller_name[0] : "S"}
                </div>
                <div>
                  <div className="flex items-center gap-1.5">
                    <p className="text-sm font-semibold text-white">
                      {listing.seller_name || listing.seller_username || "Verified Seller"}
                    </p>
                    <CheckCircle2 className="w-4 h-4 text-market-400" />
                  </div>
                  <p className="text-xs text-zinc-500">Member since 2024 · 99.8% Trust Rating</p>
                </div>
              </div>
              <Link href={`/marketplace/seller/${listing.seller_username || "lumina_tech"}`}>
                <GlassButton variant="ghost" size="sm">
                  Store Profile
                </GlassButton>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Related Items Section */}
      {relatedListings.length > 0 && (
        <div className="pt-12 border-t border-white/[0.08] space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-serif text-white">Similar Verified Offerings</h3>
            <Link
              href="/marketplace/search"
              className="text-xs text-market-400 hover:text-market-300"
            >
              Browse all items →
            </Link>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {relatedListings.map((rel) => (
              <ProductCard key={rel.id} listing={rel} />
            ))}
          </div>
        </div>
      )}

      {/* Make Offer Modal */}
      <GlassModal
        isOpen={isOfferModalOpen}
        onClose={() => setIsOfferModalOpen(false)}
        title="Make an Offer"
        description={`Asking price: ${formatTZS(priceNum)}`}
      >
        <form onSubmit={handleMakeOffer} className="space-y-4 pt-2">
          <GlassInput
            label="Your Offer Amount (TSh)"
            type="number"
            placeholder="e.g. 7200000"
            value={offerAmount}
            onChange={(e) => setOfferAmount(e.target.value)}
            required
          />
          <p className="text-[11px] text-zinc-400">
            If accepted by the seller, an escrow invoice will be issued for in-person or courier inspection.
          </p>
          <div className="flex justify-end gap-2 pt-2">
            <GlassButton
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setIsOfferModalOpen(false)}
            >
              Cancel
            </GlassButton>
            <GlassButton type="submit" variant="market" size="sm">
              Submit Offer
            </GlassButton>
          </div>
        </form>
      </GlassModal>

      {/* In-App Chat Modal */}
      <GlassModal
        isOpen={isChatModalOpen}
        onClose={() => setIsChatModalOpen(false)}
        title={`Message ${listing.seller_name || "Seller"}`}
        description={`Regarding: ${listing.title}`}
      >
        <form onSubmit={handleSendChat} className="space-y-4 pt-2">
          <textarea
            rows={4}
            value={chatMessage}
            onChange={(e) => setChatMessage(e.target.value)}
            placeholder="Hi, is this item available for inspection in Masaki today?"
            className="w-full bg-dark-900 border border-white/[0.09] rounded-xl p-3 text-xs text-white placeholder:text-zinc-500 focus:outline-none focus:border-market-500/50"
            required
          />
          <div className="flex justify-end gap-2">
            <GlassButton
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setIsChatModalOpen(false)}
            >
              Cancel
            </GlassButton>
            <GlassButton type="submit" variant="market" size="sm">
              Send Message
            </GlassButton>
          </div>
        </form>
      </GlassModal>
    </div>
  );
}
