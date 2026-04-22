"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { clearStoredAuth, getStoredEmail, getStoredToken, setStoredAuth } from "@/lib/api";
import type { DecodedAccessToken } from "@/lib/types";


interface AuthContextValue {
  isAuthenticated: boolean;
  isReady: boolean;
  token: string | null;
  user: DecodedAccessToken | null;
  login: (accessToken: string, email: string) => void;
  logout: () => void;
}


const AuthContext = createContext<AuthContextValue | undefined>(undefined);


function decodeAccessToken(token: string): DecodedAccessToken | null {
  try {
    const [, payload] = token.split(".");
    if (!payload) {
      return null;
    }

    const normalizedPayload = payload.replace(/-/g, "+").replace(/_/g, "/");
    const paddedPayload = normalizedPayload.padEnd(Math.ceil(normalizedPayload.length / 4) * 4, "=");
    const decoded = JSON.parse(window.atob(paddedPayload)) as DecodedAccessToken;
    if (decoded.type !== "access") {
      return null;
    }

    return decoded;
  } catch {
    return null;
  }
}


function isExpired(payload: DecodedAccessToken): boolean {
  return payload.exp * 1000 <= Date.now();
}


export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<DecodedAccessToken | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const storedToken = getStoredToken();
    const storedEmail = getStoredEmail();

    if (!storedToken) {
      setIsReady(true);
      return;
    }

    const decoded = decodeAccessToken(storedToken);
    if (!decoded || isExpired(decoded)) {
      clearStoredAuth();
      setIsReady(true);
      return;
    }

    setToken(storedToken);
    setUser({ ...decoded, email: storedEmail ?? undefined });
    setIsReady(true);
  }, []);

  const login = (accessToken: string, email: string) => {
    const decoded = decodeAccessToken(accessToken);
    if (!decoded || isExpired(decoded)) {
      throw new Error("Received an invalid access token.");
    }

    setStoredAuth(accessToken, email);
    setToken(accessToken);
    setUser({ ...decoded, email });
  };

  const logout = () => {
    clearStoredAuth();
    setToken(null);
    setUser(null);

    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  };

  const value: AuthContextValue = {
    isAuthenticated: Boolean(token && user),
    isReady,
    token,
    user,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}


export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider.");
  }

  return context;
}
