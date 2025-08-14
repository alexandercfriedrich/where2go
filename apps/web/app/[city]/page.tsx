'use client';
import { useEffect, useState } from 'react';
import { EventCard } from '../../components/EventCard';
import { LoadingSkeleton } from '../../components/LoadingSkeleton';

type Event = {
title: string; category: string; date: string; time: string;
venue: string; price: string; website: string;
};

export default function CityPage({ params }: { params: { city: string } }) {
const [events, setEvents] = useState<Event[]>([]);
const [loading, setLoading] = useState(true);
const [bgLoading, setBgLoading] = useState(false);
const [lastUpdated, setLastUpdated] = useState<string>('');

useEffect(() => { loadCached(params.city); }, [params.city]);

async function loadCached(city: string) {
setLoading(true);
const res = await fetch(/api/events/cached/${city});
const data = await res.json();
setEvents(data.events || []);
setLastUpdated(data.lastUpdated || '');
setLoading(false);

text
if (!data.cached || (data.events || []).length === 0) {
  refresh(city);
}
}

async function refresh(city: string) {
setBgLoading(true);
await fetch(/api/events/cached/${city}, { cache: 'no-store' });
setTimeout(() => loadCached(city), 15000);
setBgLoading(false);
}

return (
<div className="max-w-6xl mx-auto p-6">
<div className="flex justify-between mb-6">
<h1 className="text-3xl font-bold capitalize">{params.city} Events</h1>
{bgLoading ? <span className="text-blue-600">Updating…</span> : null}
</div>
{loading ? (
<LoadingSkeleton />
) : events.length === 0 ? (
<div>Keine Events gefunden. Wird aktualisiert…</div>
) : (
<div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
{events.map((e, i) => <EventCard key={i} event={e} />)}
</div>
)}
{lastUpdated && (
<p className="text-gray-500 mt-4 text-sm">Last updated: {new Date(lastUpdated).toLocaleString()}</p>
)}
</div>
);
}
