"use client";

import React, { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ShoppingBag,
  Briefcase,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  TrendingUp,
  MapPin,
  Lock,
  Phone,
  Sparkles,
  Users,
  Building2,
  Zap,
  Star,
  ChevronRight,
  Truck,
  DollarSign,
  HelpCircle,
  FileCheck,
  Layers,
  ArrowUpRight,
  MessageSquare,
  Search,
} from "lucide-react";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassCard } from "@/components/ui/GlassCard";
import { SafeImage } from "@/components/ui/SafeImage";

export default function MarketingLandingPage() {
  const [activeTab, setActiveTab] = useState<"both" | "marketplace" | "jobs">("both");
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  const stats = [
    { label: "Live Verified Jobs", value: "770+", sub: "Indexed across East Africa", branch: "jobs" },
    { label: "Active Trade Merchants", value: "10,200+", sub: "Verified sellers & creators", branch: "market" },
    { label: "Escrow Volume Guarded", value: "TSh 2.4B+", sub: "100% dispute-free fulfillment", branch: "market" },
    { label: "Platform Trust Score", value: "99.8%", sub: "BRELA & KYC verified", branch: "jobs" },
  ];

  const faqs = [
    {
      q: "What is The City and how does the dual platform work?",
      a: "The City is a next-generation super-platform designed specifically for East Africa. It pairs a premium Peer-to-Peer Escrow Marketplace (for buying and selling electronics, vehicles, fashion, and luxury goods safely) with the Jobs Engine (indexing 770+ real-time verified positions from leading banks, telcos, and multinational companies). One single login gives you full access to both worlds.",
    },
    {
      q: "How does the Marketplace Escrow guarantee 100% protection?",
      a: "When a buyer pays for an item, their money is locked in our secure The City Escrow vault. The seller dispatches the item via verified doorstep courier or meets at a safe public zone in Dar es Salaam (such as Masaki or City Centre). Only after the buyer physically inspects and approves the item are the funds released to the seller's M-Pesa, Tigo Pesa, or Bank account.",
    },
    {
      q: "How are the 770+ jobs kept up-to-date?",
      a: "Our automated crawlers continuously index career portals across Tanzania and the EAC region, cross-referencing company credentials and application deadlines. Expired roles are culled automatically, ensuring you only spend time applying for open, legitimate opportunities.",
    },
    {
      q: "Is there any cost to register, create a listing, or apply for jobs?",
      a: "Registering and applying for jobs is completely free for all candidates forever. Standard peer-to-peer sellers can also list products for free. Pro merchants who want verified business badges and promoted showroom placement enjoy low, transparent fees only upon successful escrow payout.",
    },
    {
      q: "Can I contact sellers directly on WhatsApp before buying?",
      a: "Yes! Every verified listing features an instant 1-Click WhatsApp Direct Chat button with the seller's registered phone, as well as an encrypted In-App messaging interface for negotiation and counter-offers.",
    },
  ];

  return (
    <div className="min-h-screen bg-dark-950 text-zinc-100 overflow-hidden pb-24 selection:bg-market-500 selection:text-dark-950">
      {/* Background Ambient Glows */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-market-500/10 rounded-full blur-[140px] -translate-y-1/2" />
        <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-navy-600/15 rounded-full blur-[140px]" />
        <div className="absolute bottom-10 left-1/3 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[150px]" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 sm:pt-14 space-y-20 sm:space-y-32">
        {/* ========================================================= */}
        {/* 1. HERO SECTION: DUAL ENGINE VALUE PROPOSITION             */}
        {/* ========================================================= */}
        <section className="text-center space-y-8 max-w-4xl mx-auto pt-4">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/[0.05] border border-white/[0.12] backdrop-blur-xl text-xs font-medium text-zinc-300"
          >
            <Sparkles className="w-3.5 h-3.5 text-market-400" />
            <span>The Unified Super-Platform for East Africa</span>
            <span className="w-1.5 h-1.5 rounded-full bg-navy-400" />
            <span className="text-navy-300 font-semibold">Jobs &amp; Commerce</span>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="space-y-4"
          >
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-sans font-bold tracking-tight text-white leading-[1.08]">
              One Ecosystem. <br />
              <span className="bg-gradient-to-r from-market-400 via-emerald-300 to-teal-400 bg-clip-text text-transparent">
                Trusted Marketplace.
              </span>{" "}
              <br className="hidden sm:inline" />
              <span className="bg-gradient-to-r from-blue-400 via-navy-300 to-indigo-300 bg-clip-text text-transparent">
                Elite Careers.
              </span>
            </h1>

            <p className="text-base sm:text-lg text-zinc-300 max-w-2xl mx-auto leading-relaxed">
              Experience the dual power of Tanzania&apos;s cleanest peer-to-peer escrow marketplace alongside 
              the region&apos;s leading career portal indexing over 770+ active verified opportunities.
            </p>
          </motion.div>

          {/* Dual Action CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-2"
          >
            {/* Marketplace CTA: Emerald Green */}
            <Link href="/marketplace" className="w-full sm:w-auto">
              <GlassButton
                variant="market"
                size="lg"
                className="w-full sm:w-auto min-h-[52px] px-8 text-sm gap-2.5 shadow-green-glow"
              >
                <ShoppingBag className="w-4 h-4" />
                Explore Marketplace (Biashara)
                <ArrowRight className="w-4 h-4" />
              </GlassButton>
            </Link>

            {/* Jobs CTA: Navy Blue */}
            <Link href="/jobs" className="w-full sm:w-auto">
              <GlassButton
                variant="navy"
                size="lg"
                className="w-full sm:w-auto min-h-[52px] px-8 text-sm gap-2.5 shadow-navy-glow"
              >
                <Briefcase className="w-4 h-4 text-blue-300" />
                Browse 770+ Jobs
                <ArrowRight className="w-4 h-4" />
              </GlassButton>
            </Link>

            {/* Overview Discovery CTA */}
            <Link href="/" className="w-full sm:w-auto">
              <GlassButton
                variant="secondary"
                size="lg"
                className="w-full sm:w-auto min-h-[52px] px-6 text-sm"
              >
                <Layers className="w-4 h-4 text-zinc-400" />
                Live Feed Mockup
              </GlassButton>
            </Link>
          </motion.div>

          {/* Floating Trust Metric Strip */}
          <motion.div
            initial={{ opacity: 0, y: 25 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 pt-6"
          >
            {stats.map((s, idx) => (
              <div
                key={idx}
                className="p-4 sm:p-5 rounded-2xl bg-dark-900/70 border border-white/[0.08] backdrop-blur-xl text-left space-y-1 hover:border-white/[0.18] transition-all"
              >
                <span
                  className={`text-2xl sm:text-3xl font-bold font-sans ${
                    s.branch === "market" ? "text-market-400" : "text-blue-400"
                  }`}
                >
                  {s.value}
                </span>
                <p className="text-xs font-semibold text-white truncate">{s.label}</p>
                <p className="text-[11px] text-zinc-500 truncate">{s.sub}</p>
              </div>
            ))}
          </motion.div>
        </section>

        {/* ========================================================= */}
        {/* 2. THE DUAL SHOWCASE: TWO HUBS SIDE-BY-SIDE                */}
        {/* ========================================================= */}
        <section className="space-y-12">
          <div className="text-center space-y-3 max-w-2xl mx-auto">
            <h2 className="text-3xl sm:text-4xl font-sans font-bold text-white tracking-tight">
              Two Integrated Worlds. One Seamless Experience.
            </h2>
            <p className="text-xs sm:text-sm text-zinc-400">
              Switch freely between high-value verified trade and accelerated career advancement with 
              dedicated tools designed for safety, speed, and trust.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch">
            {/* ---------------------------------------------------- */}
            {/* HUB A: MARKETPLACE SHOWCASE (EMERALD GREEN THEME)   */}
            {/* ---------------------------------------------------- */}
            <div className="rounded-3xl bg-dark-900/80 border border-market-500/30 p-6 sm:p-8 flex flex-col justify-between space-y-8 relative overflow-hidden backdrop-blur-2xl shadow-green-glow/10 group">
              <div className="absolute top-0 right-0 w-80 h-80 bg-market-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />

              <div className="space-y-6 relative z-10">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-10 h-10 rounded-2xl bg-market-500/20 text-market-400 flex items-center justify-center font-bold text-lg border border-market-500/30">
                      <ShoppingBag className="w-5 h-5" />
                    </span>
                    <div>
                      <h3 className="text-xl sm:text-2xl font-bold text-white font-sans">
                        Marketplace Branch
                      </h3>
                      <p className="text-xs text-market-400 font-semibold">
                        Peer-to-Peer Commerce &amp; Escrow
                      </p>
                    </div>
                  </div>
                  <GlassBadge variant="market">Verified Hub</GlassBadge>
                </div>

                <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed">
                  Tanzania&apos;s luxury and high-ticket peer-to-peer trading floor. Buy verified electronics, 
                  vehicles, horology, and business inventory with locked escrow guarantees.
                </p>

                {/* Feature Bullet Points */}
                <div className="space-y-3 text-xs">
                  {[
                    {
                      title: "100% Escrow Protection Vault",
                      desc: "Seller is paid only after you inspect the physical goods in person or via doorstep courier.",
                    },
                    {
                      title: "1-Click WhatsApp & In-App Bargaining",
                      desc: "Send instant counter-offers or chat directly with the seller on verified phone numbers.",
                    },
                    {
                      title: "Airy, High-Contrast P2P Feeds",
                      desc: "Clean white feed cards with explicit specs, transparent TZS pricing, and condition tags.",
                    },
                    {
                      title: "Doorstep Delivery & Safe Pickup",
                      desc: "Express logistics across Dar es Salaam, Arusha, Mwanza, and upcountry hubs.",
                    },
                  ].map((feat, i) => (
                    <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-dark-950/60 border border-white/[0.05]">
                      <CheckCircle2 className="w-4 h-4 text-market-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-semibold text-white">{feat.title}</p>
                        <p className="text-zinc-400 text-[11px]">{feat.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sample Product Showcase Card */}
              <div className="p-4 rounded-2xl bg-white text-dark-950 shadow-glass border border-slate-200 space-y-3 relative z-10">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold uppercase tracking-wider">
                    Featured Listing
                  </span>
                  <span className="text-slate-500 font-medium">Masaki, Dar es Salaam</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-16 h-16 rounded-xl bg-slate-100 overflow-hidden flex-shrink-0 relative">
                    <SafeImage
                      src="https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=300&q=80"
                      alt="MacBook Pro"
                      aspectRatio="aspect-square"
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="min-w-0 flex-1">
                    <h4 className="text-xs font-bold text-slate-900 truncate">
                      MacBook Pro 16&quot; M3 Max (36GB / 1TB)
                    </h4>
                    <p className="text-sm font-black text-market-600 font-sans">
                      TSh 7,850,000
                    </p>
                    <p className="text-[10px] text-slate-500">Condition: Like New · Escrow Guarded</p>
                  </div>
                </div>
                <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[11px] text-slate-600">Merchant: Lumina Tech (99.8%)</span>
                  <Link
                    href="/marketplace/listing/macbook-pro-16-m3-max-dar"
                    className="inline-flex items-center gap-1 text-xs font-bold text-market-700 hover:text-market-800"
                  >
                    View Item <ArrowUpRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>

              <div className="pt-2 relative z-10">
                <Link href="/marketplace" className="w-full block">
                  <GlassButton variant="market" size="md" className="w-full justify-center">
                    Enter Marketplace Showroom →
                  </GlassButton>
                </Link>
              </div>
            </div>

            {/* ---------------------------------------------------- */}
            {/* HUB B: CAREER PORTAL SHOWCASE (NAVY BLUE THEME)     */}
            {/* ---------------------------------------------------- */}
            <div className="rounded-3xl bg-dark-900/80 border border-navy-500/40 p-6 sm:p-8 flex flex-col justify-between space-y-8 relative overflow-hidden backdrop-blur-2xl shadow-navy-glow/10 group">
              <div className="absolute top-0 right-0 w-80 h-80 bg-navy-600/15 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />

              <div className="space-y-6 relative z-10">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-10 h-10 rounded-2xl bg-navy-950/80 text-blue-300 flex items-center justify-center font-bold text-lg border border-navy-700/60">
                      <Briefcase className="w-5 h-5 text-blue-400" />
                    </span>
                    <div>
                      <h3 className="text-xl sm:text-2xl font-bold text-white font-sans">
                        Jobs
                      </h3>
                      <p className="text-xs text-blue-400 font-semibold">
                        770+ Verified Corporate Roles
                      </p>
                    </div>
                  </div>
                  <GlassBadge variant="navy">Live Opportunities</GlassBadge>
                </div>

                <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed">
                  East Africa&apos;s premier professional career engine. Continuously indexing confirmed openings 
                  at commercial banks, telecom leaders, fast-growing tech hubs, and international NGOs.
                </p>

                {/* Feature Bullet Points */}
                <div className="space-y-3 text-xs">
                  {[
                    {
                      title: "770+ Real-Time Crawled Positions",
                      desc: "Direct integration with career portals across Tanzania and the East African Community.",
                    },
                    {
                      title: "Salary Transparency & Full Benefits",
                      desc: "Visible compensation packages and benchmarked salary scales in TSh and USD.",
                    },
                    {
                      title: "1-Click Verified Profile Application",
                      desc: "Submit your pre-verified credentials directly to corporate hiring managers.",
                    },
                    {
                      title: "Milestone Application Tracker",
                      desc: "Follow your application from Submission to Interview Scheduled in real-time.",
                    },
                  ].map((feat, i) => (
                    <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-dark-950/60 border border-white/[0.05]">
                      <CheckCircle2 className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-semibold text-white">{feat.title}</p>
                        <p className="text-zinc-400 text-[11px]">{feat.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Sample Job Showcase Card */}
              <div className="p-4 rounded-2xl bg-navy-950/90 text-white shadow-glass border border-navy-800/80 space-y-3 relative z-10">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30 font-bold uppercase tracking-wider">
                    Full-Time Position
                  </span>
                  <span className="text-zinc-400 font-medium">Dar es Salaam, HQ</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-14 h-14 rounded-xl bg-navy-900 border border-navy-700/60 flex items-center justify-center text-blue-400 font-bold text-xl flex-shrink-0">
                    C
                  </div>
                  <div className="min-w-0 flex-1">
                    <h4 className="text-xs font-bold text-white truncate">
                      Senior Full-Stack Engineer (Python / Next.js)
                    </h4>
                    <p className="text-xs text-blue-300 font-medium">CRDB Bank Technology Hub</p>
                    <p className="text-[11px] text-emerald-400 font-sans font-bold">
                      TSh 6,500,000 - 8,500,000 / mo
                    </p>
                  </div>
                </div>
                <div className="pt-2 border-t border-navy-800/60 flex items-center justify-between">
                  <span className="text-[11px] text-zinc-400">Applications close in 5 days</span>
                  <Link
                    href="/jobs"
                    className="inline-flex items-center gap-1 text-xs font-bold text-blue-300 hover:text-white"
                  >
                    Quick Apply <ArrowUpRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>

              <div className="pt-2 relative z-10">
                <Link href="/jobs" className="w-full block">
                  <GlassButton variant="navy" size="md" className="w-full justify-center">
                    Browse All 770+ Positions →
                  </GlassButton>
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* ========================================================= */}
        {/* 3. HOW ESCROW WORKS: THE 4-STEP SAFETY PROTOCOL           */}
        {/* ========================================================= */}
        <section className="space-y-12 rounded-3xl bg-dark-900/50 border border-white/[0.08] p-6 sm:p-12 backdrop-blur-xl">
          <div className="text-center space-y-3 max-w-2xl mx-auto">
            <GlassBadge variant="market">Buyer &amp; Seller Protection</GlassBadge>
            <h2 className="text-3xl sm:text-4xl font-sans font-bold text-white tracking-tight">
              How The City Escrow Protocol Works
            </h2>
            <p className="text-xs sm:text-sm text-zinc-400">
              Eliminating fraud, non-delivery, and stolen merchandise from East African peer-to-peer commerce.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                step: "01",
                title: "Deposit to Escrow Vault",
                desc: "Buyer initiates purchase. Funds are locked securely in our audited escrow vault via M-Pesa, Tigo Pesa, or Bank.",
                icon: Lock,
                color: "text-market-400",
              },
              {
                step: "02",
                title: "Tracked Handover / Courier",
                desc: "Merchant dispatches via tracked doorstep logistics or coordinates an in-person inspection at a verified safe zone.",
                icon: Truck,
                color: "text-blue-400",
              },
              {
                step: "03",
                title: "Physical Inspection",
                desc: "Buyer inspects hardware condition, IMEI/serial authenticity, and accessories before confirming satisfaction.",
                icon: ShieldCheck,
                color: "text-emerald-400",
              },
              {
                step: "04",
                title: "Instant Payout to Merchant",
                desc: "Once confirmed, escrow automatically releases funds directly to the merchant without delay or hidden deductions.",
                icon: CheckCircle2,
                color: "text-market-400",
              },
            ].map((st, idx) => (
              <div
                key={idx}
                className="p-6 rounded-2xl bg-dark-950/70 border border-white/[0.07] space-y-3 relative hover:border-white/[0.18] transition-all"
              >
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-black font-mono text-zinc-600">{st.step}</span>
                  <st.icon className={`w-5 h-5 ${st.color}`} />
                </div>
                <h3 className="text-sm font-bold text-white">{st.title}</h3>
                <p className="text-xs text-zinc-400 leading-relaxed">{st.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ========================================================= */}
        {/* 4. REAL REVIEWS & TRUST TESTIMONIALS                     */}
        {/* ========================================================= */}
        <section className="space-y-12">
          <div className="text-center space-y-3 max-w-2xl mx-auto">
            <h2 className="text-3xl sm:text-4xl font-sans font-bold text-white tracking-tight">
              Trusted by Merchants &amp; Professionals
            </h2>
            <p className="text-xs sm:text-sm text-zinc-400">
              See how thousands in Dar es Salaam and across East Africa use The City every day.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                quote:
                  "I sold over 18 MacBooks and high-end mirrorless cameras this month alone. Buyers in Masaki and Arusha feel completely safe paying through escrow.",
                name: "Hamza M. Bakari",
                role: "Pro Tech Merchant · Kariakoo & Masaki",
                badge: "Marketplace Pro",
                branch: "market",
              },
              {
                quote:
                  "I was tired of expired job postings on old portals. The City helped me find the Senior Full Stack role at CRDB Bank with transparent salary brackets.",
                name: "Diana K. Mwamba",
                role: "Software Engineer · CRDB Tech Hub",
                badge: "Hired via Jobs",
                branch: "jobs",
              },
              {
                quote:
                  "The clean interface and zero clutter make it feel like Linear or Raycast. It is the most professional digital ecosystem in Tanzania today.",
                name: "Kelvin S. Chalamila",
                role: "Product Strategist & Investor",
                badge: "Power User",
                branch: "both",
              },
            ].map((t, idx) => (
              <div
                key={idx}
                className="p-6 rounded-3xl bg-dark-900/70 border border-white/[0.08] backdrop-blur-xl flex flex-col justify-between space-y-4 hover:border-white/[0.18] transition-all"
              >
                <div className="space-y-3">
                  <div className="flex items-center gap-1 text-amber-400">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 fill-amber-400" />
                    ))}
                  </div>
                  <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed italic">
                    &ldquo;{t.quote}&rdquo;
                  </p>
                </div>
                <div className="pt-3 border-t border-white/[0.06] flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold text-white">{t.name}</p>
                    <p className="text-[11px] text-zinc-500">{t.role}</p>
                  </div>
                  <GlassBadge variant={t.branch === "market" ? "market" : "navy"} size="sm">
                    {t.badge}
                  </GlassBadge>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ========================================================= */}
        {/* 5. FREQUENTLY ASKED QUESTIONS (ACCORDION)                 */}
        {/* ========================================================= */}
        <section className="space-y-8 max-w-3xl mx-auto">
          <div className="text-center space-y-2">
            <h2 className="text-2xl sm:text-3xl font-sans font-bold text-white tracking-tight">
              Frequently Asked Questions
            </h2>
            <p className="text-xs text-zinc-400">
              Everything you need to know about navigating The City platform.
            </p>
          </div>

          <div className="space-y-3">
            {faqs.map((faq, idx) => {
              const isOpen = openFaq === idx;
              return (
                <div
                  key={idx}
                  className="rounded-2xl bg-dark-900/80 border border-white/[0.07] overflow-hidden transition-all"
                >
                  <button
                    onClick={() => setOpenFaq(isOpen ? null : idx)}
                    className="w-full p-4 sm:p-5 text-left flex items-center justify-between gap-4 text-xs sm:text-sm font-semibold text-white hover:text-zinc-200"
                  >
                    <span>{faq.q}</span>
                    <ChevronRight
                      className={`w-4 h-4 text-zinc-500 transition-transform ${
                        isOpen ? "rotate-90 text-market-400" : ""
                      }`}
                    />
                  </button>
                  <AnimatePresence>
                    {isOpen && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                      >
                        <div className="p-4 sm:p-5 pt-0 text-xs text-zinc-300 leading-relaxed border-t border-white/[0.04]">
                          {faq.a}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>
        </section>

        {/* ========================================================= */}
        {/* 6. GRAND CTA ANCHOR                                       */}
        {/* ========================================================= */}
        <section className="rounded-3xl bg-gradient-to-b from-dark-850 to-dark-900 border border-white/[0.1] p-8 sm:p-14 text-center space-y-8 relative overflow-hidden shadow-glass-elevated">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-market-500/10 via-navy-600/10 to-transparent pointer-events-none" />

          <div className="space-y-4 max-w-2xl mx-auto relative z-10">
            <h2 className="text-3xl sm:text-5xl font-sans font-bold text-white tracking-tight leading-tight">
              Ready to Step into the Future of East African Commerce?
            </h2>
            <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed">
              Join thousands of verified merchants, eager buyers, and top corporate professionals today.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 relative z-10">
            <Link href="/marketplace" className="w-full sm:w-auto">
              <GlassButton
                variant="market"
                size="lg"
                className="w-full sm:w-auto min-h-[50px] px-8 text-sm gap-2 shadow-green-glow"
              >
                <ShoppingBag className="w-4 h-4" />
                Launch Marketplace
              </GlassButton>
            </Link>

            <Link href="/jobs" className="w-full sm:w-auto">
              <GlassButton
                variant="navy"
                size="lg"
                className="w-full sm:w-auto min-h-[50px] px-8 text-sm gap-2 shadow-navy-glow"
              >
                <Briefcase className="w-4 h-4 text-blue-300" />
                Explore 770+ Jobs
              </GlassButton>
            </Link>

            <Link href="/auth/register" className="w-full sm:w-auto">
              <GlassButton
                variant="secondary"
                size="lg"
                className="w-full sm:w-auto min-h-[50px] px-6 text-sm"
              >
                Create Free Account
              </GlassButton>
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}