"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";

import StatusMessage from "@/components/StatusMessage";
import { useAuth } from "@/context/AuthContext";
import api, { getApiErrorMessage } from "@/lib/api";
import type { TokenResponse } from "@/lib/types";


const inputClassName =
  "w-full border border-gray-300 rounded px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-500";


interface LoginClientProps {
  registered: boolean;
}


export default function LoginClient({ registered }: LoginClientProps) {
  const router = useRouter();
  const { isAuthenticated, isReady, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    if (registered) {
      setSuccessMessage("Account created successfully. Sign in to continue.");
    }
  }, [registered]);

  useEffect(() => {
    if (isReady && isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [isAuthenticated, isReady, router]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setLoading(true);
    setErrorMessage("");

    try {
      const response = await api.post<TokenResponse>("/api/v1/auth/login", { email, password });
      login(response.data.access_token, email);
      router.replace("/dashboard");
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, "Sign in failed."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 px-4">
      <div className="max-w-sm mx-auto mt-20 bg-white border border-gray-200 rounded p-8">
        <h1 className="text-xl font-semibold text-gray-900">Sign in</h1>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label htmlFor="email" className="text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className={`${inputClassName} mt-1`}
              placeholder="user@example.com"
              required
            />
          </div>
          <div>
            <label htmlFor="password" className="text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className={`${inputClassName} mt-1`}
              placeholder="Enter your password"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
          {errorMessage ? <p className="text-sm text-red-600">{errorMessage}</p> : null}
        </form>

        <div className="mt-4 space-y-3">
          {successMessage ? (
            <StatusMessage type="success" message={successMessage} onClose={() => setSuccessMessage("")} />
          ) : null}
          <p className="text-sm text-gray-600">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="text-blue-600">
              Register
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
