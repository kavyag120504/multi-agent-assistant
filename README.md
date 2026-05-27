# KAVI AI Assistant 🚀

KAVI is a fully autonomous, multi-agent AI assistant designed not just to chat, but to actively orchestrate complex workflows, provide proactive insights, and execute natural language automations. 

This repository contains the latest version of KAVI, successfully migrated from a legacy Streamlit application to a highly scalable **Next.js (Frontend)** and **FastAPI (Backend)** architecture, fully optimized for single-repo deployment on Vercel.

## ✨ Features

- **Multi-Agent Orchestrator:** Intelligent intent detection routes queries to specialized agents (Weather, Calendar, Email, News, Web Search, Code Executor) and synthesizes their outputs for a cohesive response.
- **Mission Control (Explain Mode):** See exactly *how* KAVI answered your question with a futuristic UI trace showing which agents ran, execution times, and a confidence score.
- **Proactive Intelligence:** KAVI analyzes your data (e.g. pending tasks) and intelligently suggests actions directly inside your chat dashboard.
- **Natural Language Workflows:** Create complex automations using plain English (e.g., "Every Monday at 9AM, send me a summary of AI news").
- **Stateless JWT Auth:** Secure, fast, and scalable authentication.

## 🛠️ Tech Stack

- **Frontend**: Next.js (App Router), React, Tailwind CSS v4, Dark Glassmorphic Design.
- **Backend**: Python 3, FastAPI, LangChain, Groq LLaMA 3.3.
- **Database Architecture**: 
  - **Local Development**: SQLite (zero-config, out of the box).
  - **Production**: PostgreSQL (required for Vercel's Serverless environment).

## 🚀 Setup & Local Execution

You will need two terminal windows to run KAVI locally.

### 1. Backend Setup (Terminal 1)
```bash
# Create and activate a virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server on port 8000
python -m uvicorn api.index:app --reload
```

### 2. Frontend Setup (Terminal 2)
```bash
# Install node modules
npm install

# Start the Next.js development server
npm run dev
```

Visit `http://localhost:3000` to interact with KAVI. The frontend will automatically proxy API requests to your local FastAPI server.

## 🔑 Environment Variables

Create a `.env` file in the root directory (this file is git-ignored for safety). You can use the provided `.env.example` as a template.

```env
GROQ_API_KEY=your_groq_api_key
JWT_SECRET=your_super_secret_jwt_key
# DATABASE_URL=postgresql://user:password@host:port/dbname
```
*Note: Do not commit your real `.env` file or any `token.json` credentials.*

## 🌍 Vercel Deployment

This repository is built as a Vercel-ready monorepo. When you push this to GitHub and import it into Vercel, it automatically builds the Next.js frontend and maps the `api/` folder to Python Serverless Functions.

### Important Deployment Steps:
1. Push this code to your GitHub repository.
2. In Vercel, click **Add New Project** and import your repository.
3. In the deployment settings, configure the following **Environment Variables**:
   - `GROQ_API_KEY`
   - `JWT_SECRET`
   - `DATABASE_URL` (Required! Vercel uses an ephemeral filesystem, meaning local SQLite files reset instantly. Provide a Postgres connection string like Neon or Supabase to persist your data).
4. Click **Deploy**. Vercel will handle the rest!

## 📁 Project Structure

```text
├── app/                  # Next.js Frontend Pages
│   ├── chat/             # Main Chat Interface & Mission Control
│   ├── workflows/        # NL Automations Interface
│   └── globals.css       # Global KAVI styling (Tailwind v4)
├── api/                  # FastAPI Backend Entrypoint
│   ├── index.py          # Serverless app instance
│   └── routers/          # API Endpoints (Auth, Chat, Workflows, Insights)
├── agents/               # LLM Agents (Weather, Email, Orchestrator, etc.)
├── tools/                # Database wrappers and utilities
├── requirements.txt      # Python dependencies for Vercel
└── package.json          # Node dependencies for Next.js
```

---
*Built as a showcase for advanced Agentic AI interactions.*
