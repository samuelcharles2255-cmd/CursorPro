"use client";

import React, { useState } from "react";
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
} from "lucide-react";
import { GlassButton } from "@/components/ui/GlassButton";
import { GlassBadge } from "@/components/ui/GlassBadge";
import { GlassSidebar } from "@/components/layout/GlassSidebar";
import { formatTZS } from "@/lib/utils";

interface MockChat {
  id: number;
  contactName: string;
  contactRole: string;
  itemTitle: string;
  itemPrice: number;
  itemImage: string;
  lastMessage: string;
  timestamp: string;
  unread: number;
  messages: {
    id: number;
    isMe: boolean;
    text: string;
    time: string;
  }[];
}

const INITIAL_CHATS: MockChat[] = [
  {
    id: 1,
    contactName: "Juma Salim",
    contactRole: "Interested Buyer",
    itemTitle: "MacBook Pro 16\" M3 Max Space Black",
    itemPrice: 7850000,
    itemImage: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=200&q=80",
    lastMessage: "Would you accept 7,300,000 TSh if I pick it up at Masaki today?",
    timestamp: "10:42 AM",
    unread: 1,
    messages: [
      { id: 1, isMe: false, text: "Habari! Is the MacBook Pro M3 Max still available?", time: "10:30 AM" },
      { id: 2, isMe: true, text: "Hello! Yes, it is in pristine condition with all accessories in Masaki.", time: "10:34 AM" },
      { id: 3, isMe: false, text: "Would you accept 7,300,000 TSh if I pick it up at Masaki today?", time: "10:42 AM" },
    ],
  },
  {
    id: 2,
    contactName: "Farida Kimaro",
    contactRole: "Verified Buyer",
    itemTitle: "Sony Alpha A7R V Full-Frame Camera",
    itemPrice: 11200000,
    itemImage: "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=200&q=80",
    lastMessage: "Great, I will initiate the escrow deposit right now.",
    timestamp: "Yesterday",
    unread: 0,
    messages: [
      { id: 1, isMe: false, text: "Does this include the Sony GM 24-70mm lens?", time: "Yesterday" },
      { id: 2, isMe: true, text: "Yes, it is the full bundle with the GM II lens and 2 CFexpress cards.", time: "Yesterday" },
      { id: 3, isMe: false, text: "Great, I will initiate the escrow deposit right now.", time: "Yesterday" },
    ],
  },
];

