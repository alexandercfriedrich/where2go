'use client';

import { useEffect, useState } from 'react';
import { EventCard } from '../../components/EventCard';
import { LoadingSkeleton } from '../../components/LoadingSkeleton';

type Event = {
title: string;
category: string;
date: string;
time: string;
venue: string;
price: string;
website: string;
};

export default function CityPage({ params }: { params: { city: string } }) {
const [events, setEvents] = useState<Event[]>([]);
const [loading, setLoading] = useState(true);
const [bgLoading, setBgLoading] = useState(false);
const [lastUpdated, setLastUpdated] = useState<string>('');
const city = params.city;

useEffect(() => {
loadCached(city);
// eslint-disable-next-line react-hooks/exhaustive-deps
}, [city]);

async function loadCached(c: string) {
try {
setLoading(true);
const res = await fetch(/api/events/cached/${c});
if (!res.ok) throw new Error(API ${res.status});
const data = await res.json();

  setEvents(data.events || []);
  setLastUpdated(data.lastUpdated || '');
  setLoading(false);

  if (!data.cached || (data.events || []).length === 0) {
    refresh(c);
  }
} catch (err) {
  console.error('Failed to load cached events', err);
  setLoading(false);
}
  }

async function refresh(c: string) {
try {
setBgLoading(true);
await fetch(/api/events/cached/${c}, { cache: 'no-store' });
setTimeout(() => loadCached(c), 15000);
} catch (err) {
console.error('Background refresh failed', err);
} finally {
setBgLoading(false);
}
}

return (
<div className="max-w-6xl mx-auto p-6">
<div className="flex justify-between mb-6">
<h1 className="text-3xl font-bold capitalize">{city} Events</h1>
{bgLoading ? <span className="text-blue-600">Updating…</span> : null}
</div>
  );
}
