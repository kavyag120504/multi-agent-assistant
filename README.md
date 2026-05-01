# KAVI - Multi-Agent AI Personal Assistant

KAVI (formerly ARIA) is a production-grade multi-agent AI personal assistant built with Python, LangChain, and Groq LLM. It takes natural language input, classifies the intent, and routes the task to the correct specialized agent. Each agent handles a distinct capability and calls the appropriate API or service.

---

## Overview

Most people manage daily tasks across 5-10 separate apps. KAVI consolidates weather, email, calendar, news, web search, task management, reminders, and code execution into a single conversational interface. You type what you want in plain English and the right agent handles it automatically.

---

## Agents

**Weather Agent**
Fetches real-time weather and 5-day forecasts using OpenWeatherMap. Understands follow-up questions and timezone context.

**Search Agent**
Performs web searches via Tavily and returns an AI-generated summary with ranked results and relevance scores.

**Email Agent**
Connects to Gmail via SMTP and IMAP. Supports sending, reading inbox, searching by keyword or sender, reading the latest email from a specific person, and replying.

**News Agent**
Fetches latest news on any topic via Tavily with advanced search depth. Returns an AI-generated summary plus articles with publish dates.

**Calendar Agent**
Manages Google Calendar via OAuth2. Supports creating, viewing, updating, and deleting events. Detects timezones from natural language.

**Reminder Agent**
Sets time-based reminders stored in SQLite per user. Shows overdue alerts on the chat page and sends Telegram notifications daily.

**Todo Agent**
Full task management with priority levels (high, normal, low), due dates, and per-user data isolation via SQLite.

**Code Executor**
Extracts or generates Python code from natural language and runs it in a sandboxed subprocess with a 10-second timeout. Dangerous modules are blocked before execution.

**General Agent**
Handles open-ended conversation, knowledge questions, and accurate math using an AST-based safe calculator. Uses conversation memory for context.

---

## Architecture

```
User message
    -> Intent Parser (Groq LLM classifies intent)
    -> Orchestrator (routes to correct agent)
    -> Specialized Agent (calls API or runs logic)
    -> Response (formatted output with agent badge)
```

Conversation context (last 6 messages) is passed to every agent so follow-up questions work naturally across sessions.

---

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python 3.10+ |
| LLM | Groq API - LLaMA 3.3 70B Versatile |
| AI Framework | LangChain, langchain-groq |
| UI | Streamlit (multi-page) |
| Database | SQLite (users, sessions, memory, todos, reminders) |
| Weather | OpenWeatherMap REST API |
| Search and News | Tavily API |
| Email | Gmail SMTP + IMAP |
| Calendar | Google Calendar API v3 (OAuth2) |
| Notifications | Telegram Bot API + APScheduler |
| Security | SHA-256 + random salt password hashing, 32-byte session tokens |
| Environment | python-dotenv |

---

## Features

- Multi-user authentication with secure password hashing and session management
- Persistent conversation memory per user that survives page refreshes and restarts
- Per-user data isolation across todos, reminders, and chat history
- Conversation history page with per-date resume functionality
- Interactive Python code editor with sandbox execution and output display
- Daily Telegram notifications at 9am for overdue and due-today tasks
- Multi-page UI with fixed navbar (Chat, History, About)
- Dark red theme with glassmorphism styling

---

## Project Structure

```
multi_agent_assistant/
    agents/
        orchestrator_agent.py    routes intent to correct agent
        weather_agent.py         OpenWeatherMap API
        search_agent.py          Tavily web search
        email_agent.py           Gmail SMTP + IMAP
        news_agent.py            Tavily news search
        general_agent.py         LLM general chat and math
        calendar_agent.py        Google Calendar API
        reminder_agent.py        SQLite-based reminders
        todo_agent.py            SQLite-based task manager
        code_agent.py            Sandboxed Python executor
    tools/
        llm_client.py            Groq LLM singleton
        intent_parser.py         Classifies user intent
        memory.py                Per-user conversation memory
        auth_db.py               User authentication and sessions
        user_memory_db.py        Persistent conversation history
        todo_db.py               Todo storage with user isolation
        telegram_notifier.py     Telegram message sender
        reminder_scheduler.py    APScheduler daily job
        navbar.py                Shared navbar component
        shared_styles.py         Shared CSS utilities
    pages/
        1_Chat.py                Main chat interface
        2_History.py             Conversation history with resume
        3_About.py               Agent documentation
    app.py                       Entry point - login and register
    requirements.txt
    .env                         API keys (never commit)
    .gitignore
```

---

## Setup

**1. Clone the repository**

```bash
git clone https://github.com/kavyag120504/multi-agent-assistant
cd multi-agent-assistant
```

**2. Create and activate virtual environment**

```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_key
OPENWEATHER_API_KEY=your_openweather_key
TAVILY_API_KEY=your_tavily_key
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_PASSWORD=your_gmail_app_password
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
REMINDER_HOUR=9
REMINDER_MINUTE=0
USER_TIMEZONE=Asia/Kolkata
```

**5. Google Calendar setup**

Download `credentials.json` from Google Cloud Console (Calendar API enabled) and place it in the project root. The OAuth2 flow will create `token.json` on first use.

**6. Run the application**

```bash
streamlit run app.py
```

---

## Environment Variables

| Variable | Description |
|---|---|
| GROQ_API_KEY | Groq API key for LLaMA inference |
| OPENWEATHER_API_KEY | OpenWeatherMap API key |
| TAVILY_API_KEY | Tavily search API key |
| EMAIL_ADDRESS | Gmail address |
| EMAIL_PASSWORD | Gmail App Password (not account password) |
| TELEGRAM_BOT_TOKEN | Telegram bot token from BotFather |
| TELEGRAM_CHAT_ID | Your Telegram chat ID |
| REMINDER_HOUR | Hour for daily Telegram notification (default 9) |
| REMINDER_MINUTE | Minute for daily Telegram notification (default 0) |
| USER_TIMEZONE | Default timezone (default Asia/Kolkata) |

---

## Security Notes

- Never commit `.env`, `credentials.json`, or `token.json` to version control
- All three are listed in `.gitignore`
- SQLite database files (`*.db`) are also excluded as they contain user data
- Passwords are hashed with SHA-256 and a random 32-byte salt before storage
- The code executor blocks dangerous imports (os, sys, subprocess, socket, requests, etc.) before running any code

---

## GitHub

https://github.com/kavyag120504/multi-agent-assistant
