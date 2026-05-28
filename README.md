# KAVI AI Assistant 🚀

KAVI is a fully autonomous, multi-agent AI assistant designed not just to chat, but to actively orchestrate complex workflows, provide proactive insights, and execute natural language automations. 

This repository contains the latest version of KAVI, successfully migrated from a legacy Streamlit application to a highly scalable **Next.js (Frontend)** and **FastAPI (Backend)** architecture.

## ✨ Features

- **Multi-Agent Orchestrator:** Intelligent intent detection routes queries to 11 specialized agents (Weather, Calendar, Email, News, Web Search, Code Executor, etc.) and synthesizes their outputs for a cohesive response.
- **Mission Control (Explain Mode):** See exactly *how* KAVI answered your question with a futuristic UI trace showing which agents ran, execution times, and a confidence score.
- **Proactive Intelligence:** KAVI analyzes your data (e.g. pending tasks) and intelligently suggests actions directly inside your chat dashboard.
- **Natural Language Workflows:** Create complex automations using plain English (e.g., "Every Monday at 9AM, send me a summary of AI news").
- **Stateless JWT Auth:** Secure, fast, and scalable authentication.

## 🛠️ Tech Stack

- **Frontend**: Next.js (App Router), React, Tailwind CSS v4, Dark Glassmorphic Design.
- **Backend**: Python 3, FastAPI, LangChain, Groq LLaMA 3.
- **Database Architecture**: 
  - **Local Development**: SQLite (zero-config, out of the box).
  - **Production**: PostgreSQL (e.g., Neon or Supabase).

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
python -m uvicorn api.index:app --reload --port 8000
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

## 🌍 Production Deployment

Because KAVI utilizes a massive, heavy AI engine (LangChain, Google APIs, APScheduler), it exceeds the limits of standard serverless platforms for Python. We employ a **Decoupled Architecture** for production.

### Step 1: Deploy Backend to Render (Free)
1. In Render, create a new **Web Service** from this GitHub repository.
2. Render will automatically detect the `render.yaml` configuration file included in this repo.
3. Add your `DATABASE_URL`, `JWT_SECRET`, and `GROQ_API_KEY` to the Render Environment Variables.
4. Deploy, and copy your live Render URL (e.g., `https://kavi-backend.onrender.com`).

### Step 2: Deploy Frontend to Vercel
1. In Vercel, import this repository.
2. Add a new Environment Variable named `BACKEND_URL` and set its value to your live Render URL from Step 1.
3. Deploy! Next.js will build the UI and seamlessly proxy all API traffic to your powerful Render Python engine.

## 📁 Project Structure

```text
├── app/                  # Next.js Frontend Pages
│   ├── chat/             # Main Chat Interface & Mission Control
│   ├── workflows/        # NL Automations Interface
│   └── globals.css       # Global KAVI styling (Tailwind v4)
├── api/                  # FastAPI Backend Entrypoint
│   ├── index.py          # App instance
│   └── routers/          # API Endpoints (Auth, Chat, Workflows, Insights)
├── agents/               # 11 LLM Agents (Weather, Email, Code, Orchestrator, etc.)
├── tools/                # Database wrappers and AI utilities
├── render.yaml           # Infrastructure-as-code configuration for Render deployment
├── requirements.txt      # Python dependencies
└── package.json          # Node dependencies for Next.js
```

---
*Built as a showcase for advanced Agentic AI interactions.*
