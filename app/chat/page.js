"use client";

import { useState, useEffect, useRef } from "react";
import Navbar from "../../components/Navbar";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [insights, setInsights] = useState([]);
  const [expandedMsg, setExpandedMsg] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const userData = localStorage.getItem("kavi_user");
    if (userData) setUser(JSON.parse(userData));
    
    // Fetch insights on load
    const fetchInsights = async () => {
      try {
        const res = await fetch("/api/insights", {
          headers: { "Authorization": `Bearer ${localStorage.getItem("kavi_token")}` }
        });
        if (res.ok) {
          const data = await res.json();
          setInsights(data.insights || []);
        }
      } catch (e) {
        console.error("Failed to load insights", e);
      }
    };
    fetchInsights();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    const userMsg = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("kavi_token")}`
        },
        body: JSON.stringify({ message: userMsg.content }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Error");
      
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: data.response, 
        intent: data.intent,
        confidence: data.confidence,
        agent_runs: data.agent_runs
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: "⚠️ Something went wrong: " + err.message, intent: "error" }]);
    } finally {
      setLoading(false);
    }
  };

  const dismissInsight = async (id) => {
    try {
      await fetch(`/api/insights/${id}/dismiss`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${localStorage.getItem("kavi_token")}` }
      });
      setInsights(prev => prev.filter(i => i.id !== id));
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex flex-col relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-red-900/10 blur-[120px] rounded-full pointer-events-none"></div>
      
      <Navbar />
      
      <main className="flex-1 w-full max-w-[820px] mx-auto px-6 pt-6 pb-32 z-10">
        
        {/* Proactive Insights Panel */}
        {insights.length > 0 && (
          <div className="mb-8">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-3">Proactive Insights</h3>
            <div className="flex flex-col gap-3">
              {insights.map(insight => (
                <div key={insight.id} className="bg-[#141414]/90 border border-red-900/30 backdrop-blur-xl rounded-2xl p-4 flex justify-between items-start group shadow-lg shadow-black/50">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                      <h4 className="text-white font-[family-name:var(--font-space-grotesk)] font-semibold">{insight.title}</h4>
                    </div>
                    <p className="text-gray-400 text-sm leading-relaxed">{insight.description}</p>
                  </div>
                  <div className="flex flex-col gap-2 shrink-0 ml-4">
                    <button className="text-xs font-medium bg-red-600/10 hover:bg-red-600/20 text-red-400 border border-red-600/20 rounded-lg px-3 py-1.5 transition-colors">
                      {insight.suggested_action}
                    </button>
                    <button onClick={() => dismissInsight(insight.id)} className="text-xs text-gray-600 hover:text-gray-400">Dismiss</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {messages.length === 0 ? (
          <div className="text-center pt-16 pb-8">
            <h2 className="font-[family-name:var(--font-space-grotesk)] text-4xl font-bold text-white mb-3 tracking-tight">
              KAVI <span className="text-red-500 font-light">Autonomous Platform</span>
            </h2>
            <p className="text-gray-400 mb-12 text-[15px]">Multi-agent orchestration and workflow automation.</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
              <div className="bg-white/[0.02] border border-white/[0.05] hover:border-red-600/30 transition-all rounded-2xl p-5 cursor-pointer">
                <div className="text-white font-medium mb-1 flex items-center gap-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                  Multi-Agent Queries
                </div>
                <div className="text-sm text-gray-500">"Am I free tomorrow and what's the weather there?"</div>
              </div>
              <div className="bg-white/[0.02] border border-white/[0.05] hover:border-red-600/30 transition-all rounded-2xl p-5 cursor-pointer">
                <div className="text-white font-medium mb-1 flex items-center gap-2">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                  Proactive Automation
                </div>
                <div className="text-sm text-gray-500">"Every morning at 8am, send me a news summary."</div>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-8">
            {messages.map((msg, i) => (
              <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                <div className="flex max-w-[85%] gap-3">
                  {msg.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-red-600 flex items-center justify-center shrink-0 text-white text-xs font-bold font-[family-name:var(--font-space-grotesk)] mt-1 shadow-[0_0_15px_rgba(220,38,38,0.4)]">
                      A
                    </div>
                  )}
                  
                  <div className="flex flex-col w-full">
                    <div className={`
                      text-[15px] leading-relaxed px-5 py-3.5 shadow-sm
                      ${msg.role === 'user' 
                        ? 'bg-red-600 text-white rounded-[20px] rounded-tr-[4px]' 
                        : 'bg-[#151515] border border-white/[0.08] text-gray-200 rounded-[20px] rounded-tl-[4px]'
                      }
                    `}>
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    </div>

                    {/* Meta Data & Mission Control for Assistant Messages */}
                    {msg.role === 'assistant' && (
                      <div className="mt-2 flex items-center gap-3 ml-2">
                        {/* Confidence Badge */}
                        {msg.confidence && (
                          <div className={`flex items-center gap-1.5 text-[11px] font-semibold px-2 py-0.5 rounded-md border ${msg.confidence >= 80 ? 'bg-green-500/10 text-green-400 border-green-500/20' : msg.confidence >= 50 ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
                            {msg.confidence}% Confident
                          </div>
                        )}
                        
                        {/* Explain Button */}
                        {msg.agent_runs && msg.agent_runs.length > 0 && (
                          <button 
                            onClick={() => setExpandedMsg(expandedMsg === i ? null : i)}
                            className="text-[11px] text-gray-500 hover:text-white transition-colors flex items-center gap-1"
                          >
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
                            {expandedMsg === i ? 'Hide Trace' : 'Explain Mode'}
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Agent Trace Drawer (Mission Control) */}
                {msg.role === 'assistant' && expandedMsg === i && msg.agent_runs && (
                  <div className="mt-4 ml-11 w-full max-w-[85%] bg-[#0f0f0f] border border-red-900/20 rounded-2xl p-5 shadow-inner">
                    <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>
                      Mission Control Trace
                    </h4>
                    <div className="flex flex-col gap-3 relative before:absolute before:inset-0 before:ml-[11px] before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-red-500/20 before:to-transparent">
                      {msg.agent_runs.map((run, idx) => (
                        <div key={idx} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                          <div className="flex items-center justify-center w-6 h-6 rounded-full border-2 border-[#0f0f0f] bg-red-600/20 text-red-500 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-[0_0_10px_rgba(220,38,38,0.3)] z-10">
                            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12"/></svg>
                          </div>
                          <div className="w-[calc(100%-2.5rem)] md:w-[calc(50%-1.5rem)] bg-white/[0.02] border border-white/5 p-3 rounded-xl hover:border-red-500/30 transition-colors">
                            <div className="flex justify-between items-center mb-1">
                              <span className={`badge badge-${run.agent} mb-0`}>{run.agent}</span>
                              <span className="text-[10px] text-gray-500 font-mono">{run.execution_time_ms}ms</span>
                            </div>
                            <div className="text-xs text-gray-400 break-words line-clamp-2" title={run.summary}>
                              {run.summary}
                            </div>
                          </div>
                        </div>
                      ))}
                      <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                          <div className="flex items-center justify-center w-6 h-6 rounded-full border-2 border-[#0f0f0f] bg-gray-800 text-gray-400 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                          </div>
                          <div className="w-[calc(100%-2.5rem)] md:w-[calc(50%-1.5rem)] bg-white/[0.02] border border-white/5 p-3 rounded-xl">
                            <div className="text-[11px] font-semibold text-gray-300 mb-0.5">Synthesis Engine</div>
                            <div className="text-[10px] text-gray-500">Combining {msg.agent_runs.length} agent outputs</div>
                          </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
            
            {/* Loading State */}
            {loading && (
              <div className="flex max-w-[85%] gap-3">
                <div className="w-8 h-8 rounded-full bg-red-600/50 flex items-center justify-center shrink-0 text-white text-xs font-bold font-[family-name:var(--font-space-grotesk)] mt-1 animate-pulse">
                  A
                </div>
                <div className="bg-[#151515] border border-white/[0.08] rounded-[20px] rounded-tl-[4px] px-5 py-4 flex gap-1.5 items-center">
                  <span className="text-xs text-gray-400 mr-2">Orchestrating agents</span>
                  <span className="w-1 h-1 bg-red-500 rounded-full animate-bounce"></span>
                  <span className="w-1 h-1 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></span>
                  <span className="w-1 h-1 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {/* Input Area */}
      <div className="fixed bottom-0 left-0 w-full bg-[#0a0a0a]/95 backdrop-blur-xl border-t border-white/5 py-4 px-6 z-40">
        <div className="max-w-[820px] mx-auto">
          <form onSubmit={handleSubmit} className="relative">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask KAVI to coordinate multiple tasks..." 
              className="w-full bg-[#111] border border-white/10 hover:border-red-600/30 focus:border-red-600/60 focus:ring-4 focus:ring-red-600/10 rounded-2xl pl-5 pr-12 py-3.5 text-[15px] text-white placeholder-gray-500 outline-none transition-all shadow-lg shadow-black"
              disabled={loading}
            />
            <button 
              type="submit" 
              disabled={!input.trim() || loading}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2.5 bg-red-600 text-white rounded-xl hover:bg-red-500 disabled:opacity-0 transition-all shadow-md shadow-red-900/50"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
