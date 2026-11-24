"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Lock, Mail, Phone, User as UserIcon, ShoppingBag, Briefcase, CheckCircle2, AlertCircle } from "lucide-react";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassInput } from "@/components/ui/GlassInput";
import { useAuth } from "@/lib/auth";
import { registerUser } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [role, setRole] = useState<"seller" | "buyer" | "jobseeker">("seller");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("+255");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const data = await registerUser({
        email,
        username: email.split("@")[0].replace(/[^a-zA-Z0-9_]/g, "_") || "user",
        name,
        phone_number: phoneNumber,
        password,
        role: role === "seller" ? "seller" : "buyer",
      });

      login(data.tokens.access, data.user, data.tokens.refresh);
      router.push(role === "seller" ? "/marketplace/create-listing" : "/marketplace");
    } catch (err: any) {
      setError(err.message || "Failed to create account. Please check your information.");
    } finally {
      setIsLoading(false);
    }
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
              AT
            </div>
            <h1 className="text-2xl font-serif font-medium text-white">Join Atrium</h1>
            <p className="text-xs text-zinc-400">
              Create your account to trade fine goods or discover executive careers.
            </p>
          </div>

          {/* Account Role Selector */}
          <div className="grid grid-cols-3 gap-2">
            {[
              { id: "seller", label: "Merchant", icon: ShoppingBag },
              { id: "buyer", label: "Buyer", icon: UserIcon },
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
                      ? "bg-market-500/15 border-market-500/40 text-market-300 shadow-green-glow/10"
                      : "bg-dark-900 border-white/[0.06] text-zinc-400 hover:text-white"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{r.label}</span>
                </button>
              );
            })}
          </div>

          {error && (
            <div className="p-3.5 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-4">
            <GlassInput
              label="Full Name or Business Name"
              type="text"
              placeholder="e.g. Sarah Mwangi or Lumina Tech"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <GlassInput
              label="Email Address"
              type="email"
              placeholder="sarah@example.co.tz"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              icon={<Mail className="w-4 h-4 text-zinc-400" />}
              required
            />
            <GlassInput
              label="Tanzanian Phone Number"
              type="tel"
              placeholder="+255712345678"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              icon={<Phone className="w-4 h-4 text-zinc-400" />}
              required
            />
            <GlassInput
              label="Password (min 8 chars)"
              type="password"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              icon={<Lock className="w-4 h-4 text-zinc-400" />}
              required
            />

            <GlassButton
              type="submit"
              variant="market"
              size="lg"
              className="w-full justify-center mt-2 shadow-green-glow/20"
              disabled={isLoading}
            >
              {isLoading ? "Creating Account..." : "Create Account"}
            </GlassButton>
          </form>

          <div className="text-center pt-2 text-xs text-zinc-400">
            Already have an account?{" "}
            <Link href="/auth/login" className="text-market-400 hover:underline font-semibold">
              Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
