type Event = { title: string; category: string; date: string; time: string; venue: string; price: string; website: string; };
export function EventCard({ event }: { event: Event }) {
return (
<div className="bg-white border rounded-lg p-5 shadow-sm">
<div className="flex items-center justify-between mb-2">
<span className="text-xs px-2 py-1 bg-gray-100 rounded-full">{event.category}</span>
<div className="text-right text-sm">
<div className="font-semibold">{event.date}</div>
<div className="text-gray-500">{event.time}</div>
</div>
</div>
<h3 className="font-semibold mb-2">{event.title}</h3>
<div className="text-sm text-gray-600 mb-3">📍 {event.venue}</div>
<div className="flex items-center justify-between">
<span className="font-medium">{event.price || 'auf Anfrage'}</span>
{event.website && (
<a href={event.website} target="_blank" className="text-blue-600 hover:underline">Details →</a>
)}
</div>
</div>
);
}
