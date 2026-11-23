"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Eye,
  ArrowLeft,
  FileCheck,
  UserCheck,
  Lock,
  Filter,
} from "lucide-react";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassCard } from "@/components/ui/GlassCard";
import { GlassSidebar } from "@/components/layout/GlassSidebar";
import { formatTZS } from "@/lib/utils";

interface PendingItem {
  id: number;
  title: string;
  category: string;
  seller: string;
  sellerRating: string;
  price: number;
  submittedAt: string;
  riskScore: "LOW" | "MEDIUM" | "HIGH";
  flagReason?: string;
  status: "PENDING" | "APPROVED" | "REJECTED";
}

const INITIAL_QUEUE: PendingItem[] = [
  {
    id: 101,
    title: "Rolex Daytona Cosmograph 18k Rose Gold (Ref. 116505)",
    category: "Luxury & Fashion",
    seller: "Lumina Luxury Tech",
    sellerRating: "4.98 (PRO)",
    price: 94000000,
    submittedAt: "12 mins ago",
    riskScore: "LOW",
    status: "PENDING",
  },
  {
    id: 102,
    title: "Toyota Land Cruiser Prado TX-L 2022 (Dark Grey)",
    category: "Vehicles & Automotive",
    seller: "Swahili Motors Dar",
    sellerRating: "4.85",
    price: 185000000,
    submittedAt: "34 mins ago",
    riskScore: "LOW",
    status: "PENDING",
  },
  {
    id: 103,
    title: "DJI Inspire 3 Cinema Drone 8K Bundle",
    category: "Electronics & Gadgets",
    seller: "Dar Aerials Co.",
    sellerRating: "New Seller",
    price: 32000000,
    submittedAt: "1 hour ago",
    riskScore: "MEDIUM",
    flagReason: "High ticket item submitted by newly created seller profile.",
    status: "PENDING",
  },
];

export default function ModerationPage() {
  const [queue, setQueue] = useState<PendingItem[]>(INITIAL_QUEUE);
  const [activeTab, setActiveTab] = useState<"pending" | "verifications" | "reports">("pending");
  const [notification, setNotification] = useState<string | null>(null);

  const handleApprove = (id: number) => {
    setQueue(
      queue.map((item) => (item.id === id ? { ...item, status: "APPROVED" } : item))
    );
    setNotification("Listing verified and approved to live marketplace feeds.");
    setTimeout(() => setNotification(null), 3000);
  };

  const handleReject = (id: number) => {
    setQueue(
      queue.map((item) => (item.id === id ? { ...item, status: "REJECTED" } : item))
    );
    setNotification("Listing rejected. Notification dispatched to seller with remediation criteria.");
    setTimeout(() => setNotification(null), 3000);
  };

  return (
    <div className="flex-1 flex max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 gap-8">
      <GlassSidebar />

      <main className="flex-1 space-y-8 min-w-0">
        {/* Toast */}
        {notification && (
          <div className="fixed top-20 right-6 z-50 p-4 rounded-xl bg-market-600 text-dark-950 font-semibold shadow-green-glow flex items-center gap-2 text-xs">
            <CheckCircle2 className="w-4 h-4" />
            <span>{notification}</span>
          </div>
        )}

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <GlassBadge variant="navy">Admin Authority Desk</GlassBadge>
              <span className="text-xs text-zinc-500">Integrity & Quality Gate</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-serif font-medium text-white">
              Marketplace Moderation & Trust
            </h1>
            <p className="text-xs sm:text-sm text-zinc-400">
              Ensure luxury standards, inspect high-value serials, and approve verified merchant tiers.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <GlassBadge variant="market" size="md">
              <Lock className="w-3.5 h-3.5" /> Staff Escrow Officer
            </GlassBadge>
          </div>
        </div>

        {/* 3 Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <GlassCard variant="default" className="p-5 space-y-1">
            <span className="text-xs text-zinc-400">Pending Review Queue</span>
            <p className="text-2xl font-bold font-sans text-white">
              {queue.filter((i) => i.status === "PENDING").length} Items
            </p>
            <p className="text-[11px] text-market-400">Target review window: &lt; 30 mins</p>
          </GlassCard>

          <GlassCard variant="default" className="p-5 space-y-1">
            <span className="text-xs text-zinc-400">Merchant Verifications</span>
            <p className="text-2xl font-bold font-sans text-emerald-400">4 Pending</p>
            <p className="text-[11px] text-zinc-400">BRELA business registrations</p>
          </GlassCard>

          <GlassCard variant="default" className="p-5 space-y-1">
            <span className="text-xs text-zinc-400">Platform Trust Rating</span>
            <p className="text-2xl font-bold font-sans text-white">99.8%</p>
            <p className="text-[11px] text-emerald-400">Zero escrow fraud incidents</p>
          </GlassCard>
        </div>

        {/* Moderation Queue Table */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-serif text-white">Listing Inspection Queue</h2>
            <span className="text-xs text-zinc-500">Real-time submissions</span>
          </div>

          <div className="rounded-3xl bg-dark-850/80 border border-white/[0.08] backdrop-blur-xl overflow-hidden shadow-glass">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-dark-900/80 border-b border-white/[0.06] text-zinc-400 uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="py-3.5 px-4">Item Details</th>
                    <th className="py-3.5 px-4">Declared Value</th>
                    <th className="py-3.5 px-4">Seller & Standing</th>
                    <th className="py-3.5 px-4">Risk Level</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4 text-right">Moderator Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.04] text-zinc-300">
                  {queue.map((item) => (
                    <tr key={item.id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="py-3.5 px-4">
                        <p className="font-semibold text-white">{item.title}</p>
                        <p className="text-[11px] text-zinc-500">{item.category}</p>
                        {item.flagReason && (
                          <p className="text-[10px] text-amber-400 flex items-center gap-1 mt-1">
                            <AlertTriangle className="w-3 h-3" />
                            {item.flagReason}
                          </p>
                        )}
                      </td>
                      <td className="py-3.5 px-4 font-sans font-semibold text-market-400">
                        {formatTZS(item.price)}
                      </td>
                      <td className="py-3.5 px-4">
                        <p className="text-white font-medium">{item.seller}</p>
                        <p className="text-[11px] text-zinc-500">{item.sellerRating}</p>
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                            item.riskScore === "LOW"
                              ? "bg-emerald-500/10 text-emerald-400"
                              : "bg-amber-500/10 text-amber-400"
                          }`}
                        >
                          {item.riskScore}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                            item.status === "APPROVED"
                              ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                              : item.status === "REJECTED"
                              ? "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                              : "bg-amber-500/10 text-amber-300"
                          }`}
                        >
                          {item.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        {item.status === "PENDING" ? (
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleApprove(item.id)}
                              className="px-3 py-1.5 rounded-xl bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center gap-1 transition-colors"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              Approve
                            </button>
                            <button
                              onClick={() => handleReject(item.id)}
                              className="px-3 py-1.5 rounded-xl bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 text-rose-300 text-xs font-semibold flex items-center gap-1 transition-colors"
                            >
                              <XCircle className="w-3.5 h-3.5" />
                              Reject
                            </button>
                          </div>
                        ) : (
                          <span className="text-[11px] text-zinc-500 italic">Resolved</span>
                        )}
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
