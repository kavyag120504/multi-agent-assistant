import Navbar from "../../components/Navbar";

export default function About() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] flex flex-col">
      <Navbar />
      <main className="flex-1 w-full max-w-[820px] mx-auto px-6 py-12">
        <h1 className="font-[family-name:var(--font-space-grotesk)] text-4xl font-bold text-white mb-6">About KAVI</h1>
        <div className="text-gray-300 leading-relaxed space-y-6 text-sm">
          <p>
            KAVI v2.0 is an autonomous AI agent platform designed to proactively manage 
            your workflows and assist with complex multi-step queries. 
          </p>
          <div className="bg-[#111] border border-white/10 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white mb-4 font-[family-name:var(--font-space-grotesk)]">Architecture Highlights</h2>
            <ul className="list-disc list-inside space-y-2 text-gray-400">
              <li><strong>Frontend:</strong> Next.js App Router with React Server Components, Tailwind CSS, and Framer Motion for smooth micro-animations.</li>
              <li><strong>Backend:</strong> FastAPI deployed on Vercel Serverless Functions. Python is executed entirely on the edge.</li>
              <li><strong>Database:</strong> Dual support for SQLite (local dev) and PostgreSQL (production).</li>
              <li><strong>Auth:</strong> Secure JWT-based stateless authentication.</li>
              <li><strong>AI Engine:</strong> LangChain + LLaMA 3 for deterministic routing and intent classification.</li>
            </ul>
          </div>
          <p>
            Built by a solo engineer with a vision to automate workflows seamlessly.
          </p>
        </div>
      </main>
    </div>
  );
}
