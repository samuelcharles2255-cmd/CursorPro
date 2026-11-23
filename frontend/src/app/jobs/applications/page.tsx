"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Briefcase, Bookmark, Clock, CheckCircle2, ChevronRight, ArrowLeft } from "lucide-react";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassSidebar } from "@/components/layout/GlassSidebar";

export default function ApplicationsPage() {
  const [tab, setTab] = useState<"applied" | "saved">("applied");

  const mockApplications = [
    {
      id: 1,
      title: "Senior Full Stack Engineer (Python & Next.js)",
      company: "CRDB Bank Technology Hub",
      location: "Dar es Salaam",
      appliedDate: "Nov 20, 2026",
      status: "INTERVIEW SCHEDULED",
      statusColor: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    },
    {
      id: 2,
      title: "Head of Digital Operations",
      company: "Vodacom Tanzania PLC",
      location: "Dar es Salaam",
      appliedDate: "Nov 15, 2026",
      status: "UNDER REVIEW",
      statusColor: "bg-gold-500/15 text-gold-300 border-gold-500/30",
    },
  ];

  return (
    <div className="flex-1 flex max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 gap-8">
      <GlassSidebar />

      <main className="flex-1 space-y-6 min-w-0">
        <div>
          <h1 className="text-2xl font-serif text-white">Career Applications & Saved Roles</h1>
          <p className="text-xs text-zinc-400">
            Track interview milestones, recruiter responses, and bookmarked opportunities.
          </p>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-2 border-b border-white/[0.08] pb-3 text-xs">
          <button
            onClick={() => setTab("applied")}
            className={`pb-2 px-1 relative transition-colors ${
              tab === "applied" ? "text-navy-300 font-semibold" : "text-zinc-400 hover:text-white"
            }`}
          >
            Submitted Applications ({mockApplications.length})
            {tab === "applied" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-navy-500 shadow-navy-glow" />
            )}
          </button>
          <button
            onClick={() => setTab("saved")}
            className={`pb-2 px-1 relative transition-colors ${
              tab === "saved" ? "text-navy-300 font-semibold" : "text-zinc-400 hover:text-white"
            }`}
          >
            Saved Roles (4)
            {tab === "saved" && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-navy-500 shadow-navy-glow" />
            )}
          </button>
        </div>

        {/* List */}
        <div className="space-y-3">
          {mockApplications.map((app) => (
            <div
              key={app.id}
              className="p-5 rounded-2xl bg-dark-850/70 border border-white/[0.08] backdrop-blur-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-white/[0.15] transition-all"
            >
              <div className="space-y-1">
                <p className="text-sm font-semibold text-white">{app.title}</p>
                <p className="text-xs text-zinc-400">{app.company} · {app.location}</p>
                <p className="text-[11px] text-zinc-500">Submitted {app.appliedDate}</p>
              </div>

              <div className="flex items-center gap-3">
                <span className={`px-2.5 py-1 rounded-full text-[10px] font-semibold border ${app.statusColor}`}>
                  {app.status}
                </span>
                <Link href="/jobs">
                  <GlassButton variant="ghost" size="sm">
                    View Details
                  </GlassButton>
                </Link>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
