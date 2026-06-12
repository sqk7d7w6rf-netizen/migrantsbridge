/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // Proxy API calls through the frontend origin so clients (browsers,
    // mobile devices) never need direct network access to the backend.
    // BACKEND_INTERNAL_URL is the server-to-server address of the API
    // (e.g. http://backend:8000 in docker compose, http://localhost:8000 locally).
    const backendUrl = process.env.BACKEND_INTERNAL_URL || "http://localhost:8000";
    return [
      {
        source: "/api/v1/:path*",
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
