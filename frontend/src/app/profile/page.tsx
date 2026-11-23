"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  User,
  ShieldCheck,
  Phone,
  Mail,
  CheckCircle2,
  Lock,
  Download,
  Sparkles,
  ArrowLeft,
  RefreshCw,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassInput } from "@/components/ui/GlassInput";
import { GlassSidebar } from "@/components/layout/GlassSidebar";

export default function ProfilePage() {
  const { user, isSeller, switchRoleDemo } = useAuth();
  const [name, setName] = useState(user?.name || "Lumina Luxury Tech");
  const [phone, setPhone] = useState(user?.phone_number || "+255 755 123 456");
  const [email, setEmail] = useState(user?.email || "seller@thecity.market");
  const [savedSuccess, setSavedSuccess] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 3000);
  };

  return (
    <div className="flex-1 flex max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 gap-8">
      <GlassSidebar />

      <main className="flex-1 space-y-8 min-w-0 max-w-2xl">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <GlassBadge variant="gold">Account Overview</GlassBadge>
            <span className="text-xs text-zinc-500">Security & Credentials</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-serif font-medium text-white">
            Profile & Trust Settings
          </h1>
          <p className="text-xs text-zinc-400">
            Manage your personal data, verified merchant badge, and security preferences.
          </p>
        </div>

        {savedSuccess && (
          <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4" />
            <span>Profile updates stored securely.</span>
          </div>
        )}

        {/* Role Demo Switcher */}
        <div className="p-5 rounded-2xl bg-dark-850/60 border border-white/[0.08] backdrop-blur-xl flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-white">Active Account Tier</p>
            <p className="text-[11px] text-zinc-400">
              Current Mode: <span className="text-gold-400 font-bold">{isSeller ? "PRO SELLER" : "BUYER / JOB SEEKER"}</span>
            </p>
          </div>
          <GlassButton variant="outline" size="sm" onClick={switchRoleDemo} className="gap-1.5">
            <RefreshCw className="w-3.5 h-3.5" />
            Switch Demo Role
          </GlassButton>
        </div>

        {/* Profile form */}
        <form onSubmit={handleSave} className="p-6 sm:p-8 rounded-3xl bg-dark-850/80 border border-white/[0.09] backdrop-blur-2xl shadow-glass-elevated space-y-5">
          <div className="flex items-center gap-4 pb-4 border-b border-white/[0.06]">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-gold-500/30 to-indigo-500/30 border border-white/[0.1] flex items-center justify-center text-white text-xl font-bold">
              {name ? name[0] : "U"}
            </div>
            <div>
              <p className="text-sm font-semibold text-white">{name}</p>
              <p className="text-xs text-gold-400 flex items-center gap-1 mt-0.5">
                <ShieldCheck className="w-3.5 h-3.5" /> Verified Citizen Identity (Tanzania NIDA)
              </p>
            </div>
          </div>

          <GlassInput
            label="Display or Business Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <GlassInput
            label="Registered Email Address"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <GlassInput
            label="Verified Phone Number (M-Pesa / WhatsApp)"
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
          />

          <div className="pt-2 flex justify-end">
            <GlassButton type="submit" variant="gold" size="md">
              Save Changes
            </GlassButton>
          </div>
        </form>

        {/* Data Protection / PDPA Export */}
        <div className="p-6 rounded-2xl bg-dark-850/40 border border-white/[0.06] flex items-center justify-between text-xs">
          <div>
            <p className="font-semibold text-white">Tanzania PDPA 2022 Data Rights</p>
            <p className="text-[11px] text-zinc-400">Download a full machine-readable archive of your account transactions.</p>
          </div>
          <GlassButton variant="ghost" size="sm" className="gap-1.5 text-zinc-300">
            <Download className="w-3.5 h-3.5" />
            Export Data
          </GlassButton>
        </div>
      </main>
    </div>
  );
}
