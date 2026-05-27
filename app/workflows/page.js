"use client";

import { useState, useEffect } from "react";
import Navbar from "../../components/Navbar";

export default function Workflows() {
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [nlInput, setNlInput] = useState("");
  const [creating, setCreating] = useState(false);
  const [runStatus, setRunStatus] = useState({});

  const fetchWorkflows = async () => {
    try {
      const res = await fetch("/api/workflows", {
        headers: { "Authorization": `Bearer ${localStorage.getItem("kavi_token")}` }
      });
      if (res.ok) {
        const data = await res.json();
        setWorkflows(data.workflows);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!nlInput.trim()) return;
    setCreating(true);
    
    try {
      const res = await fetch("/api/workflows", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("kavi_token")}`
        },
        body: JSON.stringify({ nl_description: nlInput }),
      });
      if (res.ok) {
        setNlInput("");
        fetchWorkflows();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setCreating(false);
    }
  };

  const toggleStatus = async (id, currentStatus) => {
    try {
      const res = await fetch(`/api/workflows/${id}`, {
        method: "PUT",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("kavi_token")}`
        },
        body: JSON.stringify({ enabled: !currentStatus }),
      });
      if (res.ok) {
        setWorkflows(workflows.map(w => w.id === id ? { ...w, enabled: !currentStatus ? 1 : 0 } : w));
      }
    } catch (e) {
      console.error(e);
    }
  };

  const deleteWorkflow = async (id) => {
    if (!confirm("Delete this workflow?")) return;
    try {
      await fetch(`/api/workflows/${id}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${localStorage.getItem("kavi_token")}` }
      });
      setWorkflows(workflows.filter(w => w.id !== id));
    } catch (e) {
      console.error(e);
    }
  };

  const manualRun = async (id) => {
    setRunStatus(prev => ({ ...prev, [id]: "running" }));
    try {
      const res = await fetch(`/api/workflows/${id}/run`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${localStorage.getItem("kavi_token")}` }
      });
      if (res.ok) {
        setRunStatus(prev => ({ ...prev, [id]: "success" }));
        setTimeout(() => setRunStatus(prev => ({ ...prev, [id]: null })), 3000);
      } else {
        setRunStatus(prev => ({ ...prev, [id]: "failed" }));
      }
    } catch (e) {
      setRunStatus(prev => ({ ...prev, [id]: "failed" }));
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] flex flex-col">
      <Navbar />
      <main className="flex-1 w-full max-w-[820px] mx-auto px-6 py-10">
        <h1 className="font-[family-name:var(--font-space-grotesk)] text-3xl font-bold text-white mb-2">Automations</h1>
        <p className="text-gray-400 mb-8">Manage natural language workflows. For Vercel Serverless, these run manually.</p>
        
        {/* Create Form */}
        <div className="bg-[#111] border border-red-900/30 rounded-2xl p-6 mb-10 shadow-lg">
          <h2 className="text-white font-medium mb-4">Create New Workflow</h2>
          <form onSubmit={handleCreate} className="flex gap-3">
            <input 
              type="text" 
              value={nlInput}
              onChange={(e) => setNlInput(e.target.value)}
              placeholder="e.g., 'Every Monday at 9AM, send me a summary of AI news'"
              className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-red-500/50"
              disabled={creating}
            />
            <button 
              type="submit" 
              disabled={!nlInput.trim() || creating}
              className="bg-red-600 text-white rounded-xl px-6 py-3 text-sm font-medium hover:bg-red-500 disabled:opacity-50 transition-colors shrink-0"
            >
              {creating ? "Creating..." : "Create"}
            </button>
          </form>
        </div>

        {/* List */}
        <div className="flex flex-col gap-4">
          {loading ? (
            <div className="text-center text-gray-500 py-10">Loading workflows...</div>
          ) : workflows.length === 0 ? (
            <div className="text-center text-gray-500 py-10 border border-white/5 rounded-2xl border-dashed">
              No workflows found. Create one above!
            </div>
          ) : (
            workflows.map(wf => (
              <div key={wf.id} className={`bg-[#141414] border ${wf.enabled ? 'border-white/10' : 'border-white/5 opacity-60'} rounded-2xl p-5 transition-all`}>
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="text-white font-semibold font-[family-name:var(--font-space-grotesk)]">{wf.title}</h3>
                    <div className="text-xs text-gray-500 font-mono mt-1">
                      {wf.schedule && <span className="bg-white/5 px-2 py-0.5 rounded mr-2">🕒 {wf.schedule}</span>}
                      {wf.condition && <span className="bg-red-500/10 text-red-400 border border-red-500/20 px-2 py-0.5 rounded">⚡ {wf.condition}</span>}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <button 
                      onClick={() => toggleStatus(wf.id, wf.enabled)}
                      className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${wf.enabled ? 'bg-red-600' : 'bg-gray-700'}`}
                    >
                      <span className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${wf.enabled ? 'translate-x-5' : 'translate-x-1'}`} />
                    </button>
                    <button onClick={() => deleteWorkflow(wf.id)} className="text-gray-600 hover:text-red-500 transition-colors">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                    </button>
                  </div>
                </div>
                
                <div className="bg-black/30 border border-white/5 rounded-lg p-3 text-sm text-gray-300">
                  <span className="text-gray-500 uppercase text-[10px] font-bold tracking-wider mr-2">Action</span>
                  {wf.action}
                </div>

                <div className="mt-4 flex justify-end">
                  <button 
                    onClick={() => manualRun(wf.id)}
                    disabled={!wf.enabled || runStatus[wf.id] === 'running'}
                    className="text-xs font-medium bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-lg px-4 py-2 transition-colors flex items-center gap-2 disabled:opacity-50"
                  >
                    {runStatus[wf.id] === 'running' ? (
                      <><span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span> Running...</>
                    ) : runStatus[wf.id] === 'success' ? (
                      <><span className="text-green-500">✓</span> Success</>
                    ) : runStatus[wf.id] === 'failed' ? (
                      <><span className="text-red-500">✗</span> Failed</>
                    ) : (
                      <><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="5 3 19 12 5 21 5 3"/></svg> Run Now (Serverless)</>
                    )}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}
