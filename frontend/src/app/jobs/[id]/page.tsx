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
  ShieldCheck,
  Send,
  Sparkles,
  Lock,
  Globe,
  Clock,
  ChevronRight,
  AlertCircle,
} from "lucide-react";
import { fetchJobById, applyForJob, toggleSaveJob } from "@/lib/api";
import { Job } from "@/types";
import { formatDate } from "@/lib/utils";
import { useAuth } from "@/lib/auth";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassInput } from "@/components/ui/GlassInput";
import { GlassModal } from "@/components/ui/GlassModal";

interface JobDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function JobDetailPage({ params }: JobDetailPageProps) {
  const { id } = use(params);
  const { user, token, loginAsDemo } = useAuth();
  const [job, setJob] = useState<Job | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  // Application Modal & Form State
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false);
  const [applicantName, setApplicantName] = useState("");
  const [applicantEmail, setApplicantEmail] = useState("");
  const [applicantPhone, setApplicantPhone] = useState("");
  const [coverNote, setCoverNote] = useState("");
  const [isSubmittingApp, setIsSubmittingApp] = useState(false);
  const [appError, setAppError] = useState<string | null>(null);
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

  useEffect(() => {
    if (user) {
      if (user.name) setApplicantName(user.name);
      if (user.email) setApplicantEmail(user.email);
      if (user.phone_number) setApplicantPhone(user.phone_number);
    }
  }, [user]);

  const handleToggleSave = async () => {
    let activeToken = token;
    if (!activeToken) {
      try {
        await loginAsDemo("buyer");
        activeToken = localStorage.getItem("atrium_token");
      } catch (e) {
        console.warn("Auto demo login error:", e);
      }
    }

    if (!activeToken || !job) return;

    try {
      const res = await toggleSaveJob(Number(job.id), activeToken);
      setIsSaved(res.saved);
      setSaveMessage(res.message);
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (err: any) {
      console.warn("Save job error:", err);
      setIsSaved(!isSaved);
    }
  };

  const handleApplySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!job) return;

    setIsSubmittingApp(true);
    setAppError(null);

    let activeToken = token;
    if (!activeToken) {
      try {
        await loginAsDemo("buyer");
        activeToken = localStorage.getItem("atrium_token");
      } catch (e) {
        console.warn("Auto demo login error:", e);
      }
    }

    if (!activeToken) {
      setAppError("Please sign in to submit your verified application.");
      setIsSubmittingApp(false);
      return;
    }

    try {
      await applyForJob(
        Number(job.id),
        {
          full_name: applicantName || user?.name || "Verified Candidate",
          email: applicantEmail || user?.email || "candidate@atrium.market",
          phone: applicantPhone || user?.phone_number || "+255755123456",
          cover_letter: coverNote,
        },
        activeToken
      );
      setApplicationSubmitted(true);
    } catch (err: any) {
      setAppError(err.message || "Failed to submit application. Please check form fields.");
    } finally {
      setIsSubmittingApp(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-24 text-center space-y-3">
        <div className="w-8 h-8 rounded-full border-2 border-navy-500 border-t-transparent animate-spin mx-auto" />
        <p className="text-zinc-400 text-xs">Loading verified position intelligence...</p>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center space-y-4">
        <p className="text-white text-lg font-serif">Position not found or expired.</p>
        <Link href="/jobs">
          <GlassButton variant="secondary" size="sm">
            ← Return to Jobs Portal
          </GlassButton>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Editorial Breadcrumb */}
      <div className="flex items-center justify-between text-xs text-zinc-400 border-b border-white/[0.06] pb-4">
        <div className="flex items-center gap-2">
          <Link href="/jobs" className="hover:text-white flex items-center gap-1 transition-colors">
            <ArrowLeft className="w-3.5 h-3.5" />
            Executive Careers
          </Link>
          <span>/</span>
          <span className="text-zinc-500">{job.company_name || "Enterprise"}</span>
          <span>/</span>
          <span className="text-zinc-200 truncate max-w-[200px] sm:max-w-md font-medium">
            {job.title}
          </span>
        </div>

        {saveMessage && (
          <span className="text-[11px] text-navy-300 font-medium animate-fade-in">
            {saveMessage}
          </span>
        )}
      </div>

      {/* Main Grid: Asymmetric 2-Column Dossier */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Role Intelligence & Specifications (7 Cols) */}
        <div className="lg:col-span-8 space-y-6">
          {/* Header Card */}
          <div className="p-6 sm:p-8 rounded-3xl bg-dark-900/90 border border-white/[0.09] backdrop-blur-2xl shadow-glass-elevated space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-6">
              <div className="flex items-start gap-4">
                <div className="w-16 h-16 rounded-2xl bg-navy-950/90 border border-navy-700/60 flex items-center justify-center text-navy-300 text-2xl font-bold flex-shrink-0 shadow-navy-glow/20">
                  {job.company_name ? job.company_name[0] : "C"}
                </div>
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-navy-500/20 text-navy-300 border border-navy-500/40">
                      Verified Enterprise
                    </span>
                    <span className="text-xs text-zinc-400">·</span>
                    <span className="text-xs text-zinc-400 flex items-center gap-1">
                      <Clock className="w-3 h-3 text-zinc-500" />
                      Posted {formatDate(job.posted_at)}
                    </span>
                  </div>

                  <h1 className="text-2xl sm:text-3xl font-serif font-bold text-white tracking-tight leading-tight">
                    {job.title}
                  </h1>

                  <p className="text-xs sm:text-sm text-zinc-300 flex items-center gap-2 pt-0.5">
                    <span className="font-semibold text-white">{job.company_name}</span>
                    <span>·</span>
                    <span className="flex items-center gap-1 text-zinc-400">
                      <MapPin className="w-3.5 h-3.5 text-navy-400" />
                      {job.location || "Dar es Salaam, Tanzania"}
                    </span>
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 flex-shrink-0">
                <button
                  onClick={handleToggleSave}
                  className={`p-2.5 rounded-xl border transition-all ${
                    isSaved
                      ? "bg-navy-900 text-navy-200 border-navy-500 shadow-navy-glow/40"
                      : "bg-white/[0.04] text-zinc-400 hover:text-white border-white/[0.08]"
                  }`}
                  title={isSaved ? "Saved to career bookmarks" : "Save job"}
                >
                  <Bookmark className={`w-4 h-4 ${isSaved ? "fill-navy-400" : ""}`} />
                </button>
                <GlassButton
                  variant="navy"
                  size="md"
                  onClick={() => setIsApplyModalOpen(true)}
                  className="shadow-navy-glow"
                >
                  Apply Directly
                </GlassButton>
              </div>
            </div>

            {/* Structured Metric Ribbon */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-white/[0.06] text-xs">
              <div className="p-3 rounded-2xl bg-dark-850/60 border border-white/[0.05]">
                <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-medium">Work Arrangement</p>
                <p className="text-white font-semibold mt-0.5">{job.employment_type || "Full-Time"}</p>
              </div>
              <div className="p-3 rounded-2xl bg-dark-850/60 border border-white/[0.05]">
                <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-medium">Target Location</p>
                <p className="text-white font-semibold mt-0.5 truncate">{job.location || "Dar es Salaam"}</p>
              </div>
              <div className="p-3 rounded-2xl bg-dark-850/60 border border-white/[0.05]">
                <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-medium">Compensation Tier</p>
                <p className="text-navy-300 font-semibold mt-0.5 font-sans truncate">
                  {job.salary_min ? `${job.salary_currency || "TSh"} ${Number(job.salary_min).toLocaleString()}` : "Market Benchmark"}
                </p>
              </div>
              <div className="p-3 rounded-2xl bg-dark-850/60 border border-white/[0.05]">
                <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-medium">Security & Trust</p>
                <p className="text-emerald-400 font-semibold mt-0.5 flex items-center gap-1">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  BRELA Verified
                </p>
              </div>
            </div>
          </div>

          {/* Detailed Job Narrative */}
          <div className="p-6 sm:p-8 rounded-3xl bg-dark-900/70 border border-white/[0.08] backdrop-blur-xl space-y-6 text-xs sm:text-sm text-zinc-300 leading-relaxed">
            <div className="flex items-center justify-between border-b border-white/[0.06] pb-3">
              <h2 className="text-base sm:text-lg font-serif font-bold text-white">
                Position Overview &amp; Mandate
              </h2>
              <span className="text-[11px] text-zinc-500">Corporate Portal Feed</span>
            </div>

            <div className="whitespace-pre-line space-y-4 text-zinc-300">
              {job.description || (
                <p>
                  This executive position is actively recruiting verified candidates through the corporate talent acquisition pipeline in Tanzania and East Africa. Apply with your verified profile to be scheduled for preliminary screening.
                </p>
              )}
            </div>

            {/* Competency & Skill Tags */}
            {job.skills && job.skills.length > 0 && (
              <div className="pt-6 border-t border-white/[0.06] space-y-3">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                  Required Competencies &amp; Technical Stacks
                </h3>
                <div className="flex flex-wrap gap-2">
                  {job.skills.map((s) => (
                    <span
                      key={s.id}
                      className="px-3 py-1 rounded-xl bg-navy-950/80 text-navy-200 border border-navy-700/50 text-xs font-medium"
                    >
                      {s.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Fast Application Dossier & Enterprise Intel (4 Cols) */}
        <div className="lg:col-span-4 space-y-6">
          {/* Fast Direct Application Card */}
          <div className="p-6 rounded-3xl bg-gradient-to-b from-navy-950/80 to-dark-900/90 border border-navy-700/50 backdrop-blur-2xl shadow-glass-elevated space-y-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-navy-400" />
              <h3 className="text-sm font-semibold text-white">Direct Executive Pipeline</h3>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Skip third-party agencies. Your application lands directly on the verified talent acquisition portal of {job.company_name}.
            </p>

            <div className="pt-2 space-y-2">
              <GlassButton
                variant="navy"
                size="md"
                onClick={() => setIsApplyModalOpen(true)}
                className="w-full justify-center shadow-navy-glow"
              >
                Submit Application
              </GlassButton>

              {job.application_url && (
                <a
                  href={job.application_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full"
                >
                  <GlassButton variant="outline" size="sm" className="w-full justify-center gap-1.5 mt-2">
                    <ExternalLink className="w-3.5 h-3.5" />
                    Apply on Company Career Site
                  </GlassButton>
                </a>
              )}
            </div>
          </div>

          {/* Employer Intelligence Card */}
          <div className="p-6 rounded-3xl bg-dark-900/70 border border-white/[0.08] backdrop-blur-xl space-y-4 text-xs">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
              Employer Verification
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-white/[0.04]">
                <span className="text-zinc-400">Organization</span>
                <span className="text-white font-medium">{job.company_name}</span>
              </div>
              <div className="flex items-center justify-between pb-2 border-b border-white/[0.04]">
                <span className="text-zinc-400">Jurisdiction</span>
                <span className="text-white font-medium">{job.country || "Tanzania (EAC)"}</span>
              </div>
              <div className="flex items-center justify-between pb-2 border-b border-white/[0.04]">
                <span className="text-zinc-400">Hiring Authenticity</span>
                <span className="text-emerald-400 font-medium">100% Direct Corporate</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-zinc-400">Applicant Privacy</span>
                <span className="text-navy-300 font-medium">Protected &amp; Encrypted</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Real Application Modal */}
      <GlassModal
        isOpen={isApplyModalOpen}
        onClose={() => setIsApplyModalOpen(false)}
        title={`Apply: ${job.title}`}
        description={`Direct Application to ${job.company_name}`}
      >
        {applicationSubmitted ? (
          <div className="py-8 text-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 mx-auto shadow-green-glow">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <p className="text-base font-serif font-bold text-white">Application Successfully Submitted</p>
            <p className="text-xs text-zinc-400 max-w-sm mx-auto leading-relaxed">
              Your verified candidate dossier has been delivered to {job.company_name}. Track your status under your Career Applications dashboard.
            </p>
            <div className="pt-3">
              <Link href="/jobs/applications">
                <GlassButton variant="navy" size="sm">
                  View My Applications →
                </GlassButton>
              </Link>
            </div>
          </div>
        ) : (
          <form onSubmit={handleApplySubmit} className="space-y-4 pt-2 text-xs">
            {appError && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{appError}</span>
              </div>
            )}

            <div className="space-y-3">
              <GlassInput
                label="Candidate Full Name *"
                placeholder="e.g. Samuel M."
                value={applicantName}
                onChange={(e) => setApplicantName(e.target.value)}
                required
              />
              <GlassInput
                label="Email Address *"
                type="email"
                placeholder="candidate@atrium.market"
                value={applicantEmail}
                onChange={(e) => setApplicantEmail(e.target.value)}
                required
              />
              <GlassInput
                label="Direct Phone (WhatsApp / Calls) *"
                type="tel"
                placeholder="+255 755 123 456"
                value={applicantPhone}
                onChange={(e) => setApplicantPhone(e.target.value)}
                required
              />
              <div className="space-y-1.5">
                <label className="block text-xs font-medium uppercase tracking-wider text-zinc-400">
                  Executive Note / Cover Statement (Optional)
                </label>
                <textarea
                  rows={3}
                  value={coverNote}
                  onChange={(e) => setCoverNote(e.target.value)}
                  placeholder="Summarize your key qualifications, leadership experience, or portfolio link..."
                  className="w-full bg-dark-900 border border-white/[0.09] rounded-xl p-3 text-xs text-zinc-100 placeholder:text-zinc-500 focus:outline-none focus:border-navy-500/50"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-white/[0.06]">
              <GlassButton
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => setIsApplyModalOpen(false)}
                disabled={isSubmittingApp}
              >
                Cancel
              </GlassButton>
              <GlassButton
                type="submit"
                variant="navy"
                size="md"
                disabled={isSubmittingApp}
                className="shadow-navy-glow gap-1.5"
              >
                <Send className="w-3.5 h-3.5" />
                {isSubmittingApp ? "Transmitting..." : "Submit Application"}
              </GlassButton>
            </div>
          </form>
        )}
      </GlassModal>
    </div>
  );
}
