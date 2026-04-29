"""
ARIA — About page.
"""
import streamlit as st
from tools.navbar import render_navbar
from tools.auth_db import validate_session

st.set_page_config(page_title="ARIA — About", page_icon="🤖",
                   layout="wide", initial_sidebar_state="collapsed")

token = st.session_state.get("session_token")
user  = validate_session(token) if token else None
if not user:
    st.switch_page("app.py")
    st.stop()

render_navbar(user, active="about")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');
.page-body{max-width:900px;margin:0 auto;padding:16px 1.5rem 4rem}
.page-title{font-family:'Space Grotesk',sans-serif;font-size:1.8rem;font-weight:700;color:#f5f5f5;margin:0 0 .4rem}
.page-title em{color:#ef4444;font-style:normal}
.page-sub{font-size:15px;color:#888;margin:0 0 2rem;padding-bottom:1rem;border-bottom:1px solid rgba(255,255,255,.06)}
.sec-title{font-family:'Space Grotesk',sans-serif;font-size:1.1rem;font-weight:600;color:#f5f5f5;
    margin:2rem 0 1rem;padding-bottom:.5rem;border-bottom:1px solid rgba(255,255,255,.06)}
.agent-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:2rem}
.agent-card{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.07);
    border-radius:16px;padding:18px 20px;transition:border-color .2s}
.agent-card:hover{border-color:rgba(220,38,38,.3)}
.agent-hdr{display:flex;align-items:center;gap:10px;margin-bottom:10px}
.agent-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.agent-name{font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:600;color:#f5f5f5}
.agent-desc{font-size:14px;color:#888;line-height:1.6;margin-bottom:12px}
.ex-label{font-size:11px;font-weight:600;color:#444;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}
.ex-q{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);
    border-radius:8px;padding:7px 12px;font-size:13px;color:#777;margin:3px 0;font-style:italic}
.tech-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:2rem}
.tech-pill{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.07);
    border-radius:10px;padding:14px 16px;font-size:14px;color:#888}
.tech-pill strong{display:block;color:#e5e5e5;font-size:15px;margin-bottom:3px}
.arch-box{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.07);
    border-radius:16px;padding:20px 24px;font-size:14px;color:#777;
    line-height:1.9;font-family:'Courier New',monospace}
.arch-box strong{color:#ef4444}
.stButton>button{background:transparent!important;border:1px solid rgba(255,255,255,.1)!important;
    color:#888!important;border-radius:8px!important;font-family:'Inter',sans-serif!important;
    font-size:12px!important;font-weight:500!important;transition:all .15s!important}
.stButton>button:hover{border-color:rgba(220,38,38,.4)!important;color:#ef4444!important}
p,li{font-family:'Inter',sans-serif!important}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-body">', unsafe_allow_html=True)
st.markdown("""
<div class="page-title"><em>KAVI</em> — Artificial Reasoning & Intelligence Architecture</div>
<div class="page-sub">A multi-agent AI personal assistant built with Python, LangChain, and Groq LLM.
Each capability is handled by a dedicated agent — routed automatically from your natural language input.</div>
""", unsafe_allow_html=True)

st.markdown('<div class="sec-title">What ARIA Can Do</div>', unsafe_allow_html=True)

AGENTS = [
    {"name":"Weather Agent","color":"#38bdf8",
     "desc":"Real-time weather and 5-day forecasts. Understands follow-up questions and timezone context.",
     "ex":["What's the weather in Mumbai?","5-day forecast for London","Weather and forecast for Tokyo"]},
    {"name":"Search Agent","color":"#a78bfa",
     "desc":"Web searches via Tavily with AI-generated summary and ranked results with relevance scores.",
     "ex":["Search for LangChain multi-agent tutorials","Find best Python libraries for data science"]},
    {"name":"Email Agent","color":"#34d399",
     "desc":"Gmail via SMTP and IMAP. Send, read inbox, search by keyword or sender, read latest email, and reply.",
     "ex":["Send email to john@gmail.com saying meeting at 3pm","What did Rahul say in his last email?"]},
    {"name":"News Agent","color":"#fbbf24",
     "desc":"Latest news on any topic via Tavily. Returns AI summary plus articles with publish dates.",
     "ex":["Latest news on artificial intelligence","Cricket news today"]},
    {"name":"Calendar Agent","color":"#f472b6",
     "desc":"Google Calendar via OAuth2. Create, view, update, delete events. Detects timezones from your message.",
     "ex":["Schedule a team meeting tomorrow at 3pm","What are my events this week?"]},
    {"name":"Reminder Agent","color":"#fb923c",
     "desc":"Time-based reminders in SQLite. Overdue alerts and Telegram notifications at 9am daily.",
     "ex":["Remind me to call John at 5pm","Show my reminders"]},
    {"name":"Todo Agent","color":"#c084fc",
     "desc":"Task management with priority levels (high/normal/low), due dates, and per-user isolation.",
     "ex":["Add task submit assignment by Friday","Complete task 3"]},
    {"name":"Code Executor","color":"#22d3ee",
     "desc":"Generates or extracts Python code and runs it in a sandboxed subprocess. 10s timeout. Dangerous modules blocked.",
     "ex":["Run: print([x**2 for x in range(10)])","Write a fibonacci function and run it"]},
    {"name":"General Agent","color":"#4ade80",
     "desc":"Open-ended conversation, knowledge questions, and accurate math via AST-based calculator.",
     "ex":["What is the capital of France?","Calculate sqrt(144) + 2^10"]},
]

st.markdown('<div class="agent-grid">', unsafe_allow_html=True)
for a in AGENTS:
    exs = "".join(f'<div class="ex-q">"{e}"</div>' for e in a["ex"])
    st.markdown(f"""<div class="agent-card">
        <div class="agent-hdr">
            <div class="agent-dot" style="background:{a['color']};box-shadow:0 0 6px {a['color']}88"></div>
            <div class="agent-name">{a['name']}</div>
        </div>
        <div class="agent-desc">{a['desc']}</div>
        <div class="ex-label">Example questions</div>
        {exs}
    </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="sec-title">How It Works</div>', unsafe_allow_html=True)
st.markdown("""<div class="arch-box">
<strong>User message</strong> → <strong>Intent Parser</strong> (Groq LLM classifies intent)
→ <strong>Orchestrator</strong> (routes to correct agent)
→ <strong>Specialized Agent</strong> (calls API / runs logic)
→ <strong>Response</strong> (formatted output + agent badge)<br><br>
Memory is persisted per-user in SQLite. Conversation context is passed to every agent so follow-up questions work naturally.
</div>""", unsafe_allow_html=True)

st.markdown('<div class="sec-title">Tech Stack</div>', unsafe_allow_html=True)
st.markdown("""<div class="tech-grid">
    <div class="tech-pill"><strong>LLM</strong>Groq — llama-3.3-70b-versatile</div>
    <div class="tech-pill"><strong>Framework</strong>LangChain + Python 3.10+</div>
    <div class="tech-pill"><strong>UI</strong>Streamlit multi-page app</div>
    <div class="tech-pill"><strong>Database</strong>SQLite (users, memory, todos)</div>
    <div class="tech-pill"><strong>Weather</strong>OpenWeatherMap REST API</div>
    <div class="tech-pill"><strong>Search & News</strong>Tavily API</div>
    <div class="tech-pill"><strong>Email</strong>Gmail SMTP + IMAP</div>
    <div class="tech-pill"><strong>Calendar</strong>Google Calendar API v3</div>
    <div class="tech-pill"><strong>Notifications</strong>Telegram Bot + APScheduler</div>
</div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
