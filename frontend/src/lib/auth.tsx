"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User } from "@/types";

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string, user: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
  isSeller: boolean;
  switchRoleDemo: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    try {
      const savedToken = localStorage.getItem("thecity_token");
      const savedUser = localStorage.getItem("thecity_user");
      if (savedToken && savedUser) {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } else {
        // Set a default luxury demo user for smooth interaction out-of-the-box
        const demoUser: User = {
          id: 1,
          email: "seller@thecity.market",
          username: "lumina_tech",
          name: "Lumina Luxury Tech",
          phone_number: "+255755123456",
          is_seller: true,
        };
        setUser(demoUser);
        setToken("demo_jwt_token_thecity_2026");
      }
    } catch (e) {
      console.warn("Auth storage error:", e);
    }
  }, []);

  const login = (newToken: string, newUser: User) => {
    setToken(newToken);
    setUser(newUser);
    try {
      localStorage.setItem("thecity_token", newToken);
      localStorage.setItem("thecity_user", JSON.stringify(newUser));
    } catch (e) {
      console.warn("Failed saving auth:", e);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    try {
      localStorage.removeItem("thecity_token");
      localStorage.removeItem("thecity_user");
    } catch (e) {
      console.warn("Failed clearing auth:", e);
    }
  };

  const switchRoleDemo = () => {
    if (!user) return;
    const updated = { ...user, is_seller: !user.is_seller };
    setUser(updated);
    try {
      localStorage.setItem("thecity_user", JSON.stringify(updated));
    } catch (e) {
      console.warn("Failed saving switch:", e);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        login,
        logout,
        isAuthenticated: !!token,
        isSeller: !!user?.is_seller,
        switchRoleDemo,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
