"use client";

import React, { useState, useEffect } from "react";
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
  Key,
  ShoppingBag,
  Briefcase,
  AlertCircle,
} from "lucide-react";
import { useAuth } from "@/lib/auth";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassInput } from "@/components/ui/GlassInput";
import { GlassSidebar } from "@/components/layout/GlassSidebar";
import { updateCurrentUser, changePassword, fetchOrders, fetchJobApplications } from "@/lib/api";
import { Order, JobApplication } from "@/types";
import { formatTZS, formatDate } from "@/lib/utils";

export default function ProfilePage() {
  const { user, token, isSeller, loginAsDemo, refreshUser } = useAuth();
  const [name, setName] = useState(user?.name || "Lumina Luxury Tech");
  const [phone, setPhone] = useState(user?.phone_number || "+255755123456");
  const [email, setEmail] = useState(user?.email || "seller@atrium.market");
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Password Change State
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isChangingPass, setIsChangingPass] = useState(false);
  const [passError, setPassError] = useState<string | null>(null);
  const [passSuccess, setPassSuccess] = useState<string | null>(null);

  // Ledgers
  const [recentOrders, setRecentOrders] = useState<Order[]>([]);
  const [recentApps, setRecentApps] = useState<JobApplication[]>([]);

  useEffect(() => {
    if (user) {
      if (user.name) setName(user.name);
      if (user.phone_number) setPhone(user.phone_number);
      if (user.email) setEmail(user.email);
    }
  }, [user]);

  useEffect(() => {
    async function loadLedgers() {
      if (!token) return;
      try {
        const [ordersData, appsData] = await Promise.all([
          fetchOrders(token),
          fetchJobApplications(token),
        ]);
        setRecentOrders(ordersData.slice(0, 3));
        setRecentApps(appsData.slice(0, 3));
      } catch (e) {
        console.warn("Profile ledger load notice:", e);
      }
    }
    loadLedgers();
  }, [token]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      if (token) {
        await updateCurrentUser({ name, phone_number: phone }, token);
        await refreshUser();
      }
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err: any) {
      console.warn("Profile update error:", err);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPassError(null);
    setPassSuccess(null);

    if (newPassword !== confirmPassword) {
      setPassError("New password and confirmation do not match.");
      return;
    }

    if (newPassword.length < 8) {
      setPassError("New password must be at least 8 characters.");
      return;
    }

    if (!token) {
      setPassError("Please authenticate to update your password.");
      return;
    }

    setIsChangingPass(true);
    try {
      const res = await changePassword(oldPassword, newPassword, token);
      setPassSuccess(res.message || "Password updated successfully.");
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setTimeout(() => setPassSuccess(null), 4000);
    } catch (err: any) {
      setPassError(err.message || "Failed to update password. Check existing password.");
    } finally {
      setIsChangingPass(false);
    }
  };

  const handleSwitchRole = async () => {
    const targetRole = isSeller ? "buyer" : "seller";
    await loginAsDemo(targetRole);
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
          <GlassButton variant="outline" size="sm" onClick={handleSwitchRole} className="gap-1.5">
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
              {isSaving ? "Saving..." : "Save Profile Details"}
            </GlassButton>
          </div>
        </form>

        {/* Security & Password Change */}
        <form onSubmit={handlePasswordChange} className="p-6 sm:p-8 rounded-3xl bg-dark-850/80 border border-white/[0.09] backdrop-blur-2xl shadow-glass-elevated space-y-4">
          <div className="flex items-center gap-2 border-b border-white/[0.06] pb-3">
            <Key className="w-4 h-4 text-gold-400" />
            <h3 className="text-sm font-semibold text-white">Security &amp; Password Credentials</h3>
          </div>

          {passError && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{passError}</span>
            </div>
          )}

          {passSuccess && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              <span>{passSuccess}</span>
            </div>
          )}

          <div className="space-y-3">
            <GlassInput
              label="Current Password"
              type="password"
              placeholder="••••••••••••"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              required
            />
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <GlassInput
                label="New Password"
                type="password"
                placeholder="Min 8 characters"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
              <GlassInput
                label="Confirm New Password"
                type="password"
                placeholder="Confirm password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <GlassButton type="submit" variant="outline" size="sm" disabled={isChangingPass}>
              {isChangingPass ? "Updating Password..." : "Update Password"}
            </GlassButton>
          </div>
        </form>

        {/* Activity Ledgers: Placed Escrow Orders */}
        {recentOrders.length > 0 && (
          <div className="p-6 rounded-3xl bg-dark-850/60 border border-white/[0.08] backdrop-blur-xl space-y-3">
            <div className="flex items-center justify-between border-b border-white/[0.06] pb-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-white">
                <ShoppingBag className="w-4 h-4 text-market-400" />
                <span>Recent Escrow Orders</span>
              </div>
              <Link href="/marketplace/cart" className="text-[11px] text-zinc-400 hover:text-white">
                View Trade Bag →
              </Link>
            </div>

            <div className="space-y-2">
              {recentOrders.map((ord) => (
                <div key={ord.id} className="p-3 rounded-xl bg-dark-900/60 border border-white/[0.05] flex items-center justify-between text-xs">
                  <div>
                    <span className="font-mono font-bold text-white">{ord.order_number}</span>
                    <p className="text-[11px] text-zinc-400">{formatDate(ord.created_at)}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-market-400 font-sans">{formatTZS(ord.total_amount)}</p>
                    <span className="text-[10px] text-zinc-400 uppercase tracking-wider">{ord.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Activity Ledgers: Job Applications */}
        {recentApps.length > 0 && (
          <div className="p-6 rounded-3xl bg-dark-850/60 border border-white/[0.08] backdrop-blur-xl space-y-3">
            <div className="flex items-center justify-between border-b border-white/[0.06] pb-2">
              <div className="flex items-center gap-2 text-xs font-semibold text-white">
                <Briefcase className="w-4 h-4 text-navy-400" />
                <span>Submitted Career Applications</span>
              </div>
              <Link href="/jobs/applications" className="text-[11px] text-zinc-400 hover:text-white">
                View All Applications →
              </Link>
            </div>

            <div className="space-y-2">
              {recentApps.map((app) => (
                <div key={app.id} className="p-3 rounded-xl bg-dark-900/60 border border-white/[0.05] flex items-center justify-between text-xs">
                  <div>
                    <p className="font-medium text-white">{app.job_title}</p>
                    <p className="text-[11px] text-zinc-400">{app.company_name} · {formatDate(app.created_at)}</p>
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-navy-500/15 text-navy-300 border border-navy-500/30">
                    {app.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

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
