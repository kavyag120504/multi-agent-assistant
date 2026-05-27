"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Navbar from "../../components/Navbar";

export default function History() {
  const [historyGroups, setHistoryGroups] = useState({});
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch("/api/chat/history", {
          headers: { "Authorization": `Bearer ${localStorage.getItem("kavi_token")}` }
        });
        if (res.ok) {
          const data = await res.json();
          // Group by date
          const groups = {};
          data.history.forEach(msg => {
            const dateStr = msg.created_at ? msg.created_at.substring(0, 10) : "Unknown";
            if (!groups[dateStr]) groups[dateStr] = [];
            groups[dateStr].push(msg);
          });
          setHistoryGroups(groups);
        }
      } catch (e) {
        console.error("Failed to load history", e);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  const handleClearHistory = async () => {
    if (!confirm("This permanently deletes your entire conversation history. Are you sure?")) return;
    try {
      const res = await fetch("/api/chat/history", {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${localStorage.getItem("kavi_token")}` }
      });
      if (res.ok) {
        setHistoryGroups({});
      }
    } catch (e) {
      console.error(e);
    }
  };

  const sortedDates = Object.keys(historyGroups).sort().reverse();

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex flex-col">
      <Navbar />
      <main className="flex-1 w-full max-w-[820px] mx-auto px-6 py-8">
        <h1 className="font-[family-name:var(--font-space-grotesk)] text-2xl font-bold text-white mb-1">Conversation History</h1>
        <p className="text-gray-500 text-[15px] mb-8 pb-4 border-b border-white/[0.06]">Your full chat history — review past conversations</p>
        
        {loading ? (
          <div className="text-center py-20 text-gray-500">Loading history...</div>
        ) : sortedDates.length === 0 ? (
          <div className="text-center py-24">
            <h3 className="font-[family-name:var(--font-space-grotesk)] text-xl text-gray-300 mb-2">No history yet</h3>
            <p className="text-gray-500 text-sm">Start a conversation and it will appear here.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-8">
            {sortedDates.map(date => (
              <div key={date}>
                <div className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-4 flex items-center gap-2">
                  {date} <span className="text-[11px] font-normal tracking-normal text-gray-600 capitalize">· {historyGroups[date].length} messages</span>
                </div>
                <div className="flex flex-col gap-1.5">
                  {historyGroups[date].map((msg, idx) => {
                    const timeStr = msg.created_at ? msg.created_at.substring(11, 16) : "";
                    const isUser = msg.role === 'user';
                    return (
                      <div key={idx} className={`flex gap-3 px-4 py-3 rounded-xl border ${isUser ? 'bg-red-600/5 border-red-600/10 flex-row-reverse' : 'bg-white/[0.02] border-white/5'}`}>
                        <div className={`text-[11px] font-semibold uppercase tracking-wider shrink-0 pt-0.5 min-w-[50px] ${isUser ? 'text-red-500 text-right' : 'text-gray-500'}`}>
                          {isUser ? 'You' : 'KAVI'}
                        </div>
                        <div className="flex-1 text-sm text-gray-300 leading-relaxed break-words">
                          {!isUser && msg.intent && (
                            <span className={`badge badge-${msg.intent} mr-2`}>{msg.intent}</span>
                          )}
                          {msg.content.length > 200 ? msg.content.substring(0, 200) + "..." : msg.content}
                        </div>
                        <div className="text-xs text-gray-600 shrink-0 pt-0.5">{timeStr}</div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}

            <div className="mt-12 pt-8 border-t border-white/[0.06]">
              <div className="bg-[#111] border border-red-900/30 rounded-xl p-5">
                <h3 className="text-red-400 font-medium mb-1">Danger Zone</h3>
                <p className="text-gray-500 text-sm mb-4">This permanently deletes your entire conversation history.</p>
                <button 
                  onClick={handleClearHistory}
                  className="bg-red-600 hover:bg-red-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
                >
                  Delete All History
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
