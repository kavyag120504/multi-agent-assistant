/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    const isDev = process.env.NODE_ENV === "development";
    const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";
    
    // Always proxy /api/ to the python backend
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
