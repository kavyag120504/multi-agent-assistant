"""
Shared CSS theme for all ARIA pages.
Dark background + crimson/red accent — matches the uploaded design reference.
Import and call inject_styles() at the top of every page.
"""
import streamlit as st


THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ── Design tokens ── */
:root {
    --bg:           #0d0d0d;
    --bg-card:      #161616;
    --bg-card2:     #1e1e1e;
    --border:       rgba(255,255,255,0.08);
    --border-red:   rgba(220,38,38,0.4);
    --red:          #dc2626;
    --red-bright:   #ef4444;
    --red-glow:     rgba(220,38,38,0.25);
    --red-subtle:   rgba(220,38,38,0.08);
    --text:         #f5f5f5;
    --text-muted:   #888;
    --text-dim:     #555;
    --white:        #ffffff;
    --radius:       12px;
    --radius-lg:    20px;
    --font:         'Inter', sans-serif;
    --font-head:    'Space Grotesk', sans-serif;
}

/* ── Reset & base ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
}

/* Subtle red gradient background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 0% 0%,   rgba(180,10,10,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 100% 100%, rgba(120,0,0,0.12) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}
[data-testid="stMain"] { position: relative; z-index: 1; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #111 !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"]::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--red), transparent);
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ── Streamlit nav (multi-page) ── */
[data-testid="stSidebarNav"] {
    padding-top: 0.5rem;
}
[data-testid="stSidebarNav"] a {
    color: var(--text-muted) !important;
    font-family: var(--font) !important;
    font-size: 14px !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNav"] a[aria-selected="true"] {
    background: var(--red-subtle) !important;
    color: var(--red-bright) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--border-red) !important;
    color: var(--red-bright) !important;
    border-radius: var(--radius) !important;
    font-family: var(--font) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 20px !important;
    transition: all 0.2s !important;
    letter-spacing: 0.3px !important;
}
.stButton > button:hover {
    background: var(--red-subtle) !important;
    border-color: var(--red-bright) !important;
    box-shadow: 0 0 16px var(--red-glow) !important;
}
.stButton > button[kind="primary"] {
    background: var(--red) !important;
    color: white !important;
    border-color: var(--red) !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--red-bright) !important;
    box-shadow: 0 0 24px var(--red-glow) !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 14px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--red) !important;
    box-shadow: 0 0 0 2px var(--red-glow) !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--red) !important;
    box-shadow: 0 0 0 2px var(--red-glow) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tab"] {
    font-family: var(--font) !important;
    font-size: 14px !important;
    color: var(--text-muted) !important;
    border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--red-bright) !important;
    border-bottom-color: var(--red-bright) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--red); }

/* ── Agent badges ── */
.agent-badge {
    display: inline-block;
    font-size: 10px;
    font-family: var(--font);
    font-weight: 600;
    letter-spacing: 0.5px;
    padding: 2px 10px;
    border-radius: 20px;
    margin-bottom: 5px;
    text-transform: uppercase;
}
.badge-weather  { background: rgba(14,165,233,0.12);  color: #38bdf8; border: 1px solid rgba(14,165,233,0.3); }
.badge-search   { background: rgba(139,92,246,0.12);  color: #a78bfa; border: 1px solid rgba(139,92,246,0.3); }
.badge-email    { background: rgba(16,185,129,0.12);  color: #34d399; border: 1px solid rgba(16,185,129,0.3); }
.badge-news     { background: rgba(245,158,11,0.12);  color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
.badge-calendar { background: rgba(236,72,153,0.12);  color: #f472b6; border: 1px solid rgba(236,72,153,0.3); }
.badge-reminder { background: rgba(249,115,22,0.12);  color: #fb923c; border: 1px solid rgba(249,115,22,0.3); }
.badge-todo     { background: rgba(168,85,247,0.12);  color: #c084fc; border: 1px solid rgba(168,85,247,0.3); }
.badge-code     { background: rgba(6,182,212,0.12);   color: #22d3ee; border: 1px solid rgba(6,182,212,0.3); }
.badge-general  { background: rgba(34,197,94,0.12);   color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }

/* ── Chat bubbles ── */
.msg-row-user {
    display: flex;
    justify-content: flex-end;
    margin: 12px 0;
}
.msg-row-assistant {
    display: flex;
    justify-content: flex-start;
    margin: 12px 0;
    gap: 10px;
    align-items: flex-start;
}
.bubble-user {
    background: var(--red);
    border-radius: 18px 18px 4px 18px;
    padding: 11px 16px;
    max-width: 68%;
    color: #fff;
    font-size: 14px;
    line-height: 1.55;
    font-family: var(--font);
}
.bubble-assistant {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 4px 18px 18px 18px;
    padding: 12px 16px;
    max-width: 72%;
    color: var(--text);
    font-size: 14px;
    line-height: 1.6;
    font-family: var(--font);
}
.aria-avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    background: var(--red);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-size: 15px;
    font-weight: 700;
    color: white;
    font-family: var(--font-head);
    box-shadow: 0 0 12px var(--red-glow);
}

/* ── Thinking dots ── */
.thinking { display: flex; gap: 5px; padding: 6px 2px; }
.thinking span {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--red); animation: tdot 1.2s infinite;
}
.thinking span:nth-child(2) { animation-delay: 0.2s; opacity: 0.7; }
.thinking span:nth-child(3) { animation-delay: 0.4s; opacity: 0.5; }
@keyframes tdot {
    0%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-7px); }
}

/* ── Cards ── */
.aria-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 20px;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.aria-card:hover {
    border-color: var(--border-red);
    box-shadow: 0 4px 24px var(--red-glow);
}

/* ── Sidebar nav items ── */
.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 12px;
    border-radius: var(--radius);
    margin: 2px 0;
    cursor: pointer;
    font-size: 13px;
    color: var(--text-muted);
    transition: all 0.15s;
    text-decoration: none;
}
.nav-item:hover { background: var(--red-subtle); color: var(--text); }
.nav-item.active { background: var(--red-subtle); color: var(--red-bright); }

/* ── Stat pill ── */
.stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-card2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
    color: var(--text-muted);
}
.stat-pill strong { color: var(--text); font-size: 14px; }

p, li { font-family: var(--font) !important; }
</style>
"""


def inject_styles():
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def get_badge(intent: str) -> str:
    labels = {
        "weather":  "Weather",
        "search":   "Search",
        "email":    "Email",
        "news":     "News",
        "calendar": "Calendar",
        "reminder": "Reminder",
        "todo":     "Todo",
        "code":     "Code",
        "general":  "General",
    }
    label = labels.get(intent, "ARIA")
    return f'<span class="agent-badge badge-{intent}">{label}</span>'
