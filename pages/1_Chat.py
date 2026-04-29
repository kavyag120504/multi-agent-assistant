"""
ARIA — Chat page.
"""
import streamlit as st
import re
from datetime import date
from tools.navbar import render_navbar
from tools.shared_styles import get_badge
from tools.auth_db import validate_session
from tools.todo_db import get_tasks
from agents.orchestrator_agent import run_assistant, clear_memory
from agents.code_agent import _check_safety, _run_code

st.set_page_config(page_title="ARIA — Chat", page_icon="🤖",
                   layout="wide", initial_sidebar_state="collapsed")

token = st.session_state.get("session_token")
user  = validate_session(token) if token else None
if not user:
    st.switch_page("app.py")
    st.stop()
user_id = user["id"]

for k, v in [("messages",[]),("total_queries",0),("agents_used",{}),
              ("editor_code",""),("editor_open",False),("editor_output","")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Navbar ────────────────────────────────────────────────────────────────────
render_navbar(user, active="chat")

# ── Page CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');

.page-body{max-width:820px;margin:0 auto;padding:8px 1.5rem 5rem}
.overdue{background:rgba(220,38,38,.07);border:1px solid rgba(220,38,38,.2);
    border-radius:10px;padding:9px 14px;font-size:13px;color:#f87171;margin-bottom:1rem}
.empty{text-align:center;padding:3rem 1rem 2rem}
.empty h2{font-family:'Space Grotesk',sans-serif;font-size:2.4rem;font-weight:700;
    color:#f5f5f5;margin-bottom:.4rem}
.empty h2 em{color:#ef4444;font-style:normal}
.empty p{color:#666;font-size:16px;margin-bottom:2rem}
.cap-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;text-align:left}
.cap-card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);
    border-radius:14px;padding:18px;transition:border-color .2s}
.cap-card:hover{border-color:rgba(220,38,38,.3)}
.cap-title{font-family:'Space Grotesk',sans-serif;font-size:15px;font-weight:600;
    color:#e5e5e5;margin-bottom:5px}
.cap-desc{font-size:13px;color:#666;line-height:1.5}
.row-user{display:flex;justify-content:flex-end;margin:10px 0}
.row-asst{display:flex;justify-content:flex-start;margin:10px 0;gap:10px;align-items:flex-start}
.bub-user{background:#dc2626;border-radius:18px 18px 4px 18px;padding:12px 18px;
    max-width:68%;color:#fff;font-size:15px;line-height:1.55;font-family:'Inter',sans-serif}
.bub-asst{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);
    border-radius:4px 18px 18px 18px;padding:14px 18px;max-width:72%;
    color:#e5e5e5;font-size:15px;line-height:1.6;font-family:'Inter',sans-serif}
.av{width:32px;height:32px;border-radius:50%;background:#dc2626;display:flex;
    align-items:center;justify-content:center;flex-shrink:0;
    font-size:13px;font-weight:700;color:#fff;font-family:'Space Grotesk',sans-serif}
.dots{display:flex;gap:5px;padding:6px 2px}
.dots span{width:6px;height:6px;border-radius:50%;background:#dc2626;animation:dot 1.2s infinite}
.dots span:nth-child(2){animation-delay:.2s;opacity:.7}
.dots span:nth-child(3){animation-delay:.4s;opacity:.5}
@keyframes dot{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-7px)}}
.agent-badge{display:inline-block;font-size:10px;font-family:'Inter',sans-serif;
    font-weight:600;letter-spacing:.5px;padding:2px 10px;border-radius:20px;
    margin-bottom:5px;text-transform:uppercase}
.badge-weather{background:rgba(14,165,233,.12);color:#38bdf8;border:1px solid rgba(14,165,233,.3)}
.badge-search{background:rgba(139,92,246,.12);color:#a78bfa;border:1px solid rgba(139,92,246,.3)}
.badge-email{background:rgba(16,185,129,.12);color:#34d399;border:1px solid rgba(16,185,129,.3)}
.badge-news{background:rgba(245,158,11,.12);color:#fbbf24;border:1px solid rgba(245,158,11,.3)}
.badge-calendar{background:rgba(236,72,153,.12);color:#f472b6;border:1px solid rgba(236,72,153,.3)}
.badge-reminder{background:rgba(249,115,22,.12);color:#fb923c;border:1px solid rgba(249,115,22,.3)}
.badge-todo{background:rgba(168,85,247,.12);color:#c084fc;border:1px solid rgba(168,85,247,.3)}
.badge-code{background:rgba(6,182,212,.12);color:#22d3ee;border:1px solid rgba(6,182,212,.3)}
.badge-general{background:rgba(34,197,94,.12);color:#4ade80;border:1px solid rgba(34,197,94,.3)}
[data-testid="stBottom"],[data-testid="stBottom"]>div,
[data-testid="stBottom"]>div>div,[data-testid="stBottom"]>div>div>div,
[data-testid="stBottom"] section,[data-testid="stBottom"] form{
    background:#0a0a0a!important;border-top:none!important}
[data-testid="stChatInput"]{background:rgba(255,255,255,.06)!important;
    border:1px solid rgba(220,38,38,.2)!important;border-radius:14px!important}
[data-testid="stChatInput"]:focus-within{border-color:rgba(220,38,38,.5)!important;
    box-shadow:0 0 0 2px rgba(220,38,38,.12)!important}
[data-testid="stChatInput"] textarea{background:transparent!important;color:#111!important;
    caret-color:#ef4444!important;font-family:'Inter',sans-serif!important;font-size:14px!important}
[data-testid="stChatInput"] textarea::placeholder{color:#555!important}
[data-testid="stBottom"]>div{max-width:820px!important;margin:0 auto!important;padding:10px 1.5rem!important}
.code-panel{background:rgba(255,255,255,.03);border:1px solid rgba(220,38,38,.25);
    border-radius:14px;padding:16px;margin:1rem 0}
.code-out{background:#050505;border:1px solid rgba(255,255,255,.06);border-radius:10px;
    padding:12px 14px;font-family:'Courier New',monospace;font-size:13px;
    color:#4ade80;margin-top:10px;white-space:pre-wrap}
.code-err{background:#050505;border:1px solid rgba(220,38,38,.3);border-radius:10px;
    padding:12px 14px;font-family:'Courier New',monospace;font-size:13px;
    color:#f87171;margin-top:10px;white-space:pre-wrap}
.stButton>button{background:transparent!important;
    border:1px solid rgba(255,255,255,.1)!important;color:#888!important;
    border-radius:8px!important;font-family:'Inter',sans-serif!important;
    font-size:12px!important;font-weight:500!important;transition:all .15s!important}
.stButton>button:hover{border-color:rgba(220,38,38,.4)!important;color:#ef4444!important}
p,li{font-family:'Inter',sans-serif!important}
</style>
""", unsafe_allow_html=True)

# ── Page body ─────────────────────────────────────────────────────────────────
st.markdown('<div class="page-body">', unsafe_allow_html=True)

try:
    pending = get_tasks("pending", user_id=user_id)
    today   = str(date.today())
    overdue = [t for t in pending if t["due_date"] and t["due_date"] < today]
    if overdue:
        names = " · ".join(f"#{t['id']} {t['task']}" for t in overdue)
        st.markdown(f'<div class="overdue">Overdue: {names}</div>', unsafe_allow_html=True)
except Exception:
    pass

if not st.session_state.messages:
    first = user['display_name'].split()[0]
    st.markdown(f"""
    <div class="empty">
        <h2>Hello, <em>{first}</em></h2>
        <p>What can I help you with today?</p>
        <div class="cap-grid">
            <div class="cap-card"><div class="cap-title">Weather</div><div class="cap-desc">Current + 5-day forecast for any city</div></div>
            <div class="cap-card"><div class="cap-title">Web Search</div><div class="cap-desc">AI-summarised results with relevance scoring</div></div>
            <div class="cap-card"><div class="cap-title">Email</div><div class="cap-desc">Send, read, search and reply to Gmail</div></div>
            <div class="cap-card"><div class="cap-title">News</div><div class="cap-desc">Latest headlines with AI summary</div></div>
            <div class="cap-card"><div class="cap-title">Calendar</div><div class="cap-desc">Create, view, update and delete events</div></div>
            <div class="cap-card"><div class="cap-title">Tasks & Reminders</div><div class="cap-desc">Todos with priorities and Telegram alerts</div></div>
            <div class="cap-card"><div class="cap-title">Code Executor</div><div class="cap-desc">Run Python in a secure sandbox</div></div>
            <div class="cap-card"><div class="cap-title">General AI</div><div class="cap-desc">Math, knowledge and conversation</div></div>
            <div class="cap-card"><div class="cap-title">Context Memory</div><div class="cap-desc">History persisted — never lost</div></div>
        </div>
    </div>""", unsafe_allow_html=True)

def _extract_code(text):
    m = re.search(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else None

for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(f'<div class="row-user"><div class="bub-user">{msg["content"]}</div></div>',
                    unsafe_allow_html=True)
    else:
        badge  = get_badge(msg.get("intent","general"))
        intent = msg.get("intent","general")
        st.markdown(f"""<div class="row-asst">
            <div class="av">A</div>
            <div style="flex:1;min-width:0">{badge}
                <div class="bub-asst">{msg["content"]}</div>
            </div></div>""", unsafe_allow_html=True)
        if intent == "code":
            snippet = _extract_code(msg["content"])
            if snippet and st.button("Open in Code Editor", key=f"ce_{i}"):
                st.session_state.editor_code   = snippet
                st.session_state.editor_open   = True
                st.session_state.editor_output = ""
                st.rerun()

if st.session_state.editor_open:
    st.markdown('<div class="code-panel">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:12px;font-weight:600;color:#ef4444;margin-bottom:8px">Code Editor</div>',
                unsafe_allow_html=True)
    edited = st.text_area("", value=st.session_state.editor_code, height=180,
                           key="code_area", label_visibility="collapsed")
    r1, r2 = st.columns([1,6])
    with r1:
        if st.button("Run", type="primary", key="run_btn"):
            err = _check_safety(edited)
            if err:
                st.session_state.editor_output = f"BLOCKED: {err}"
            else:
                out, serr = _run_code(edited, timeout=10)
                st.session_state.editor_code   = edited
                st.session_state.editor_output = out or serr or "(no output)"
            st.rerun()
    with r2:
        if st.button("Close", key="close_btn"):
            st.session_state.editor_open   = False
            st.session_state.editor_output = ""
            st.rerun()
    if st.session_state.editor_output:
        is_err = any(x in st.session_state.editor_output for x in ["BLOCKED","Error","Traceback"])
        st.markdown(f'<div class="{"code-err" if is_err else "code-out"}">{st.session_state.editor_output}</div>',
                    unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Message ARIA..."):
    st.session_state.messages.append({"role":"user","content":prompt})
    st.session_state.total_queries += 1
    with st.spinner(""):
        st.markdown("""<div class="row-asst"><div class="av">A</div>
            <div class="bub-asst"><div class="dots"><span></span><span></span><span></span></div></div>
        </div>""", unsafe_allow_html=True)
        response, intent = run_assistant(prompt, user_id=user_id)
    st.session_state.agents_used[intent] = st.session_state.agents_used.get(intent,0)+1
    st.session_state.messages.append({"role":"assistant","content":response,"intent":intent})
    st.rerun()
