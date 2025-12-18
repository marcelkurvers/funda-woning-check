import { useState, useEffect } from 'react';

interface AIStatus {
    provider: string;
    model: string;
    status: 'online' | 'offline';
}

export function AIStatusIndicator() {
    const [status, setStatus] = useState<AIStatus | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchStatus() {
            try {
                const res = await fetch('/api/ai/status');
                if (res.ok) {
                    const data = await res.json();
                    setStatus(data);
                }
            } catch (err) {
                console.error('Failed to fetch AI status', err);
            } finally {
                setLoading(false);
            }
        }

        fetchStatus();
        // Poll every 30 seconds
        const interval = setInterval(fetchStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading && !status) return null;

    const isOnline = status?.status === 'online';

    return (
        <div className="flex items-center gap-3 px-4 py-2 bg-white rounded-xl border border-slate-200 shadow-sm transition-all hover:shadow-md">
            <div className="flex items-center justify-center relative">
                <div className={`w-3.5 h-3.5 rounded-full ${isOnline ? 'bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]' : 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.5)]'} transition-colors duration-500`}></div>
                {isOnline && <div className="absolute inset-0 w-3.5 h-3.5 rounded-full bg-emerald-500 animate-ping opacity-20"></div>}
            </div>

            <div className="flex flex-col">
                <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase font-bold tracking-[0.1em] text-slate-500">
                        {status?.provider || 'AI Engine'}
                    </span>
                    {isOnline ? (
                        <span className="flex items-center gap-1 text-[9px] font-bold text-emerald-600 bg-emerald-50 px-1.5 rounded-sm">
                            ONLINE
                        </span>
                    ) : (
                        <span className="flex items-center gap-1 text-[9px] font-bold text-red-600 bg-red-50 px-1.5 rounded-sm">
                            OFFLINE
                        </span>
                    )}
                </div>
                <div className="text-sm font-bold text-slate-800 tracking-tight leading-tight">
                    {status?.model || 'Connecting...'}
                </div>
            </div>
        </div>
    );
}
