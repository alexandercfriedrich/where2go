/** @type {import('next').NextConfig} */
const nextConfig = {
experimental: { appDir: true },
env: {
UPSTASH_REDIS_URL: process.env.UPSTASH_REDIS_URL,
UPSTASH_REDIS_TOKEN: process.env.UPSTASH_REDIS_TOKEN,
VERCEL_AI_TOKEN: process.env.VERCEL_AI_TOKEN
},
async redirects() {
return [{ source: '/', destination: '/wien', permanent: false }];
}
};
module.exports = nextConfig;
