"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const userData = localStorage.getItem("kavi_user");
    if (userData) {
      setUser(JSON.parse(userData));
    } else {
      router.push("/");
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("kavi_token");
    localStorage.removeItem("kavi_user");
    router.push("/");
  };

  if (!user) return null;

  return (
    <nav className="sticky top-0 z-50 bg-[#0a0a0a]/90 backdrop-blur-md border-b border-white/5">
      <div className="max-w-[820px] mx-auto px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="font-[family-name:var(--font-space-grotesk)] text-lg font-bold text-white tracking-wide">
            KAVI <span className="text-red-500">v2.0</span>
          </div>
          <div className="flex items-center gap-1 font-[family-name:var(--font-inter)] text-sm">
            <Link href="/chat" className={`px-3 py-1.5 rounded-lg transition-colors ${pathname === '/chat' ? 'text-white bg-white/5 font-medium' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}>
              Chat
            </Link>
            <Link href="/history" className={`px-3 py-1.5 rounded-lg transition-colors ${pathname === '/history' ? 'text-white bg-white/5 font-medium' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}>
              History
            </Link>
            <Link href="/workflows" className={`px-3 py-1.5 rounded-lg transition-colors ${pathname === '/workflows' ? 'text-white bg-white/5 font-medium' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}>
              Automations
            </Link>
            <Link href="/about" className={`px-3 py-1.5 rounded-lg transition-colors ${pathname === '/about' ? 'text-white bg-white/5 font-medium' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}>
              About
            </Link>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-400 hidden sm:block">
            {user.display_name}
          </div>
          <button 
            onClick={handleLogout}
            className="text-xs font-medium text-gray-400 hover:text-red-400 px-3 py-1.5 rounded-lg border border-white/10 hover:border-red-500/30 transition-all bg-transparent"
          >
            Sign Out
          </button>
        </div>
      </div>
    </nav>
  );
}
