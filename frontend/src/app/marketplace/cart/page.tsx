"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ShoppingBag,
  Trash2,
  ShieldCheck,
  Truck,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  CreditCard,
  Lock,
} from "lucide-react";
import { useCart } from "@/lib/cart";
import { formatTZS } from "@/lib/utils";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassInput } from "@/components/ui/GlassInput";
import { GlassBadge } from "@/components/ui/GlassBadge";

export default function CartPage() {
  const { items, removeFromCart, clearCart, totalPrice } = useCart();
  const [deliveryMethod, setDeliveryMethod] = useState<"courier" | "pickup">("courier");
  const [paymentMethod, setPaymentMethod] = useState<"mpesa" | "tigo" | "bank">("mpesa");
  const [recipientName, setRecipientName] = useState("");
  const [recipientPhone, setRecipientPhone] = useState("+255");
  const [deliveryAddress, setDeliveryAddress] = useState("");
  const [isOrdered, setIsOrdered] = useState(false);
  const [orderNumber, setOrderNumber] = useState("");

  const deliveryFee = deliveryMethod === "courier" ? 15000 : 0;
  const grandTotal = totalPrice + deliveryFee;

  const handleCheckout = (e: React.FormEvent) => {
    e.preventDefault();
    const orderNum = `AT-${Math.floor(100000 + Math.random() * 900000)}`;
    setOrderNumber(orderNum);
    setIsOrdered(true);
    clearCart();
  };

  if (isOrdered) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center space-y-6">
        <div className="w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mx-auto shadow-emerald-500/20 shadow-lg">
          <CheckCircle2 className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <h1 className="text-3xl font-serif font-medium text-white">Order Confirmed with Escrow</h1>
          <p className="text-xs text-zinc-400">Order Identifier: <span className="font-mono text-market-400 font-bold">{orderNumber}</span></p>
          <p className="text-xs sm:text-sm text-zinc-300 max-w-md mx-auto leading-relaxed pt-2">
            Your payment is placed in secure The City Escrow vault. The merchant will dispatch the item for inspection before funds are credited.
          </p>
        </div>
        <div className="pt-4 flex justify-center gap-3">
          <Link href="/marketplace">
            <GlassButton variant="market" size="md">
              Return to Marketplace
            </GlassButton>
          </Link>
          <Link href="/marketplace/seller/dashboard">
            <GlassButton variant="secondary" size="md">
              View Activity
            </GlassButton>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-zinc-400">
        <Link href="/marketplace" className="hover:text-white flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" />
          Marketplace
        </Link>
        <span>/</span>
        <span className="text-zinc-200 font-medium">Fine Trade Bag</span>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-serif font-medium text-white">
            Shopping Cart & Escrow Checkout
          </h1>
          <p className="text-xs text-zinc-400">
            {items.length} {items.length === 1 ? "item" : "items"} selected for purchase
          </p>
        </div>
        <GlassBadge variant="market">100% Escrow Guarded</GlassBadge>
      </div>

      {items.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Items list */}
          <div className="lg:col-span-7 space-y-4">
            <div className="rounded-3xl bg-dark-850/80 border border-white/[0.08] backdrop-blur-2xl p-6 divide-y divide-white/[0.05]">
              {items.map((item) => (
                <div key={item.listing_id} className="py-4 first:pt-0 last:pb-0 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <img
                      src={item.image || "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=200&q=80"}
                      alt=""
                      className="w-16 h-16 rounded-2xl object-cover bg-dark-900 flex-shrink-0"
                    />
                    <div className="space-y-1">
                      <p className="text-sm font-semibold text-white">{item.title}</p>
                      <p className="text-xs text-market-400 font-medium font-sans">
                        {formatTZS(item.price)}
                      </p>
                      <p className="text-[11px] text-zinc-500">Qty: {item.quantity}</p>
                    </div>
                  </div>

                  <button
                    onClick={() => removeFromCart(item.listing_id)}
                    className="p-2 text-zinc-500 hover:text-rose-400 rounded-lg hover:bg-white/[0.04]"
                    title="Remove item"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Checkout & Delivery Details */}
          <div className="lg:col-span-5 space-y-6">
            <form onSubmit={handleCheckout} className="p-6 rounded-3xl bg-dark-850/80 border border-white/[0.09] backdrop-blur-2xl shadow-glass-elevated space-y-5">
              <h3 className="text-base font-semibold text-white">Handover & Delivery</h3>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => setDeliveryMethod("courier")}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    deliveryMethod === "courier"
                      ? "bg-market-500/15 border-market-500/40 text-market-300"
                      : "bg-dark-900 border-white/[0.06] text-zinc-400"
                  }`}
                >
                  <Truck className="w-4 h-4 mb-1" />
                  <p className="font-semibold text-white">Doorstep Courier</p>
                  <p className="text-[10px] text-zinc-500">TSh 15,000</p>
                </button>
                <button
                  type="button"
                  onClick={() => setDeliveryMethod("pickup")}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    deliveryMethod === "pickup"
                      ? "bg-market-500/15 border-market-500/40 text-market-300"
                      : "bg-dark-900 border-white/[0.06] text-zinc-400"
                  }`}
                >
                  <ShieldCheck className="w-4 h-4 mb-1" />
                  <p className="font-semibold text-white">In-Person Handover</p>
                  <p className="text-[10px] text-zinc-500">Free in Dar</p>
                </button>
              </div>

              <div className="space-y-3">
                <GlassInput
                  label="Recipient Full Name *"
                  placeholder="e.g. Samuel M."
                  value={recipientName}
                  onChange={(e) => setRecipientName(e.target.value)}
                  required
                />
                <GlassInput
                  label="Contact Phone (M-Pesa / WhatsApp) *"
                  type="tel"
                  placeholder="+255 755 123 456"
                  value={recipientPhone}
                  onChange={(e) => setRecipientPhone(e.target.value)}
                  required
                />
                {deliveryMethod === "courier" && (
                  <GlassInput
                    label="Delivery Address / Landmark *"
                    placeholder="e.g. Masaki, Chole Road / Kariakoo Market"
                    value={deliveryAddress}
                    onChange={(e) => setDeliveryAddress(e.target.value)}
                    required
                  />
                )}
              </div>

              {/* Order Calculation */}
              <div className="pt-3 border-t border-white/[0.06] space-y-2 text-xs">
                <div className="flex justify-between text-zinc-400">
                  <span>Subtotal</span>
                  <span className="text-white font-medium">{formatTZS(totalPrice)}</span>
                </div>
                <div className="flex justify-between text-zinc-400">
                  <span>Logistics & Courier</span>
                  <span className="text-white font-medium">{formatTZS(deliveryFee)}</span>
                </div>
                <div className="flex justify-between text-zinc-400">
                  <span>Escrow Fee</span>
                  <span className="text-emerald-400 font-medium">Free (Covered by The City)</span>
                </div>
                <div className="flex justify-between text-sm font-bold text-white pt-2 border-t border-white/[0.06]">
                  <span>Total Amount</span>
                  <span className="text-market-400 font-sans text-base">{formatTZS(grandTotal)}</span>
                </div>
              </div>

              <GlassButton
                type="submit"
                variant="market"
                size="lg"
                className="w-full justify-center shadow-green-glow"
              >
                Place Order with Escrow Guard
              </GlassButton>
            </form>
          </div>
        </div>
      ) : (
        <div className="text-center py-20 rounded-3xl bg-dark-850/40 border border-white/[0.06] p-8 space-y-4">
          <ShoppingBag className="w-12 h-12 text-zinc-600 mx-auto" />
          <h2 className="text-xl font-serif text-white">Your Trade Bag is Empty</h2>
          <p className="text-xs text-zinc-400 max-w-sm mx-auto">
            Discover verified flagship electronics, timepieces, and luxury goods in our showroom.
          </p>
          <Link href="/marketplace">
            <GlassButton variant="market" size="md">
              Browse Marketplace
            </GlassButton>
          </Link>
        </div>
      )}
    </div>
  );
}
