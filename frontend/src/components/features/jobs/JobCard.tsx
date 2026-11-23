"use client";

import React, { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { MapPin, Briefcase, Building2, Calendar, ArrowUpRight, Bookmark } from "lucide-react";
import { Job } from "@/types";
import { formatDate } from "@/lib/utils";
import { SafeImage } from "@/components/ui/SafeImage";

interface JobCardProps {
  job: Job;
}

export function JobCard({ job }: JobCardProps) {
  const [isSaved, setIsSaved] = useState(false);

  const toggleSave = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsSaved(!isSaved);
  };

  return (
    <article className="group relative rounded-2xl bg-dark-900/90 border border-navy-800/60 hover:border-navy-500/60 p-5 flex flex-col justify-between shadow-glass hover:shadow-navy-glow transition-all duration-200 min-w-0">
      <div className="space-y-3.5 min-w-0">
        {/* Top: Company Logo + Employment Type */}
        <div className="flex items-start justify-between gap-3 min-w-0">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-11 h-11 rounded-xl bg-navy-950 border border-navy-700/50 flex items-center justify-center text-navy-300 font-bold overflow-hidden flex-shrink-0">
              {job.company_logo ? (
                <SafeImage
                  src={job.company_logo}
                  alt={job.company_name}
                  fallbackType="company"
                  aspectRatio="aspect-square"
                  className="w-full h-full object-contain p-1"
                />
              ) : (
                <Building2 className="w-5 h-5 text-navy-400" />
              )}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-zinc-300 truncate">
                {job.company_name}
              </p>
              <div className="flex items-center gap-1 text-[11px] text-zinc-400 truncate">
                <MapPin className="w-3.5 h-3.5 text-navy-400 flex-shrink-0" />
                <span className="truncate">
                  {job.location || "Dar es Salaam, Tanzania"}
                </span>
              </div>
            </div>
          </div>

          {/* Bookmark Button (44x44px touch target) */}
          <button
            onClick={toggleSave}
            className="min-h-[44px] min-w-[44px] p-2 rounded-xl text-zinc-400 hover:text-navy-300 hover:bg-navy-900/50 flex items-center justify-center transition-colors flex-shrink-0"
            aria-label={isSaved ? "Remove from saved jobs" : "Save this job"}
          >
            <Bookmark className={`w-4 h-4 ${isSaved ? "fill-navy-400 text-navy-400" : ""}`} />
          </button>
        </div>

        {/* Title */}
        <Link href={`/jobs/${job.id}`} className="block">
          <h3 className="text-sm sm:text-base font-bold text-white group-hover:text-navy-300 transition-colors line-clamp-2 leading-snug">
            {job.title}
          </h3>
        </Link>

        {/* Badges: Employment type & Salary */}
        <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
          <span className="px-2.5 py-1 rounded-full bg-navy-900 text-navy-300 border border-navy-700/60 font-semibold text-[11px]">
            {job.employment_type || "Full-time"}
          </span>
          {job.salary_min && (
            <span className="px-2.5 py-1 rounded-full bg-white/[0.04] text-emerald-400 border border-white/[0.06] text-[11px] font-mono">
              {job.salary_currency || "TSh"} {Number(job.salary_min).toLocaleString()}
            </span>
          )}
        </div>
      </div>

      {/* Card Footer */}
      <div className="mt-4 pt-3 border-t border-navy-800/40 flex items-center justify-between text-xs text-zinc-400">
        <span className="flex items-center gap-1.5 text-[11px] text-zinc-500">
          <Calendar className="w-3.5 h-3.5 text-zinc-500" />
          {job.posted_at ? formatDate(job.posted_at) : "Active"}
        </span>

        <Link
          href={`/jobs/${job.id}`}
          className="min-h-[44px] px-3.5 rounded-xl bg-navy-700/80 hover:bg-navy-600 text-white font-semibold text-xs inline-flex items-center gap-1 transition-colors"
        >
          <span>View Role</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </article>
  );
}
