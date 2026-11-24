"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Briefcase,
  Bookmark,
  Clock,
  CheckCircle2,
  ChevronRight,
  ArrowLeft,
  Building2,
  MapPin,
  Calendar,
  ExternalLink,
  ShieldCheck,
  AlertCircle,
  Sparkles,
} from "lucide-react";
import { fetchJobApplications, fetchSavedJobs } from "@/lib/api";
import { JobApplication, SavedJob } from "@/types";
import { formatDate } from "@/lib/utils";
import { useAuth } from "@/lib/auth";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassSidebar } from "@/components/layout/GlassSidebar";

export default function ApplicationsPage() {
  const { user, token, loginAsDemo } = useAuth();
  const [tab, setTab] = useState<"applied" | "saved">("applied");
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [savedJobs, setSavedJobs] = useState<SavedJob[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      let activeToken = token;
      if (!activeToken) {
        try {
          await loginAsDemo("buyer");
          activeToken = localStorage.getItem("atrium_token");
        } catch (e) {
          console.warn("Auto demo login error:", e);
        }
      }

      if (activeToken) {
        try {
          const [appsData, savedData] = await Promise.all([
            fetchJobApplications(activeToken),
            fetchSavedJobs(activeToken),
          ]);
          setApplications(appsData);
          setSavedJobs(savedData);
        } catch (err) {
          console.warn("Failed to load application history:", err);
        }
      }
      setIsLoading(false);
    }

    loadData();
  }, [token]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "INTERVIEW_SCHEDULED":
        return {
          label: "Interview Scheduled",
          className: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
        };
      case "UNDER_REVIEW":
        return {
          label: "Under Review",
          className: "bg-gold-500/15 text-gold-300 border-gold-500/30",
        };
      case "OFFERED":
        return {
          label: "Offer Extended",
          className: "bg-emerald-400/20 text-emerald-300 border-emerald-400/50 font-bold",
        };
      case "REJECTED":
        return {
          label: "Not Selected",
          className: "bg-zinc-800 text-zinc-400 border-zinc-700",
        };
      case "SUBMITTED":
      default:
        return {
          label: "Application Received",
          className: "bg-navy-500/15 text-navy-300 border-navy-500/30",
        };
    }
  };

  return (
    <div className="flex-1 flex max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 gap-8">
      <GlassSidebar />

      <main className="flex-1 space-y-6 min-w-0 max-w-4xl">
        {/* Header */}
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <GlassBadge variant="navy">Talent Pipeline</GlassBadge>
            <span className="text-xs text-zinc-500">Candidate Ledger</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-white tracking-tight">
            Career Applications &amp; Saved Roles
          </h1>
          <p className="text-xs sm:text-sm text-zinc-400">
            Real-time status tracking for direct enterprise submissions across Tanzania and East Africa.
          </p>
        </div>

        {/* Custom Segmented Tabs */}
        <div className="flex items-center gap-3 border-b border-white/[0.08] pb-3 text-xs">
          <button
            onClick={() => setTab("applied")}
            className={`pb-2 px-3 rounded-lg transition-all font-medium flex items-center gap-2 ${
              tab === "applied"
                ? "bg-navy-900/80 text-navy-200 border border-navy-500/50 shadow-navy-glow/20"
                : "text-zinc-400 hover:text-white hover:bg-white/[0.04]"
            }`}
          >
            <Briefcase className="w-3.5 h-3.5" />
            <span>Submitted Applications ({applications.length})</span>
          </button>
          <button
            onClick={() => setTab("saved")}
            className={`pb-2 px-3 rounded-lg transition-all font-medium flex items-center gap-2 ${
              tab === "saved"
                ? "bg-navy-900/80 text-navy-200 border border-navy-500/50 shadow-navy-glow/20"
                : "text-zinc-400 hover:text-white hover:bg-white/[0.04]"
            }`}
          >
            <Bookmark className="w-3.5 h-3.5" />
            <span>Bookmarked Roles ({savedJobs.length})</span>
          </button>
        </div>

        {/* Content Section */}
        {isLoading ? (
          <div className="py-20 text-center space-y-3">
            <div className="w-8 h-8 rounded-full border-2 border-navy-500 border-t-transparent animate-spin mx-auto" />
            <p className="text-zinc-400 text-xs">Querying application registry...</p>
          </div>
        ) : tab === "applied" ? (
          applications.length > 0 ? (
            <div className="space-y-3">
              {applications.map((app) => {
                const badge = getStatusBadge(app.status);
                return (
                  <div
                    key={app.id}
                    className="p-5 rounded-2xl bg-dark-850/80 border border-white/[0.08] backdrop-blur-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-white/[0.15] transition-all shadow-glass"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-semibold text-white">{app.job_title}</p>
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold border ${badge.className}`}>
                          {badge.label}
                        </span>
                      </div>
                      <p className="text-xs text-zinc-400 flex items-center gap-2">
                        <span className="text-zinc-300 font-medium">{app.company_name}</span>
                        <span>·</span>
                        <span>{app.location || "Dar es Salaam"}</span>
                      </p>
                      <p className="text-[11px] text-zinc-500">
                        Submitted on {formatDate(app.created_at)}
                      </p>
                    </div>

                    <div className="flex items-center gap-2">
                      <Link href={`/jobs/${app.job}`}>
                        <GlassButton variant="navy" size="sm">
                          View Role Details →
                        </GlassButton>
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="py-16 text-center rounded-3xl bg-dark-900/50 border border-white/[0.06] p-8 space-y-3">
              <Briefcase className="w-10 h-10 text-zinc-600 mx-auto" />
              <h3 className="text-base font-serif text-white">No Active Applications</h3>
              <p className="text-xs text-zinc-400 max-w-sm mx-auto">
                Explore 840+ verified corporate roles and apply directly with your Atrium profile credentials.
              </p>
              <div className="pt-2">
                <Link href="/jobs">
                  <GlassButton variant="navy" size="sm">
                    Browse Executive Roles
                  </GlassButton>
                </Link>
              </div>
            </div>
          )
        ) : (
          savedJobs.length > 0 ? (
            <div className="space-y-3">
              {savedJobs.map((saved) => (
                <div
                  key={saved.id}
                  className="p-5 rounded-2xl bg-dark-850/80 border border-white/[0.08] backdrop-blur-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:border-white/[0.15] transition-all shadow-glass"
                >
                  <div className="space-y-1">
                    <p className="text-sm font-semibold text-white">
                      {saved.job_details?.title || `Position #${saved.job}`}
                    </p>
                    <p className="text-xs text-zinc-400">
                      {saved.job_details?.company_name || "Enterprise Employer"} · {saved.job_details?.location || "Tanzania"}
                    </p>
                    <p className="text-[11px] text-zinc-500">
                      Saved on {formatDate(saved.created_at)}
                    </p>
                  </div>

                  <Link href={`/jobs/${saved.job}`}>
                    <GlassButton variant="navy" size="sm">
                      Apply Now →
                    </GlassButton>
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-16 text-center rounded-3xl bg-dark-900/50 border border-white/[0.06] p-8 space-y-3">
              <Bookmark className="w-10 h-10 text-zinc-600 mx-auto" />
              <h3 className="text-base font-serif text-white">No Bookmarked Roles</h3>
              <p className="text-xs text-zinc-400 max-w-sm mx-auto">
                Save interesting positions while browsing to review and apply when ready.
              </p>
              <div className="pt-2">
                <Link href="/jobs">
                  <GlassButton variant="navy" size="sm">
                    Explore Opportunities
                  </GlassButton>
                </Link>
              </div>
            </div>
          )
        )}
      </main>
    </div>
  );
}
