"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  Search,
  Send,
  MoreVertical,
  ShieldCheck,
  ShoppingBag,
  ArrowLeft,
  CheckCheck,
  Phone,
  DollarSign,
  MapPin,
  Sparkles,
  Lock,
} from "lucide-react";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassSidebar } from "@/components/layout/GlassSidebar";
import { formatTZS } from "@/lib/utils";
import { useAuth } from "@/lib/auth";
import { fetchConversations, fetchConversationMessages, sendMessage } from "@/lib/api";
import { Conversation, ChatMessage } from "@/types";

export default function MessagingPage() {
  const { token, user, loginAsDemo } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConvId, setSelectedConvId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [search, setSearch] = useState("");

  // Load conversations
  useEffect(() => {
    async function load() {
      if (!token) return;
      setIsLoading(true);
      try {
        const list = await fetchConversations(token);
        setConversations(list);
        if (list.length > 0 && !selectedConvId) {
          setSelectedConvId(list[0].id);
        }
      } catch (e) {
        console.warn("Conversations load error:", e);
      } finally {
        setIsLoading(false);
      }
    }
    load();
  }, [token]);

  // Load messages for selected conversation
  useEffect(() => {
    async function loadMsgs() {
      if (!token || !selectedConvId) return;
      try {
        const msgs = await fetchConversationMessages(selectedConvId, token);
        setMessages(msgs);
      } catch (e) {
        console.warn("Messages load error:", e);
      }
    }
    loadMsgs();
  }, [token, selectedConvId]);

  const activeConv = conversations.find((c) => c.id === selectedConvId) || conversations[0];

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || !selectedConvId || !token) return;

    const text = inputMessage.trim();
    setInputMessage("");

    // Optimistic message
    const tempMsg: ChatMessage = {
      id: Date.now(),
      sender_id: user?.id || 0,
      sender_username: user?.username || "You",
      content: text,
      created_at: new Date().toISOString(),
      is_read: false,
    };
    setMessages((prev) => [...prev, tempMsg]);

    try {
      const saved = await sendMessage(selectedConvId, text, token);
      setMessages((prev) => prev.map((m) => (m.id === tempMsg.id ? saved : m)));
    } catch (e) {
      console.warn("Failed to persist message:", e);
    }
  };

  const setCounterOffer = (amountTZS: string) => {
    setInputMessage(`Official Counter Offer: ${amountTZS} TZS with Dar es Salaam in-person inspection.`);
  };

  return (
    <div className="flex-1 flex max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 gap-8">
      <GlassSidebar />

      <main className="flex-1 min-w-0 flex flex-col h-[750px] rounded-3xl bg-dark-850/80 border border-white/[0.09] backdrop-blur-2xl shadow-glass-elevated overflow-hidden">
        {/* Top Header */}
        <div className="p-4 sm:p-5 border-b border-white/[0.07] flex items-center justify-between gap-4 bg-dark-900/60">
          <div className="flex items-center gap-3">
            <Link href="/marketplace" className="text-zinc-400 hover:text-white sm:hidden">
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div>
              <h1 className="text-lg font-serif font-medium text-white flex items-center gap-2">
                Marketplace Direct Inquiries
                <GlassBadge variant="market" size="sm">
                  Escrow Guarded
                </GlassBadge>
              </h1>
              <p className="text-[11px] text-zinc-400">
                End-to-end negotiated transactions secured via Atrium Escrow.
              </p>
            </div>
          </div>

          {!token && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-400 hidden sm:inline">Sign in to sync:</span>
              <button
                onClick={() => loginAsDemo("buyer")}
                className="px-3 py-1.5 rounded-xl bg-market-500/20 hover:bg-market-500/30 border border-market-500/40 text-market-300 text-xs font-semibold"
              >
                Sign In as Buyer
              </button>
            </div>
          )}
        </div>

        {/* Split Pane */}
        <div className="flex-1 flex min-h-0 overflow-hidden">
          {/* Thread List Sidebar */}
          <aside className="w-80 border-r border-white/[0.07] bg-dark-900/40 flex flex-col flex-shrink-0">
            {/* Search filter */}
            <div className="p-3 border-b border-white/[0.06]">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Filter inquiries..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full bg-dark-950/70 border border-white/[0.06] rounded-xl pl-9 pr-3 py-1.5 text-xs text-white placeholder:text-zinc-500 focus:outline-none focus:border-market-500/50"
                />
              </div>
            </div>

            {/* Conversation list */}
            <div className="flex-1 overflow-y-auto divide-y divide-white/[0.04]">
              {conversations.length === 0 ? (
                <div className="p-6 text-center space-y-3">
                  <p className="text-xs text-zinc-400">
                    {token ? "No active inquiry threads found." : "Sign in to view your live chat threads."}
                  </p>
                  {!token && (
                    <button
                      onClick={() => loginAsDemo("buyer")}
                      className="px-3 py-1.5 rounded-xl bg-market-500/20 text-market-300 text-xs font-semibold"
                    >
                      Connect Demo Thread
                    </button>
                  )}
                </div>
              ) : (
                conversations
                  .filter((c) => {
                    const q = search.toLowerCase();
                    return (
                      !q ||
                      c.listing_title?.toLowerCase().includes(q) ||
                      c.other_participant?.name?.toLowerCase().includes(q)
                    );
                  })
                  .map((conv) => {
                    const isSelected = conv.id === selectedConvId;
                    const contactName =
                      conv.other_participant?.name ||
                      conv.other_participant?.username ||
                      conv.seller_username ||
                      "Participant";
                    const role = conv.other_participant?.role || "Merchant";

                    return (
                      <button
                        key={conv.id}
                        onClick={() => setSelectedConvId(conv.id)}
                        className={`w-full p-3.5 text-left transition-all flex items-start gap-3 hover:bg-white/[0.03] ${
                          isSelected ? "bg-white/[0.06] border-l-2 border-market-400" : ""
                        }`}
                      >
                        <div className="w-10 h-10 rounded-xl bg-dark-950 border border-white/[0.08] flex items-center justify-center text-market-400 font-bold text-xs flex-shrink-0">
                          {contactName[0]?.toUpperCase() || "C"}
                        </div>

                        <div className="flex-1 min-w-0 space-y-1">
                          <div className="flex items-center justify-between gap-1">
                            <span className="text-xs font-semibold text-white truncate">
                              {contactName}
                            </span>
                            <span className="text-[10px] text-zinc-500">
                              {role}
                            </span>
                          </div>

                          <p className="text-[11px] text-market-300 truncate font-medium">
                            {conv.listing_title || "Marketplace Product"}
                          </p>

                          <p className="text-[11px] text-zinc-400 truncate">
                            {conv.last_message?.content || "Tap to read message thread..."}
                          </p>
                        </div>
                      </button>
                    );
                  })
              )}
            </div>
          </aside>

          {/* Active Chat Conversation Pane */}
          <section className="flex-1 flex flex-col min-w-0 bg-dark-850/40">
            {activeConv ? (
              <>
                {/* Context Item Header */}
                <div className="p-3.5 px-6 border-b border-white/[0.07] bg-dark-900/40 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-10 h-10 rounded-xl bg-dark-950 border border-white/[0.08] flex items-center justify-center text-market-400 font-serif font-bold text-sm flex-shrink-0">
                      {activeConv.other_participant?.name?.[0] || "A"}
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold text-white truncate">
                          {activeConv.other_participant?.name || activeConv.seller_username}
                        </span>
                        <GlassBadge variant="market" size="sm">
                          Verified
                        </GlassBadge>
                      </div>
                      <p className="text-[11px] text-zinc-400 truncate flex items-center gap-2">
                        <span>Re: {activeConv.listing_title}</span>
                        {activeConv.listing_price && (
                          <span className="text-market-300 font-semibold">
                            {formatTZS(activeConv.listing_price)}
                          </span>
                        )}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {activeConv.listing_slug && (
                      <Link href={`/marketplace/listing/${activeConv.listing_slug}`}>
                        <GlassButton variant="ghost" size="sm">
                          View Listing
                        </GlassButton>
                      </Link>
                    )}
                  </div>
                </div>

                {/* Quick Counter Offer Pills */}
                <div className="px-6 py-2 bg-dark-900/20 border-b border-white/[0.04] flex items-center gap-2 overflow-x-auto text-[11px]">
                  <span className="text-zinc-500 whitespace-nowrap">Quick Reply:</span>
                  <button
                    onClick={() => setCounterOffer("7,200,000")}
                    className="px-2.5 py-1 rounded-lg bg-market-500/10 hover:bg-market-500/20 text-market-300 border border-market-500/25 whitespace-nowrap transition-all"
                  >
                    Counter 7.2M TZS
                  </button>
                  <button
                    onClick={() => setCounterOffer("7,500,000")}
                    className="px-2.5 py-1 rounded-lg bg-market-500/10 hover:bg-market-500/20 text-market-300 border border-market-500/25 whitespace-nowrap transition-all"
                  >
                    Counter 7.5M TZS
                  </button>
                  <button
                    onClick={() =>
                      setInputMessage(
                        "I would like to schedule an in-person inspection at your Masaki showroom."
                      )
                    }
                    className="px-2.5 py-1 rounded-lg bg-dark-900 hover:bg-dark-800 text-zinc-300 border border-white/[0.08] whitespace-nowrap transition-all"
                  >
                    Request Inspection
                  </button>
                </div>

                {/* Messages Scroll Area */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                  {messages.length === 0 ? (
                    <div className="text-center py-20 text-zinc-500 text-xs">
                      No messages yet in this inquiry thread. Send the first message below.
                    </div>
                  ) : (
                    messages.map((m) => {
                      const isMe = user ? m.sender_id === user.id : m.sender_username === "You";
                      return (
                        <div
                          key={m.id}
                          className={`flex flex-col ${isMe ? "items-end" : "items-start"}`}
                        >
                          <div
                            className={`max-w-md p-3.5 rounded-2xl text-xs leading-relaxed ${
                              isMe
                                ? "bg-market-600 text-dark-950 font-medium rounded-br-none shadow-green-glow/20"
                                : "bg-dark-900 border border-white/[0.08] text-white rounded-bl-none"
                            }`}
                          >
                            {m.content}
                          </div>
                          <span className="text-[10px] text-zinc-500 mt-1 px-1">
                            {isMe ? "You" : m.sender_username || "Merchant"}
                          </span>
                        </div>
                      );
                    })
                  )}
                </div>

                {/* Input Area */}
                <form
                  onSubmit={handleSendMessage}
                  className="p-4 border-t border-white/[0.07] bg-dark-900/60 flex items-center gap-3"
                >
                  <input
                    type="text"
                    placeholder="Type inquiry or formal offer..."
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    className="flex-1 bg-dark-950/80 border border-white/[0.08] rounded-2xl px-4 py-2.5 text-xs text-white placeholder:text-zinc-500 focus:outline-none focus:border-market-500/50"
                  />
                  <GlassButton type="submit" variant="market" size="sm" className="gap-1.5 px-4">
                    <Send className="w-3.5 h-3.5" />
                    <span>Send</span>
                  </GlassButton>
                </form>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-zinc-500 text-xs">
                Select an inquiry from the sidebar to open the negotiation thread.
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
