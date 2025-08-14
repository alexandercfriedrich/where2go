import './globals.css';
export const metadata = {
title: 'WHERE2GO',
description: 'Find events worldwide'
};
export default function RootLayout({ children }: { children: React.ReactNode }) {
return (
<html lang="de">
<body>
<nav className="border-b bg-white/90 backdrop-blur">
<div className="max-w-6xl mx-auto px-4 py-3 flex justify-between">
<a href="/wien" className="font-bold text-blue-600">WHERE2GO</a>
<a href="/cities" className="text-gray-600">Cities</a>
</div>
</nav>
<main className="bg-gray-50 min-h-screen">{children}</main>
</body>
</html>
);
}

