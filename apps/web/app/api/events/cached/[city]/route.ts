import { NextResponse } from 'next/server';
import { Redis } from '@upstash/redis';

const redis = new Redis({ url: process.env.UPSTASH_REDIS_URL!, token: process.env.UPSTASH_REDIS_TOKEN! });

export async function GET(_: Request, { params }: { params: { city: string } }) {
const city = params.city.toLowerCase();
const today = new Date().toISOString().slice(0, 10);
const cacheKey = events:${city}:${today};
const statusKey = status:${city}:lastUpdated;

const cached = await redis.get(cacheKey);
const lastUpdated = (await redis.get(statusKey)) as string | null;

if (cached) {
return NextResponse.json({ events: JSON.parse(cached as string), cached: true, lastUpdated });
}

await redis.lpush('scraping:queue', JSON.stringify({ city, ts: Date.now() }));
return NextResponse.json({ events: [], cached: false, lastUpdated });
}
