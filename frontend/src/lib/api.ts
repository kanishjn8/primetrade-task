import axios from "axios";


const ACCESS_TOKEN_STORAGE_KEY = "taskmanager_access_token";
const USER_EMAIL_STORAGE_KEY = "taskmanager_user_email";


export interface ApiErrorData {
  detail?: string;
  errors?: Record<string, string>;
}


const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
});


api.interceptors.request.use((config) => {
  if (typeof window === "undefined") {
    return config;
  }

  const token = getStoredToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});


api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      clearStoredAuth();
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }

    return Promise.reject(error);
  },
);


export function setStoredAuth(accessToken: string, email: string): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, accessToken);
  window.localStorage.setItem(USER_EMAIL_STORAGE_KEY, email);
}


export function clearStoredAuth(): void {
  if (typeof window === "undefined") {
    return;
  }

  window.localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
  window.localStorage.removeItem(USER_EMAIL_STORAGE_KEY);
}


export function getStoredToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);
}


export function getStoredEmail(): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  return window.localStorage.getItem(USER_EMAIL_STORAGE_KEY);
}


export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError<ApiErrorData>(error)) {
    return error.response?.data?.detail ?? fallback;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return fallback;
}


export function getApiFieldErrors(error: unknown): Record<string, string> {
  if (axios.isAxiosError<ApiErrorData>(error)) {
    return error.response?.data?.errors ?? {};
  }

  return {};
}


export default api;
