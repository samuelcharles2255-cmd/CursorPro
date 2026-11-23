"use client";

import React, { useState, useEffect, use } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Building2,
  MapPin,
  Calendar,
  DollarSign,
  Share2,
  Bookmark,
  ExternalLink,
  CheckCircle2,
  Briefcase,
} from "lucide-react";
import { fetchJobById } from "@/lib/api";
import { Job } from "@/types";
import { formatDate } from "@/lib/utils";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassModal } from "@/components/ui/GlassModal";

interface JobDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function JobDetailPage({ params }: JobDetailPageProps) {
  const { id } = use(params);
  const [job, setJob] = useState<Job | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false);
  const [applicationSubmitted, setApplicationSubmitted] = useState(false);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      const res = await fetchJobById(id);
      if (res) setJob(res);
      setIsLoading(false);
    }
    load();
  }, [id]);

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center text-zinc-400 text-xs">
        Loading position details...
      </div>
    );
  }

  if (!job) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center space-y-4">
        <p className="text-white text-lg">Position not found or expired.</p>
        <Link href="/jobs">
          <GlassButton variant="secondary" size="sm">
            ← Return to Jobs
          </GlassButton>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-zinc-400">
        <Link href="/jobs" className="hover:text-white flex items-center gap-1">
          <ArrowLeft className="w-3.5 h-3.5" />
          Jobs Portal
        </Link>
        <span>/</span>
        <span className="text-zinc-200 truncate">{job.title}</span>
      </div>

      {/* Header Card */}
      <div className="p-8 rounded-3xl bg-dark-850/80 border border-white/[0.09] backdrop-blur-2xl shadow-glass-elevated space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-navy-950/80 border border-navy-700/50 flex items-center justify-center text-navy-300 text-2xl font-bold flex-shrink-0 shadow-navy-glow/20">
              {job.company_name ? job.company_name[0] : "C"}
            </div>
            <div className="space-y-1">
              <h1 className="text-2xl sm:text-3xl font-serif font-medium text-white">
                {job.title}
              </h1>
              <p className="text-xs text-zinc-400 flex items-center gap-2">
                <span className="text-zinc-200 font-medium">{job.company_name}</span>
                <span>·</span>
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-zinc-500" />
                  {job.location || "Dar es Salaam, Tanzania"}
                </span>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsSaved(!isSaved)}
              className={`p-2.5 rounded-xl border transition-all ${
                isSaved
                  ? "bg-navy-900 text-navy-200 border-navy-500 shadow-navy-glow/30"
                  : "bg-white/[0.04] text-zinc-400 hover:text-white border-white/[0.08]"
              }`}
              title="Save Job"
            >
              <Bookmark className="w-4 h-4" />
            </button>
            <GlassButton
              variant="navy"
              size="md"
              onClick={() => setIsApplyModalOpen(true)}
            >
              Apply for Role
            </GlassButton>
          </div>
        </div>

        {/* Info pills */}
        <div className="flex flex-wrap items-center gap-2 pt-4 border-t border-white/[0.06] text-xs">
          <GlassBadge variant="navy">{job.employment_type || "Full-time"}</GlassBadge>
          <span className="px-3 py-1 rounded-full bg-white/[0.04] text-zinc-400 border border-white/[0.06] flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-zinc-500" />
            Posted {formatDate(job.posted_at)}
          </span>
          {job.salary_min && (
            <span className="px-3 py-1 rounded-full bg-navy-950/80 text-navy-200 border border-navy-700/60 font-sans">
              Salary: {job.salary_currency || "TSh"} {Number(job.salary_min).toLocaleString()}
            </span>
          )}
        </div>
      </div>

      {/* Description Content */}
      <div className="p-8 rounded-3xl bg-dark-850/60 border border-white/[0.07] backdrop-blur-xl space-y-6 text-xs sm:text-sm text-zinc-300 leading-relaxed">
        <h2 className="text-lg font-serif text-white">About the Position</h2>
        <div className="whitespace-pre-line space-y-3">
          {job.description || (
            <p>
              This position is indexed directly from the verified corporate career portal. Apply to join a high-performing team advancing key business initiatives in Tanzania and East Africa.
            </p>
          )}
        </div>

        {/* Skills */}
        {job.skills && job.skills.length > 0 && (
          <div className="pt-6 border-t border-white/[0.06] space-y-2">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Required Skills & Competencies
            </h3>
            <div className="flex flex-wrap gap-2">
              {job.skills.map((s) => (
                <span
                  key={s.id}
                  className="px-3 py-1 rounded-lg bg-navy-950/60 text-navy-200 border border-navy-700/50 text-xs"
                >
                  {s.name}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Apply Modal */}
      <GlassModal
        isOpen={isApplyModalOpen}
        onClose={() => setIsApplyModalOpen(false)}
        title={`Apply: ${job.title}`}
        description={`Direct Application to ${job.company_name}`}
      >
        {applicationSubmitted ? (
          <div className="py-6 text-center space-y-3">
            <CheckCircle2 className="w-10 h-10 text-emerald-400 mx-auto" />
            <p className="text-sm font-semibold text-white">Application Recorded</p>
            <p className="text-xs text-zinc-400">
              Your profile credentials and verified contact information have been submitted to {job.company_name}.
            </p>
          </div>
        ) : (
          <div className="space-y-4 pt-2 text-xs">
            <p className="text-zinc-300">
              Applying with your verified The City profile credentials.
            </p>
            <div className="p-4 rounded-xl bg-dark-900 border border-white/[0.06] space-y-2">
              <div className="flex justify-between">
                <span className="text-zinc-500">Candidate:</span>
                <span className="text-white font-medium">Samuel M. (Logged in)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-zinc-500">Contact:</span>
                <span className="text-white">+255 755 123 456</span>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <GlassButton
                variant="ghost"
                size="sm"
                onClick={() => setIsApplyModalOpen(false)}
              >
                Cancel
              </GlassButton>
              <GlassButton
                variant="navy"
                size="sm"
                onClick={() => setApplicationSubmitted(true)}
              >
                Submit Application
              </GlassButton>
            </div>
          </div>
        )}
      </GlassModal>
    </div>
  );
}
