export function LoadingSkeleton() {
return (
<div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
{Array.from({ length: 6 }).map((_, i) => (
<div key={i} className="bg-white border rounded-lg p-5 animate-pulse">
<div className="h-4 w-24 bg-gray-200 rounded mb-3" />
<div className="h-5 w-3/4 bg-gray-200 rounded mb-2" />
<div className="h-4 w-1/2 bg-gray-200 rounded mb-4" />
<div className="flex justify-between">
<div className="h-4 w-16 bg-gray-200 rounded" />
<div className="h-4 w-20 bg-gray-200 rounded" />
</div>
</div>
))}
</div>
);
}
