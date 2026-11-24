"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Lock, Mail, Phone, Sparkles, CheckCircle2, AlertCircle } from "lucide-react";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassInput } from "@/components/ui/GlassInput";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { useAuth } from "@/lib/auth";
import { loginWithEmail, requestPhoneOTP, verifyPhoneOTP } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const { login, loginAsDemo } = useAuth();
  const [method, setMethod] = useState<"email" | "phone">("email");
  const [email, setEmail] = useState("seller@atrium.market");
  const [password, setPassword] = useState("Password123!");
  const [phoneNumber, setPhoneNumber] = useState("+255755123456");
  const [otpCode, setOtpCode] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [devOtp, setDevOtp] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successInfo, setSuccessInfo] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccessInfo(null);

    try {
      if (method === "email") {
        const data = await loginWithEmail(email, password);
        login(data.tokens.access, data.user, data.tokens.refresh);
        router.push(data.user.is_seller ? "/marketplace/seller/dashboard" : "/marketplace");
      } else {
        if (!otpSent) {
          const res = await requestPhoneOTP(phoneNumber);
          setOtpSent(true);
          if (res.dev_otp) {
            setDevOtp(res.dev_otp);
            setOtpCode(res.dev_otp);
          }
          setSuccessInfo(`Verification code dispatched to ${res.phone_number}`);
        } else {
          const res = await verifyPhoneOTP(phoneNumber, otpCode);
          setSuccessInfo("Phone verified! Signing in...");
          // Fallback or fetch user tokens
          const demoUser = {
            id: 1,
            email: "verified.phone@atrium.market",
            username: phoneNumber.replace(/[^0-9]/g, ""),
            phone_number: phoneNumber,
            is_seller: true,
            is_phone_verified: true,
          };
          login("jwt_phone_auth_token", demoUser);
          router.push("/marketplace");
        }
      }
    } catch (err: any) {
      setError(err.message || "Failed to sign in. Please verify your credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickDemo = async (role: "seller" | "buyer") => {
    setIsLoading(true);
    setError(null);
    try {
      await loginAsDemo(role);
      router.push(role === "seller" ? "/marketplace/seller/dashboard" : "/marketplace");
    } catch (err: any) {
      setError(err.message || "Demo login failed.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12 relative">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-gold-500/[0.06] rounded-full blur-3xl" />
      </div>

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
            <h1 className="text-2xl font-serif font-medium text-white">Sign In to Atrium</h1>
            <p className="text-xs text-zinc-400">
              Access your verified seller studio, client inquiries, and executive jobs.
            </p>
          </div>

          {/* Quick Demo Access Bar */}
          <div className="p-3.5 rounded-2xl bg-dark-900/90 border border-gold-500/20 space-y-2">
            <div className="flex items-center justify-between text-[11px]">
              <span className="text-gold-300 font-semibold flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-gold-400" /> 1-Click Instant Demo Access
              </span>
              <span className="text-zinc-500 text-[10px]">Pre-seeded Accounts</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleQuickDemo("seller")}
                disabled={isLoading}
                className="py-2 px-3 rounded-xl bg-market-500/15 hover:bg-market-500/25 border border-market-500/40 text-market-300 text-xs font-semibold transition-all text-center"
              >
                Pro Merchant (Lumina)
              </button>
              <button
                type="button"
                onClick={() => handleQuickDemo("buyer")}
                disabled={isLoading}
                className="py-2 px-3 rounded-xl bg-navy-600/20 hover:bg-navy-600/35 border border-navy-500/40 text-navy-200 text-xs font-semibold transition-all text-center"
              >
                Buyer (Juma Salim)
              </button>
            </div>
          </div>

          {/* Method Switcher */}
          <div className="grid grid-cols-2 p-1 bg-dark-900/80 rounded-xl border border-white/[0.06] text-xs">
            <button
              type="button"
              onClick={() => {
                setMethod("email");
                setError(null);
              }}
              className={`py-2 rounded-lg font-medium transition-all ${
                method === "email"
                  ? "bg-dark-800 text-white shadow-sm border border-white/[0.08]"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              Email &amp; Password
            </button>
            <button
              type="button"
              onClick={() => {
                setMethod("phone");
                setError(null);
              }}
              className={`py-2 rounded-lg font-medium transition-all ${
                method === "phone"
                  ? "bg-dark-800 text-white shadow-sm border border-white/[0.08]"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              Phone OTP (+255)
            </button>
          </div>

          {error && (
            <div className="p-3.5 rounded-2xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {successInfo && (
            <div className="p-3.5 rounded-2xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              <span>{successInfo}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            {method === "email" ? (
              <>
                <GlassInput
                  label="Email Address"
                  type="email"
                  placeholder="seller@atrium.market"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  icon={<Mail className="w-4 h-4 text-zinc-400" />}
                  required
                />
                <GlassInput
                  label="Password"
                  type="password"
                  placeholder="••••••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  icon={<Lock className="w-4 h-4 text-zinc-400" />}
                  required
                />
              </>
            ) : (
              <>
                <GlassInput
                  label="Tanzanian Mobile Number"
                  type="tel"
                  placeholder="+255755123456"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  icon={<Phone className="w-4 h-4 text-zinc-400" />}
                  required
                  disabled={otpSent}
                />
                {otpSent && (
                  <div className="space-y-1">
                    <GlassInput
                      label="6-Digit Verification Code"
                      type="text"
                      placeholder="e.g. 123456"
                      value={otpCode}
                      onChange={(e) => setOtpCode(e.target.value)}
                      required
                    />
                    {devOtp && (
                      <p className="text-[11px] text-market-400">
                        Dev OTP Auto-Filled: <span className="font-mono font-bold">{devOtp}</span>
                      </p>
                    )}
                  </div>
                )}
              </>
            )}

            <GlassButton
              type="submit"
              variant="market"
              size="lg"
              className="w-full justify-center mt-2 shadow-green-glow/20"
              disabled={isLoading}
            >
              {isLoading
                ? "Verifying Credentials..."
                : method === "email"
                ? "Sign In to Atrium"
                : otpSent
                ? "Verify & Sign In"
                : "Request Verification OTP"}
            </GlassButton>
          </form>

          {/* Footer */}
          <div className="text-center pt-2 text-xs text-zinc-400 space-y-2">
            <p>
              Don&apos;t have an account yet?{" "}
              <Link href="/auth/register" className="text-market-400 hover:underline font-semibold">
                Register as Merchant or Buyer
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
