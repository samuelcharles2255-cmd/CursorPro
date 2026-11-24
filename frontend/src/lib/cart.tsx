"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { OrderItem } from "@/types";

interface CartContextType {
  items: OrderItem[];
  addToCart: (item: Omit<OrderItem, "quantity">) => void;
  removeFromCart: (listingId?: number | null) => void;
  clearCart: () => void;
  totalPrice: number;
  itemCount: number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<OrderItem[]>([]);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("thecity_cart");
      if (saved) {
        setItems(JSON.parse(saved));
      }
    } catch (e) {
      console.warn("Cart storage read failed:", e);
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem("thecity_cart", JSON.stringify(items));
    } catch (e) {
      console.warn("Cart storage write failed:", e);
    }
  }, [items]);

  const addToCart = (newItem: Omit<OrderItem, "quantity">) => {
    setItems((prev) => {
      const existing = prev.find((i) => i.listing_id === newItem.listing_id);
      if (existing) {
        return prev.map((i) =>
          i.listing_id === newItem.listing_id
            ? { ...i, quantity: i.quantity + 1 }
            : i
        );
      }
      return [...prev, { ...newItem, quantity: 1 }];
    });
  };

  const removeFromCart = (listingId?: number | null) => {
    if (listingId === undefined || listingId === null) return;
    setItems((prev) => prev.filter((i) => i.listing_id !== listingId));
  };

  const clearCart = () => {
    setItems([]);
  };

  const totalPrice = items.reduce(
    (sum, item) => sum + Number(item.price || item.unit_price || 0) * item.quantity,
    0
  );
  const itemCount = items.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <CartContext.Provider
      value={{
        items,
        addToCart,
        removeFromCart,
        clearCart,
        totalPrice,
        itemCount,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
}
