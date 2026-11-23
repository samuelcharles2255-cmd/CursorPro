import type { Metadata } from "next";
import { Inter, Cormorant_Garamond } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import { CartProvider } from "@/lib/cart";
import { GlassNavbar } from "@/components/layout/GlassNavbar";
import { GlassFooter } from "@/components/layout/GlassFooter";
import { MobileBottomNav } from "@/components/layout/MobileBottomNav";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const cormorant = Cormorant_Garamond({
  subsets: ["latin"],
  variable: "--font-cormorant",
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "The City · Dual Career Platform & Peer-to-Peer Escrow Marketplace",
  description:
    "The unified super-platform combining Tanzania's most trusted Peer-to-Peer Escrow Marketplace with the premier 770+ Verified Jobs & Career Portal.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`dark ${inter.variable} ${cormorant.variable}`}>
      <body className="bg-dark-950 text-zinc-100 font-sans antialiased min-h-screen flex flex-col selection:bg-market-500 selection:text-dark-950">
        <AuthProvider>
          <CartProvider>
            <GlassNavbar />
            <div className="flex-1 flex flex-col pb-16 md:pb-0">{children}</div>
            <GlassFooter />
            <MobileBottomNav />
          </CartProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
