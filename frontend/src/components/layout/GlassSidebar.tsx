"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  ShoppingBag,
  Briefcase,
  MessageSquare,
  PlusCircle,
  ShieldCheck,
  User,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Compass,
  Newspaper,
  Tag,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";

interface GlassSidebarProps {
  className?: string;
}

interface NavItem {
  name: string;
  href: string;
  icon: any;
  badge?: string;
  badgeColor?: string;
  branch?: "market" | "jobs" | "default";
}

interface NavGroup {
  label: string;
  items: NavItem[];
}

export function GlassSidebar({ className }: GlassSidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const pathname = usePathname();
  const { user } = useAuth();

  const navGroups: NavGroup[] = [
    {
      label: "The City Platform",
      items: [
        { name: "Overview", href: "/", icon: Compass, branch: "default" },
        { name: "Marketplace", href: "/marketplace", icon: ShoppingBag, badge: "Green", branch: "market" },
        { name: "Jobs", href: "/jobs", icon: Briefcase, badge: "770+", branch: "jobs" },
      ],
    },
    {
      label: "Marketplace (Biashara)",
      items: [
        { name: "Browse Feed", href: "/marketplace/search", icon: Tag, branch: "market" },
        { name: "Post an Item", href: "/marketplace/create-listing", icon: PlusCircle, branch: "market" },
        { name: "Seller Dashboard", href: "/marketplace/seller/dashboard", icon: LayoutDashboard, branch: "market" },
        { name: "Messages & Offers", href: "/marketplace/messages", icon: MessageSquare, branch: "market" },
      ],
    },
    {
      label: "Career Center",
      items: [
        { name: "Search All Jobs", href: "/jobs", icon: Briefcase, branch: "jobs" },
        { name: "Application Status", href: "/jobs/applications", icon: LayoutDashboard, branch: "jobs" },
      ],
    },
    {
      label: "Administration & Trust",
      items: [
        { name: "Moderation Queue", href: "/marketplace/moderation", icon: ShieldCheck, branch: "default" },
        { name: "Profile & Settings", href: "/profile", icon: Settings, branch: "default" },
      ],
    },
  ];

  return (
    <motion.aside
      animate={{ width: isCollapsed ? 76 : 260 }}
      transition={{ duration: 0.25, ease: "easeInOut" }}
      className={cn(
        "relative hidden lg:flex flex-col h-[calc(100vh-5rem)] sticky top-20 border-r border-white/[0.08] bg-dark-950/70 backdrop-blur-2xl p-3 z-30 select-none",
        className
      )}
    >
      {/* Collapse toggle button */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3 top-6 w-7 h-7 rounded-full bg-dark-850 border border-white/[0.15] text-zinc-400 hover:text-white flex items-center justify-center shadow-md z-40 transition-colors"
        aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {isCollapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
      </button>

      {/* Navigation Groups */}
      <div className="flex-1 space-y-6 overflow-y-auto pt-2 no-scrollbar">
        {navGroups.map((group, idx) => (
          <div key={idx} className="space-y-1">
            {!isCollapsed && (
              <p className="px-3 text-[10px] font-bold tracking-wider uppercase text-zinc-500 mb-1.5">
                {group.label}
              </p>
            )}
            {group.items.map((item) => {
              const Icon = item.icon;
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));

              // Branch-specific active styles
              const activeStyles =
                item.branch === "market"
                  ? "bg-market-500/15 text-market-300 border border-market-500/30 shadow-green-glow"
                  : item.branch === "jobs"
                  ? "bg-navy-600/25 text-navy-200 border border-navy-500/40 shadow-navy-glow"
                  : "bg-white/[0.08] text-white border border-white/[0.1] shadow-glass-sm";

              const iconColor = isActive
                ? item.branch === "market"
                  ? "text-market-400"
                  : item.branch === "jobs"
                  ? "text-navy-400"
                  : "text-white"
                : item.branch === "market"
                ? "text-market-500/70 group-hover:text-market-400"
                : item.branch === "jobs"
                ? "text-navy-400/70 group-hover:text-navy-300"
                : "text-zinc-400 group-hover:text-zinc-200";

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3 min-h-[44px] rounded-xl text-xs font-semibold transition-all group relative",
                    isActive
                      ? activeStyles
                      : "text-zinc-400 hover:text-zinc-200 hover:bg-white/[0.04]"
                  )}
                  title={isCollapsed ? item.name : undefined}
                >
                  {/* Subtle active glow indicator */}
                  {isActive && (
                    <motion.div
                      layoutId="activeSidebarGlow"
                      className={cn(
                        "absolute left-0 w-1 h-5 rounded-r-full",
                        item.branch === "market"
                          ? "bg-market-400 shadow-green-glow"
                          : item.branch === "jobs"
                          ? "bg-navy-400 shadow-navy-glow"
                          : "bg-white"
                      )}
                    />
                  )}
                  <Icon className={cn("w-4 h-4 flex-shrink-0 transition-colors", iconColor)} />
                  {!isCollapsed && (
                    <span className="flex-1 truncate">{item.name}</span>
                  )}
                  {!isCollapsed && item.badge && (
                    <span
                      className={cn(
                        "px-1.5 py-0.5 rounded-full text-[10px] font-mono",
                        item.branch === "market"
                          ? "bg-market-500/20 text-market-300"
                          : "bg-navy-500/20 text-navy-300"
                      )}
                    >
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </div>

      {/* Bottom User Indicator */}
      <div className="pt-3 border-t border-white/[0.07]">
        {!isCollapsed ? (
          <div className="p-3 rounded-2xl bg-dark-900/60 border border-white/[0.06] flex items-center justify-between">
            <div className="flex items-center gap-2.5 min-w-0">
              <div className="w-8 h-8 rounded-xl bg-market-500/20 border border-market-500/30 flex items-center justify-center text-market-300 text-xs font-bold">
                {user?.name ? user.name[0] : "U"}
              </div>
              <div className="truncate">
                <p className="text-xs font-semibold text-white truncate">{user?.name || "Lumina Tech"}</p>
                <p className="text-[10px] text-market-400 font-mono font-medium">VERIFIED MERCHANT</p>
              </div>
            </div>
            <Sparkles className="w-3.5 h-3.5 text-market-400 flex-shrink-0" />
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="w-8 h-8 rounded-xl bg-market-500/20 border border-market-500/30 flex items-center justify-center text-market-400 text-xs font-bold">
              <Sparkles className="w-4 h-4" />
            </div>
          </div>
        )}
      </div>
    </motion.aside>
  );
}
