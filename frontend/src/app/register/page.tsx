"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState, type FormEvent } from "react";

import { useAuth } from "@/context/AuthContext";
import api, { getApiErrorMessage } from "@/lib/api";


const inputClassName =
  "w-full border border-gray-300 rounded px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-500";


export default function RegisterPage() {
  const router = useRouter();
  const { isAuthenticated, isReady } = useAuth();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

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
      await api.post("/api/v1/auth/register", { username, email, password });
      router.push("/login?registered=1");
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, "Registration failed."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 px-4">
      <div className="max-w-sm mx-auto mt-20 bg-white border border-gray-200 rounded p-8">
        <h1 className="text-xl font-semibold text-gray-900">Create account</h1>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label htmlFor="username" className="text-sm font-medium text-gray-700">
              Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className={`${inputClassName} mt-1`}
              placeholder="kanish"
              required
            />
          </div>
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
              placeholder="StrongPass123!"
              required
              minLength={8}
              pattern="(?=.*[A-Z])(?=.*\d).{8,}"
              title="Password must be at least 8 characters long and include one uppercase letter and one number."
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white text-sm font-medium px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {loading ? "Creating account..." : "Create account"}
          </button>
          {errorMessage ? <p className="text-sm text-red-600">{errorMessage}</p> : null}
        </form>

        <p className="mt-4 text-sm text-gray-600">
          Already have an account?{" "}
          <Link href="/login" className="text-blue-600">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
