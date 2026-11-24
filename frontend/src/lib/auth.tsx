"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User } from "@/types";
import { loginWithEmail, fetchCurrentUser, refreshAccessToken } from "@/lib/api";

interface AuthContextType {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  login: (token: string, user: User, refreshToken?: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
  isSeller: boolean;
  loginAsDemo: (role?: "seller" | "buyer") => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);

  useEffect(() => {
    try {
      const savedToken = localStorage.getItem("atrium_token") || localStorage.getItem("thecity_token");
      const savedRefresh = localStorage.getItem("atrium_refresh_token");
      const savedUser = localStorage.getItem("atrium_user") || localStorage.getItem("thecity_user");
      if (savedToken && savedUser) {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
        if (savedRefresh) setRefreshToken(savedRefresh);
      }
    } catch (e) {
      console.warn("Auth storage error:", e);
    }
  }, []);

  const login = (newToken: string, newUser: User, newRefresh?: string) => {
    setToken(newToken);
    setUser(newUser);
    if (newRefresh) setRefreshToken(newRefresh);
    try {
      localStorage.setItem("atrium_token", newToken);
      localStorage.setItem("atrium_user", JSON.stringify(newUser));
      if (newRefresh) localStorage.setItem("atrium_refresh_token", newRefresh);
    } catch (e) {
      console.warn("Failed saving auth:", e);
    }
  };

  const logout = () => {
    setToken(null);
    setRefreshToken(null);
    setUser(null);
    try {
      localStorage.removeItem("atrium_token");
      localStorage.removeItem("atrium_refresh_token");
      localStorage.removeItem("atrium_user");
      localStorage.removeItem("thecity_token");
      localStorage.removeItem("thecity_user");
    } catch (e) {
      console.warn("Failed clearing auth:", e);
    }
  };

  const loginAsDemo = async (role: "seller" | "buyer" = "seller") => {
    const email = role === "seller" ? "seller@atrium.market" : "buyer@atrium.market";
    const password = "Password123!";
    try {
      const data = await loginWithEmail(email, password);
      login(data.tokens.access, data.user, data.tokens.refresh);
    } catch (err) {
      console.warn("Demo login error, falling back locally:", err);
      const fallbackUser: User = {
        id: role === "seller" ? 1 : 2,
        email,
        username: role === "seller" ? "lumina_tech" : "juma_salim",
        name: role === "seller" ? "Lumina Luxury Tech & Goods" : "Juma Salim",
        phone_number: role === "seller" ? "+255755123456" : "+255712345678",
        is_seller: role === "seller",
      };
      login("demo_token", fallbackUser);
    }
  };

  const refreshUser = async () => {
    if (!token) return;
    try {
      const current = await fetchCurrentUser(token);
      setUser(current);
      localStorage.setItem("atrium_user", JSON.stringify(current));
    } catch (e) {
      console.warn("refreshUser error:", e);
      // Attempt token refresh if refresh token is present
      const savedRefresh = refreshToken || localStorage.getItem("atrium_refresh_token");
      if (savedRefresh) {
        try {
          const refreshed = await refreshAccessToken(savedRefresh);
          setToken(refreshed.access);
          localStorage.setItem("atrium_token", refreshed.access);
          const current = await fetchCurrentUser(refreshed.access);
          setUser(current);
          localStorage.setItem("atrium_user", JSON.stringify(current));
        } catch (refreshErr) {
          console.warn("Session expired. Logging out cleanly:", refreshErr);
          logout();
        }
      }
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        refreshToken,
        login,
        logout,
        isAuthenticated: !!token,
        isSeller: !!(user?.is_seller || (user as any)?.role === "seller"),
        loginAsDemo,
        refreshUser,
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

