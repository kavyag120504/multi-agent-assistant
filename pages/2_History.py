"""
ARIA — History page.
"""
import streamlit as st
from collections import defaultdict
from datetime import datetime, date as dt_date
from tools.navbar import render_navbar
from tools.shared_styles import get_badge
from tools.auth_db import validate_session
from tools.user_memory_db import load_history, clear_history

st.set_page_config(page_title="ARIA — History", page_icon="🤖",
                   layout="wide", initial_sidebar_state="collapsed")

token = st.session_state.get("session_token")
user  = validate_session(token) if token else None
if not user:
    st.switch_page("app.py")
    st.stop()
user_id = user["id"]

render_navbar(user, active="history")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');
.page-body{max-width:820px;margin:0 auto;padding:16px 1.5rem 4rem}
.page-title{font-family:'Space Grotesk',sans-serif;font-size:1.6rem;font-weight:700;color:#f5f5f5;margin:0 0 .3rem}
.page-sub{font-size:15px;color:#666;margin:0 0 1.5rem;padding-bottom:1rem;border-bottom:1px solid rgba(255,255,255,.06)}
.date-label{font-size:12px;font-weight:600;color:#555;text-transform:uppercase;
    letter-spacing:1.5px;margin:1.5rem 0 .6rem;display:flex;align-items:center;gap:8px}
.date-label span{font-size:11px;color:#444;font-weight:400;text-transform:none;letter-spacing:0}
.hist-msg{display:flex;gap:10px;padding:10px 14px;border-radius:10px;
    margin:3px 0;border:1px solid transparent;align-items:flex-start}
.hist-msg.u{background:rgba(220,38,38,.05);border-color:rgba(220,38,38,.1);flex-direction:row-reverse}
.hist-msg.a{background:rgba(255,255,255,.02);border-color:rgba(255,255,255,.05)}
.hist-role{font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;
    flex-shrink:0;padding-top:2px;min-width:50px}
.hist-role.you{color:#ef4444;text-align:right}
.hist-role.aria{color:#555}
.hist-content{font-size:14px;color:#aaa;line-height:1.55;flex:1;word-break:break-word}
.hist-time{font-size:12px;color:#444;flex-shrink:0;padding-top:2px}
.agent-badge{display:inline-block;font-size:10px;font-family:'Inter',sans-serif;
    font-weight:600;letter-spacing:.5px;padding:2px 8px;border-radius:20px;
    margin-right:4px;text-transform:uppercase}
.badge-weather{background:rgba(14,165,233,.12);color:#38bdf8;border:1px solid rgba(14,165,233,.3)}
.badge-search{background:rgba(139,92,246,.12);color:#a78bfa;border:1px solid rgba(139,92,246,.3)}
.badge-email{background:rgba(16,185,129,.12);color:#34d399;border:1px solid rgba(16,185,129,.3)}
.badge-news{background:rgba(245,158,11,.12);color:#fbbf24;border:1px solid rgba(245,158,11,.3)}
.badge-calendar{background:rgba(236,72,153,.12);color:#f472b6;border:1px solid rgba(236,72,153,.3)}
.badge-reminder{background:rgba(249,115,22,.12);color:#fb923c;border:1px solid rgba(249,115,22,.3)}
.badge-todo{background:rgba(168,85,247,.12);color:#c084fc;border:1px solid rgba(168,85,247,.3)}
.badge-code{background:rgba(6,182,212,.12);color:#22d3ee;border:1px solid rgba(6,182,212,.3)}
.badge-general{background:rgba(34,197,94,.12);color:#4ade80;border:1px solid rgba(34,197,94,.3)}
.empty-hist{text-align:center;padding:5rem 2rem}
.empty-hist h3{font-family:'Space Grotesk',sans-serif;font-size:1.2rem;color:#333;margin-bottom:.5rem}
.empty-hist p{color:#444;font-size:13px}
.stButton>button{background:transparent!important;border:1px solid rgba(255,255,255,.1)!important;
    color:#888!important;border-radius:8px!important;font-family:'Inter',sans-serif!important;
    font-size:12px!important;font-weight:500!important;transition:all .15s!important}
.stButton>button:hover{border-color:rgba(220,38,38,.4)!important;color:#ef4444!important}
p,li{font-family:'Inter',sans-serif!important}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="page-body">', unsafe_allow_html=True)
st.markdown("""
<div class="page-title">Conversation History</div>
<div class="page-sub">Your full chat history — click Resume on any day to continue that session</div>
""", unsafe_allow_html=True)

history = load_history(user_id, limit=300)

if not history:
    st.markdown("""<div class="empty-hist">
        <h3>No history yet</h3>
        <p>Start a conversation and it will appear here.</p>
    </div>""", unsafe_allow_html=True)
else:
    grouped = defaultdict(list)
    for msg in history:
        dk = msg["created_at"][:10] if msg.get("created_at") else "Unknown"
        grouped[dk].append(msg)

    for dk in sorted(grouped.keys(), reverse=True):
        try:
            d = datetime.strptime(dk, "%Y-%m-%d").date()
            today = dt_date.today()
            label = "Today" if d==today else ("Yesterday" if (today-d).days==1 else d.strftime("%B %d, %Y"))
        except Exception:
            label = dk

        msgs = grouped[dk]
        st.markdown(f'<div class="date-label">{label} <span>· {len(msgs)} messages</span></div>',
                    unsafe_allow_html=True)

        for msg in msgs:
            role     = msg["role"]
            content  = msg["content"]
            intent   = msg.get("intent","")
            time_str = msg.get("created_at","")[-8:-3] if msg.get("created_at") else ""
            display  = content if len(content)<=200 else content[:200]+"..."
            badge_html = f'<span class="agent-badge badge-{intent}">{intent.upper()}</span>' if intent and role=="assistant" else ""

            if role=="user":
                st.markdown(f"""<div class="hist-msg u">
                    <div class="hist-role you">You</div>
                    <div class="hist-content">{display}</div>
                    <div class="hist-time">{time_str}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="hist-msg a">
                    <div class="hist-role aria">ARIA</div>
                    <div class="hist-content">{badge_html}{display}</div>
                    <div class="hist-time">{time_str}</div>
                </div>""", unsafe_allow_html=True)

        _, btn_col, _ = st.columns([3,2,3])
        with btn_col:
            if st.button(f"Resume {label}", key=f"res_{dk}", use_container_width=True):
                st.session_state.messages = [
                    {"role":m["role"],"content":m["content"],"intent":m.get("intent","general")}
                    for m in msgs
                ]
                st.switch_page("pages/1_Chat.py")

        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:rgba(255,255,255,.06);margin:1.5rem 0'>", unsafe_allow_html=True)
    with st.expander("Danger Zone — Delete all history"):
        st.warning("This permanently deletes your entire conversation history.")
        if st.button("Delete All History", type="primary"):
            clear_history(user_id)
            st.session_state.messages = []
            st.success("History cleared.")
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
