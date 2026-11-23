import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTZS(amount: number | string | undefined | null): string {
  if (amount === undefined || amount === null || amount === "") return "TSh 0";
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  if (isNaN(num)) return "TSh 0";
  return `TSh ${num.toLocaleString("en-US", { maximumFractionDigits: 0 })}`;
}

export function formatCondition(condition?: string): string {
  switch (condition) {
    case "NEW":
      return "Brand New";
    case "LIKE_NEW":
      return "Like New / Pristine";
    case "GOOD":
      return "Good Condition";
    case "FAIR":
      return "Fair / Working";
    case "REFURBISHED":
      return "Refurbished";
    default:
      return condition || "Good";
  }
}

export function formatDate(dateString?: string): string {
  if (!dateString) return "";
  const d = new Date(dateString);
  if (isNaN(d.getTime())) return dateString;
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function getConditionColor(condition?: string): string {
  switch (condition) {
    case "NEW":
      return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
    case "LIKE_NEW":
      return "bg-gold-500/10 text-gold-400 border-gold-500/20";
    case "REFURBISHED":
      return "bg-blue-500/10 text-blue-400 border-blue-500/20";
    default:
      return "bg-zinc-800/60 text-zinc-300 border-zinc-700/40";
  }
}
