# Multi-Agent AI Personal Assistant

A modular, multi-agent AI assistant that understands natural language and executes real-world tasks by coordinating specialized agents — built with Python, LangChain, and Groq (free LLM API).

---

##  Problem Statement

Modern digital assistants struggle to execute complex, multi-step tasks across different services in a seamless way. Most systems rely on a single centralized model, which limits their ability to specialize, scale, and coordinate efficiently.

This project solves that by building a **multi-agent architecture** where each agent is a specialist, and an orchestrator routes tasks intelligently.

---

##  Features

- **Orchestrator Agent** — understands user intent and delegates to the right agent
- **Weather Agent** — fetches real-time weather using OpenWeatherMap API
- **Search Agent** — performs web searches using Tavily API
- **Email Agent** — sends emails via SMTP (no OAuth required)
- **Chat UI** — clean conversational interface built with Streamlit

---

##  Architecture

```
User Input (Streamlit UI)
        │
        ▼
Orchestrator Agent  ◄── LLM (Groq / Gemini)
        │
   ┌────┴─────────────┐
   ▼         ▼        ▼
Weather    Search   Email
 Agent     Agent    Agent
   │         │        │
   ▼         ▼        ▼
OpenWeather Tavily   SMTP
   API       API    Server
```

---

## Project Structure

```
multi_agent_assistant/
│
├── agents/
│   ├── orchestrator_agent.py   # Routes user query to correct agent
│   ├── weather_agent.py        # Handles weather queries
│   ├── search_agent.py         # Handles web search queries
│   └── email_agent.py          # Handles email sending
│
├── tools/
│   ├── llm_client.py           # Connects to Groq/Gemini LLM
│   └── intent_parser.py        # Parses user intent from query
│
├── ui/
│   └── app.py                  # Streamlit chat interface
│
├── .env                        # API keys (not committed to GitHub)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/multi-agent-assistant.git
cd multi-agent-assistant
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up API keys

Create a `.env` file in the root folder:
```
GROQ_API_KEY=your_groq_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
TAVILY_API_KEY=your_tavily_api_key
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

> All APIs used have a **free tier** — no credit card required.

### 5. Run the app
```bash
streamlit run ui/app.py
```

---

## API Keys (All Free)

| Service | Purpose | Free Tier |
|---|---|---|
| [Groq](https://console.groq.com) | LLM brain | Yes |
| [OpenWeatherMap](https://openweathermap.org/api) | Weather data | Yes |
| [Tavily](https://tavily.com) | Web search | Yes |
| Gmail SMTP | Send emails | Yes |

---

## Example Queries

| User Says | Agent Used |
|---|---|
| "What's the weather in Delhi?" | Weather Agent |
| "Search for latest AI news" | Search Agent |
| "Send an email to john@example.com saying hello" | Email Agent |
| "What's the temperature in Mumbai and email it to me?" | Orchestrator → Weather + Email |

---

## Tech Stack

- **Python 3.10+**
- **LangChain** — agent framework
- **Groq API** — fast, free LLM (Llama 3)
- **Streamlit** — chat UI
- **OpenWeatherMap API** — weather data
- **Tavily API** — web search
- **SMTP** — email sending

---

## Future Improvements

- Add a Calendar Agent (Google Calendar integration)
- Add memory so the assistant remembers past conversations
- Deploy to Hugging Face Spaces or Streamlit Cloud
- Add voice input support

---

##  Author

**Your Name**
- GitHub: [Kavya Goswami](https://github.com/kavya120504)
- LinkedIn:(https://www.linkedin.com/in/kavya-goswami-39a8442ab/)

---

##  License

MIT License — free to use and modify.
