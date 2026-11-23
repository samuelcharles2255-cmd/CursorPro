"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Lock, Mail, Phone, User, ShoppingBag, Briefcase, CheckCircle2 } from "lucide-react";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassInput } from "@/components/ui/GlassInput";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [role, setRole] = useState<"seller" | "buyer" | "jobseeker">("seller");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("+255");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiBase}/api/auth/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          username: email.split("@")[0] || "user",
          name,
          phone_number: phoneNumber,
          password,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        login(data.tokens?.access || "jwt_sample", data.user);
        router.push(role === "seller" ? "/marketplace/create-listing" : "/marketplace");
        return;
      }
    } catch (e) {
      console.warn("Register API fallback:", e);
    }

    login("jwt_sample", {
      id: Date.now(),
      email,
      username: email.split("@")[0] || "user",
      name,
      phone_number: phoneNumber,
      is_seller: role === "seller",
    });
    router.push(role === "seller" ? "/marketplace/create-listing" : "/marketplace");
    setIsLoading(false);
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12 relative">
      <div className="relative w-full max-w-md space-y-6">
        <Link
          href="/"
          className="text-xs text-zinc-400 hover:text-white inline-flex items-center gap-1.5 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to Overview
        </Link>

        <div className="rounded-3xl bg-dark-850/80 border border-white/[0.1] p-8 backdrop-blur-2xl shadow-glass-elevated space-y-6">
          <div className="text-center space-y-2">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-market-500/20 via-dark-850 to-navy-600/30 border border-market-400/30 flex items-center justify-center text-white font-bold text-sm mx-auto shadow-green-glow/20 tracking-wider">
              TC
            </div>
            <h1 className="text-2xl font-serif font-medium text-white">Join The City</h1>
            <p className="text-xs text-zinc-400">
              Create your account to trade luxury goods or discover executive careers.
            </p>
          </div>

          {/* Account Role Selector */}
          <div className="grid grid-cols-3 gap-2">
            {[
              { id: "seller", label: "Merchant", icon: ShoppingBag },
              { id: "buyer", label: "Buyer", icon: User },
              { id: "jobseeker", label: "Job Seeker", icon: Briefcase },
            ].map((r) => {
              const Icon = r.icon;
              return (
                <button
                  key={r.id}
                  type="button"
                  onClick={() => setRole(r.id as any)}
                  className={`p-3 rounded-xl border flex flex-col items-center gap-1.5 text-xs font-medium transition-all ${
                    role === r.id
                      ? "bg-gold-500/15 border-gold-500/40 text-gold-300 shadow-gold-glow/10"
                      : "bg-dark-900 border-white/[0.06] text-zinc-400 hover:text-white"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{r.label}</span>
                </button>
              );
            })}
          </div>

          <form onSubmit={handleRegister} className="space-y-4">
            <GlassInput
              label="Full Name or Business Name *"
              placeholder="e.g. Lumina Tech or Samuel J."
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <GlassInput
              label="Email Address *"
              type="email"
              placeholder="you@domain.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <GlassInput
              label="Phone Number (WhatsApp verified) *"
              type="tel"
              placeholder="+255 755 123 456"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              required
            />
            <GlassInput
              label="Create Password *"
              type="password"
              placeholder="At least 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <GlassButton
              type="submit"
              variant="gold"
              size="lg"
              className="w-full justify-center mt-2 shadow-gold-glow"
              isLoading={isLoading}
            >
              Complete Registration
            </GlassButton>
          </form>

          <div className="pt-4 border-t border-white/[0.06] text-center text-xs text-zinc-400">
            Already registered?{" "}
            <Link href="/auth/login" className="text-gold-400 hover:underline font-medium">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
