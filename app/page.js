"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  const [tab, setTab] = useState("login"); // login | register
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");
      
      localStorage.setItem("kavi_token", data.token);
      localStorage.setItem("kavi_user", JSON.stringify(data.user));
      router.push("/chat");
    } catch (err) {
      setError(err.message);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    if (password !== passwordConfirm) {
      return setError("Passwords do not match.");
    }
    try {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, display_name: displayName, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Registration failed");
      
      setSuccess("Account created successfully! You can now sign in.");
      setTab("login");
      setPassword("");
      setPasswordConfirm("");
    } catch (err) {
      setError(err.message);
    }
  };

  const pills = [
    "Weather & Forecast", "Email Management", "Google Calendar", 
    "Web Search", "Latest News", "Task Manager", "Code Executor", "Smart Reminders"
  ];

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#0a0a0a]">
      <div className="flex w-full max-w-[1200px] flex-col md:flex-row gap-8 px-6 py-12">
        {/* Left Side */}
        <div className="flex-1 flex flex-col justify-center py-12 px-4 md:px-12">
          <h1 className="text-5xl md:text-6xl font-bold text-white leading-tight mb-6 font-[family-name:var(--font-space-grotesk)]">
            Meet <span className="text-red-500">KAVI</span><br/>Your AI Assistant
          </h1>
          <p className="text-gray-400 text-lg leading-relaxed max-w-md mb-8">
            A multi-agent AI platform that handles your weather, emails,
            calendar, news, tasks, reminders, web search, and code execution —
            all through natural language.
          </p>
          <div className="flex flex-wrap gap-2">
            {pills.map((p, i) => (
              <span key={i} className="bg-red-600/10 border border-red-600/30 rounded-full px-3.5 py-1 text-xs text-red-400 font-medium font-[family-name:var(--font-inter)]">
                {p}
              </span>
            ))}
          </div>
        </div>

        {/* Right Side */}
        <div className="w-full md:w-[420px] shrink-0 bg-[#161616]/95 border border-white/10 rounded-3xl p-8 md:p-10 backdrop-blur-xl m-auto shadow-2xl">
          <div className="flex border-b border-white/10 mb-6 font-[family-name:var(--font-inter)]">
            <button 
              className={`flex-1 pb-3 text-sm font-medium transition-colors ${tab === 'login' ? 'text-red-500 border-b-2 border-red-500' : 'text-gray-500 hover:text-gray-300'}`}
              onClick={() => { setTab('login'); setError(''); setSuccess(''); }}
            >
              Sign In
            </button>
            <button 
              className={`flex-1 pb-3 text-sm font-medium transition-colors ${tab === 'register' ? 'text-red-500 border-b-2 border-red-500' : 'text-gray-500 hover:text-gray-300'}`}
              onClick={() => { setTab('register'); setError(''); setSuccess(''); }}
            >
              Create Account
            </button>
          </div>

          {error && <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-lg">{error}</div>}
          {success && <div className="mb-4 p-3 bg-green-500/10 border border-green-500/20 text-green-400 text-sm rounded-lg">{success}</div>}

          {tab === "login" ? (
            <div>
              <h2 className="text-2xl font-bold text-white mb-1 font-[family-name:var(--font-space-grotesk)]">Welcome Back</h2>
              <p className="text-gray-400 text-sm mb-6">Sign in to your KAVI account</p>
              <form onSubmit={handleLogin} className="flex flex-col gap-4 font-[family-name:var(--font-inter)]">
                <input 
                  type="text" 
                  placeholder="Username" 
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-red-500/50 focus:ring-1 focus:ring-red-500/20 transition-all"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required 
                />
                <input 
                  type="password" 
                  placeholder="Password" 
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-red-500/50 focus:ring-1 focus:ring-red-500/20 transition-all"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required 
                />
                <button type="submit" className="mt-2 w-full bg-red-600 hover:bg-red-500 text-white rounded-xl px-4 py-3 text-sm font-medium transition-colors">
                  Sign In
                </button>
              </form>
            </div>
          ) : (
            <div>
              <h2 className="text-2xl font-bold text-white mb-1 font-[family-name:var(--font-space-grotesk)]">Create Account</h2>
              <p className="text-gray-400 text-sm mb-6">Join KAVI — it's free</p>
              <form onSubmit={handleRegister} className="flex flex-col gap-4 font-[family-name:var(--font-inter)]">
                <input 
                  type="text" 
                  placeholder="Full Name" 
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-red-500/50 focus:ring-1 focus:ring-red-500/20 transition-all"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  required 
                />
                <input 
                  type="text" 
                  placeholder="Username" 
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-red-500/50 focus:ring-1 focus:ring-red-500/20 transition-all"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required 
                />
                <input 
                  type="password" 
                  placeholder="Password (min 6 chars)" 
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-red-500/50 focus:ring-1 focus:ring-red-500/20 transition-all"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required 
                />
                <input 
                  type="password" 
                  placeholder="Confirm Password" 
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-red-500/50 focus:ring-1 focus:ring-red-500/20 transition-all"
                  value={passwordConfirm}
                  onChange={(e) => setPasswordConfirm(e.target.value)}
                  required 
                />
                <button type="submit" className="mt-2 w-full bg-red-600 hover:bg-red-500 text-white rounded-xl px-4 py-3 text-sm font-medium transition-colors">
                  Create Account
                </button>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
