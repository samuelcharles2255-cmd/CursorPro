"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Briefcase,
  Search,
  MapPin,
  Building2,
  SlidersHorizontal,
  ChevronRight,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";
import { fetchJobs, FALLBACK_JOBS } from "@/lib/api";
import { Job } from "@/types";
import { JobCard } from "@/components/features/jobs/JobCard";
import { GlassSidebar } from "@/components/layout/GlassSidebar";

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>(FALLBACK_JOBS);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [locationFilter, setLocationFilter] = useState("all");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      try {
        const data = await fetchJobs({ search });
        if (data && data.length > 0) {
          setJobs(data);
        }
      } catch (e) {
        console.warn("Jobs load error:", e);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [search]);

  const filtered = jobs.filter((j) => {
    if (typeFilter !== "all") {
      const empType = (j.employment_type || "full-time").toLowerCase();
      if (!empType.includes(typeFilter.toLowerCase())) {
        return false;
      }
    }
    if (locationFilter !== "all") {
      const loc = (j.location || "").toLowerCase();
      if (!loc.includes(locationFilter.toLowerCase())) return false;
    }
    return true;
  });

  return (
    <div className="flex-1 flex max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 gap-8">
      <GlassSidebar />

      <main className="flex-1 space-y-8 min-w-0">
        {/* Navy Anchor Hero */}
        <section className="relative rounded-3xl bg-gradient-to-r from-navy-950 via-dark-900 to-navy-900 border border-navy-700/50 p-6 sm:p-10 shadow-glass-elevated overflow-hidden">
          <div className="absolute top-0 right-0 w-80 h-80 bg-navy-600/[0.12] rounded-full blur-3xl pointer-events-none" />

          <div className="relative z-10 max-w-2xl space-y-3.5">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-navy-600/25 border border-navy-500/40 text-navy-200 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-navy-400 animate-pulse" />
              Jobs · 770+ Verified Open Roles in East Africa
            </div>

            <h1 className="text-3xl sm:text-4xl font-serif font-bold text-white tracking-tight leading-tight">
              Executive &amp; Tech Opportunities in Tanzania.
            </h1>

            <p className="text-xs sm:text-sm text-zinc-300 leading-relaxed">
              Curated positions indexed directly from corporate ATS portals across banks, tech hubs, and NGOs with clear salary benchmarks.
            </p>

            {/* Search Input */}
            <div className="pt-2">
              <div className="relative">
                <Search className="w-4 h-4 text-zinc-400 absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Filter by job title, company name, or skills (e.g. Developer, Finance, M-Pesa)..."
                  className="w-full min-h-[48px] bg-dark-950/90 border border-navy-700/60 rounded-2xl pl-11 pr-4 py-2.5 text-xs text-white placeholder:text-zinc-500 focus:outline-none focus:border-navy-400 transition-colors"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Filter Toolbar */}
        <section className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-2xl bg-dark-900/70 border border-navy-800/60 text-xs">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-zinc-400 font-medium">Employment:</span>
            {["all", "full-time", "contract", "remote"].map((t) => (
              <button
                key={t}
                onClick={() => setTypeFilter(t)}
                className={`min-h-[36px] px-3 rounded-lg capitalize text-xs font-semibold transition-all ${
                  typeFilter === t
                    ? "bg-navy-700 text-white shadow-navy-glow"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                {t === "all" ? "All Types" : t}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <span className="text-zinc-400 font-medium">City:</span>
            <select
              value={locationFilter}
              onChange={(e) => setLocationFilter(e.target.value)}
              className="bg-dark-850 border border-navy-700/60 rounded-xl px-3 py-1.5 text-xs text-zinc-200 focus:outline-none focus:border-navy-400"
            >
              <option value="all">All Locations</option>
              <option value="dar es salaam">Dar es Salaam</option>
              <option value="nairobi">Nairobi</option>
              <option value="arusha">Arusha</option>
              <option value="remote">Remote</option>
            </select>
          </div>
        </section>

        {/* Jobs Feed Grid */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-xs text-zinc-400 font-medium">
              Showing <span className="text-white font-bold">{filtered.length}</span> verified job openings
            </p>
          </div>

          {isLoading ? (
            <div className="text-center py-20 text-xs text-zinc-400">
              Loading active positions from database...
            </div>
          ) : filtered.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {filtered.map((job) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>
          ) : (
            <div className="text-center py-20 rounded-3xl bg-dark-850/40 border border-white/[0.06] p-8 space-y-2">
              <p className="text-base font-semibold text-white">No roles match your search</p>
              <p className="text-xs text-zinc-400">
                Try selecting &ldquo;All Types&rdquo; or clearing your keywords.
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
