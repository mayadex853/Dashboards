/** @type {import('next').NextConfig} */
const nextConfig = {
  serverExternalPackages: ["pdf-lib"],
  experimental: { serverActions: { bodySizeLimit: "25mb" } },
};
export default nextConfig;
