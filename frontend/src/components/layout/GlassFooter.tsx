import React from "react";
import Link from "next/link";
import { ShieldCheck, Truck, Lock, ArrowUpRight } from "lucide-react";

export function GlassFooter() {
  return (
    <footer className="w-full border-t border-white/[0.08] bg-dark-950/80 backdrop-blur-xl mt-20 relative z-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        {/* Trust Badges Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pb-12 border-b border-white/[0.06]">
          <div className="flex items-center gap-3.5">
            <div className="p-2.5 rounded-xl bg-gold-500/10 border border-gold-500/20 text-gold-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-semibold text-white">Inspected & Verified Escrow</p>
              <p className="text-[11px] text-zinc-400">Funds released only upon safe handover.</p>
            </div>
          </div>
          <div className="flex items-center gap-3.5">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Truck className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-semibold text-white">Same-Day Dar es Salaam Delivery</p>
              <p className="text-[11px] text-zinc-400">Kariakoo, Masaki, Mikocheni & upcountry express.</p>
            </div>
          </div>
          <div className="flex items-center gap-3.5">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Lock className="w-5 h-5" />
            </div>
            <div>
              <p className="text-xs font-semibold text-white">Tanzania PDPA 2022 Compliant</p>
              <p className="text-[11px] text-zinc-400">Strict buyer & seller personal data encryption.</p>
            </div>
          </div>
        </div>

        {/* Links Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 pt-12">
          <div>
            <span className="text-xs font-semibold tracking-wider uppercase text-zinc-400 mb-4 block">
              Marketplace
            </span>
            <ul className="space-y-2.5 text-xs text-zinc-400">
              <li>
                <Link href="/marketplace" className="hover:text-market-300 transition-colors">
                  Featured Collections
                </Link>
              </li>
              <li>
                <Link href="/marketplace/category/electronics" className="hover:text-market-300 transition-colors">
                  Electronics & Tech
                </Link>
              </li>
              <li>
                <Link href="/marketplace/category/luxury-fashion" className="hover:text-market-300 transition-colors">
                  Timepieces & Luxury
                </Link>
              </li>
              <li>
                <Link href="/marketplace/category/automotive" className="hover:text-market-300 transition-colors">
                  Prestige Vehicles
                </Link>
              </li>
              <li>
                <Link href="/marketplace/create-listing" className="text-market-400 hover:underline flex items-center gap-1 font-medium">
                  Start Selling <ArrowUpRight className="w-3 h-3" />
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <span className="text-xs font-semibold tracking-wider uppercase text-zinc-400 mb-4 block">
              Careers & Jobs
            </span>
            <ul className="space-y-2.5 text-xs text-zinc-400">
              <li>
                <Link href="/jobs" className="hover:text-white transition-colors">
                  Search All Openings
                </Link>
              </li>
              <li>
                <Link href="/jobs?type=Full-time" className="hover:text-white transition-colors">
                  Executive Full-time Roles
                </Link>
              </li>
              <li>
                <Link href="/jobs?type=Remote" className="hover:text-white transition-colors">
                  Remote Engineering & Design
                </Link>
              </li>
              <li>
                <Link href="/jobs/applications" className="hover:text-white transition-colors">
                  Track Applications
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <span className="text-xs font-semibold tracking-wider uppercase text-zinc-400 mb-4 block">
              Platform & Trust
            </span>
            <ul className="space-y-2.5 text-xs text-zinc-400">
              <li>
                <Link href="/landing" className="text-market-400 font-semibold hover:underline flex items-center gap-1">
                  Platform Showcase &amp; Story <ArrowUpRight className="w-3 h-3" />
                </Link>
              </li>
              <li>
                <Link href="/marketplace/moderation" className="hover:text-white transition-colors">
                  Trust & Moderation Desk
                </Link>
              </li>
              <li>
                <Link href="/profile" className="hover:text-white transition-colors">
                  Identity Verification
                </Link>
              </li>
              <li>
                <span className="text-zinc-500 cursor-default">Escrow & Disputes</span>
              </li>
              <li>
                <span className="text-zinc-500 cursor-default">Privacy Policy (PDPA)</span>
              </li>
            </ul>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="w-7 h-7 rounded-lg bg-market-500/20 border border-market-500/30 flex items-center justify-center font-serif font-bold text-market-400 text-xs">
                TC
              </div>
              <span className="font-serif font-bold tracking-wider text-sm text-white">THE CITY</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed mb-4">
              The high-conviction ecosystem uniting executive career opportunities with a verified fine trade marketplace across Tanzania and East Africa.
            </p>
            <div className="flex items-center gap-2 text-[11px] text-zinc-500 font-mono">
              <span>TZS (TSh)</span> · <span>Swahili &amp; English</span>
            </div>
          </div>
        </div>

        {/* Bottom copyright */}
        <div className="mt-12 pt-6 border-t border-white/[0.05] flex flex-col sm:flex-row items-center justify-between text-xs text-zinc-500 gap-4">
          <p>© {new Date().getFullYear()} The City Technologies Ltd. All rights reserved.</p>
          <p className="text-zinc-400 font-medium">Crafted with Quiet Luxury &amp; High Conviction.</p>
        </div>
      </div>
    </footer>
  );
}
