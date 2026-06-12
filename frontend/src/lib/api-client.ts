import axios from "axios";

// In the browser, default to a relative URL: requests go to the same origin
// that served the app, and Next.js rewrites proxy them to the backend. This
// works from any device (phones included) without the client needing the
// backend's address. On the server (SSR), axios requires an absolute URL, so
// fall back to the backend's internal address.
// NEXT_PUBLIC_API_URL can still override this for split deployments.
const defaultBaseURL =
  typeof window === "undefined"
    ? `${process.env.BACKEND_INTERNAL_URL || "http://localhost:8000"}/api/v1`
    : "/api/v1";

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || defaultBaseURL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.request.use(
  async (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      // Don't redirect if we're on an auth page (login, register, etc.)
      const url = error.config?.url || "";
      const isAuthEndpoint = url.includes("/auth/login") || url.includes("/auth/register") || url.includes("/auth/refresh");
      if (!isAuthEndpoint) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