export default function MessagingPage() {
  const [chats, setChats] = useState<MockChat[]>(INITIAL_CHATS);
  const [selectedChatId, setSelectedChatId] = useState<number>(1);
  const [inputMessage, setInputMessage] = useState("");

  const activeChat = chats.find((c) => c.id === selectedChatId) || chats[0];

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const newMsg = {
      id: Date.now(),
      isMe: true,
      text: inputMessage,
      time: "Just now",
    };

    setChats(
      chats.map((c) =>
        c.id === selectedChatId
          ? {
              ...c,
              messages: [...c.messages, newMsg],
              lastMessage: inputMessage,
              timestamp: "Just now",
            }
          : c
      )
    );
    setInputMessage("");
  };

  const handleQuickOffer = (amount: number) => {
    const newMsg = {
      id: Date.now(),
      isMe: true,
      text: `Official counter-offer: ${formatTZS(amount)} under The City Escrow.`,
      time: "Just now",
    };
    setChats(
      chats.map((c) =>
        c.id === selectedChatId
          ? {
              ...c,
              messages: [...c.messages, newMsg],
              lastMessage: newMsg.text,
            }
          : c
      )
    );
  };

  return (
    <div className="flex-1 flex max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8 gap-8">
      <GlassSidebar />

      <main className="flex-1 min-w-0 space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-serif text-white">Merchant & Buyer Inquiries</h1>
            <p className="text-xs text-zinc-400">
              Encrypted real-time communication guarded by The City Escrow.
            </p>
          </div>
          <GlassBadge variant="market" size="sm">
            <ShieldCheck className="w-3.5 h-3.5 text-market-400" />
            Escrow Guard Active
          </GlassBadge>
        </div>

        {/* Messaging Container */}
        <div className="h-[620px] rounded-3xl bg-dark-850/80 border border-white/[0.08] backdrop-blur-2xl overflow-hidden shadow-glass-elevated flex flex-col md:flex-row">
          {/* Left: Conversations list */}
          <div className="w-full md:w-80 border-r border-white/[0.08] flex flex-col bg-dark-900/60">
            {/* Search */}
            <div className="p-3 border-b border-white/[0.06]">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Filter inquiries..."
                  className="w-full bg-dark-950/80 rounded-xl pl-9 pr-3 py-1.5 text-xs text-zinc-200 border border-white/[0.06] focus:outline-none"
                />
              </div>
            </div>

            {/* List */}
            <div className="flex-1 overflow-y-auto divide-y divide-white/[0.04]">
              {chats.map((chat) => (
                <div
                  key={chat.id}
                  onClick={() => setSelectedChatId(chat.id)}
                  className={`p-4 flex items-start gap-3 cursor-pointer transition-colors ${
                    selectedChatId === chat.id
                      ? "bg-white/[0.06] border-l-2 border-market-500"
                      : "hover:bg-white/[0.02]"
                  }`}
                >
                  <img
                    src={chat.itemImage}
                    alt=""
                    className="w-11 h-11 rounded-xl object-cover bg-dark-950 flex-shrink-0"
                  />
                  <div className="flex-1 min-w-0 space-y-0.5">
                    <div className="flex items-center justify-between">
                      <p className="text-xs font-semibold text-white truncate">
                        {chat.contactName}
                      </p>
                      <span className="text-[10px] text-zinc-500">{chat.timestamp}</span>
                    </div>
                    <p className="text-[11px] text-market-400 font-medium truncate">
                      {chat.itemTitle}
                    </p>
                    <p className="text-[11px] text-zinc-400 truncate">{chat.lastMessage}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right: Active Chat Window */}
          <div className="flex-1 flex flex-col min-w-0 bg-dark-850/40">
            {/* Chat Header with Item Preview */}
            <div className="p-4 border-b border-white/[0.07] bg-dark-900/80 backdrop-blur-md flex items-center justify-between gap-4">
              <div className="flex items-center gap-3 min-w-0">
                <img
                  src={activeChat.itemImage}
                  alt=""
                  className="w-10 h-10 rounded-xl object-cover bg-dark-950 flex-shrink-0"
                />
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-xs font-semibold text-white truncate">
                      {activeChat.contactName}
                    </p>
                    <span className="text-[10px] text-zinc-500">({activeChat.contactRole})</span>
                  </div>
                  <p className="text-[11px] text-zinc-400 truncate">
                    {activeChat.itemTitle} ·{" "}
                    <span className="text-market-400 font-semibold">
                      {formatTZS(activeChat.itemPrice)}
                    </span>
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleQuickOffer(7500000)}
                  className="hidden sm:inline-flex px-3 py-1.5 rounded-lg bg-market-500/15 hover:bg-market-500/25 border border-market-500/30 text-market-300 text-xs font-medium"
                >
                  Send Counter Offer
                </button>
              </div>
            </div>

            {/* Messages Body */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
              {activeChat.messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${msg.isMe ? "items-end" : "items-start"}`}
                >
                  <div
                    className={`max-w-md p-3.5 rounded-2xl text-xs leading-relaxed ${
                      msg.isMe
                        ? "bg-gradient-to-r from-market-600 to-market-500 text-dark-950 font-medium rounded-br-sm shadow-green-glow/20"
                        : "bg-dark-900/90 border border-white/[0.08] text-zinc-100 rounded-bl-sm"
                    }`}
                  >
                    {msg.text}
                  </div>
                  <span className="text-[10px] text-zinc-500 mt-1 px-1">{msg.time}</span>
                </div>
              ))}
            </div>

            {/* Quick response pills */}
            <div className="px-4 py-2 border-t border-white/[0.05] bg-dark-900/40 flex items-center gap-2 overflow-x-auto text-[11px]">
              <span className="text-zinc-500 flex-shrink-0">Quick reply:</span>
              <button
                onClick={() => setInputMessage("Yes, available for inspection in Masaki today.")}
                className="px-2.5 py-1 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-zinc-300 flex-shrink-0"
              >
                Available for inspection
              </button>
              <button
                onClick={() => setInputMessage("I can do 7,500,000 TSh minimum.")}
                className="px-2.5 py-1 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-zinc-300 flex-shrink-0"
              >
                Minimum price is 7.5M
              </button>
              <button
                onClick={() => setInputMessage("Can we proceed through The City Escrow deposit?")}
                className="px-2.5 py-1 rounded-lg bg-white/[0.04] hover:bg-white/[0.08] text-zinc-300 flex-shrink-0"
              >
                Use Escrow Deposit
              </button>
            </div>

            {/* Input Bar */}
            <form onSubmit={handleSendMessage} className="p-3 border-t border-white/[0.07] bg-dark-900/70 flex items-center gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message or inquiry..."
                className="flex-1 bg-dark-950/80 border border-white/[0.08] rounded-xl px-4 py-2.5 text-xs text-white placeholder:text-zinc-500 focus:outline-none focus:border-market-500/50"
              />
              <GlassButton type="submit" variant="market" size="sm" className="px-4">
                <Send className="w-4 h-4" />
              </GlassButton>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
