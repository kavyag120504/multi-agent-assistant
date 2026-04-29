"""
ARIA — Entry point.
Handles login / register. Authenticated users are redirected to Chat.
"""
import streamlit as st
from tools.shared_styles import inject_styles
from tools.auth_db import (
    register_user, login_user,
    create_session, validate_session,
    cleanup_expired_sessions,
)
from tools.reminder_scheduler import start_scheduler

st.set_page_config(
    page_title="ARIA — AI Assistant",
    page_icon="assets/favicon.png" if False else "🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

start_scheduler()

if "cleanup_done" not in st.session_state:
    cleanup_expired_sessions()
    st.session_state.cleanup_done = True

inject_styles()

# ── Extra auth-page styles ────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { display: none !important; }

.login-wrap {
    display: flex;
    min-height: 92vh;
    align-items: center;
    justify-content: center;
    gap: 0;
}
.login-left {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 3rem 4rem;
}
.login-left h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 3.2rem;
    font-weight: 700;
    color: #fff;
    line-height: 1.15;
    margin-bottom: 1rem;
}
.login-left h1 span { color: #ef4444; }
.login-left p {
    color: #888;
    font-size: 15px;
    line-height: 1.7;
    max-width: 420px;
    margin-bottom: 2rem;
}
.pill-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 2rem; }
.pill {
    background: rgba(220,38,38,0.1);
    border: 1px solid rgba(220,38,38,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    color: #f87171;
    font-family: 'Inter', sans-serif;
}
.login-right {
    width: 420px;
    flex-shrink: 0;
    background: rgba(22,22,22,0.95);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 2.5rem 2rem;
    backdrop-filter: blur(20px);
    margin: 2rem;
}
.login-right h2 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 0.3rem;
}
.login-right p { color: #888; font-size: 13px; margin-bottom: 1.5rem; }
.divider-line {
    display: flex; align-items: center; gap: 12px;
    margin: 1.2rem 0; color: #555; font-size: 12px;
}
.divider-line::before, .divider-line::after {
    content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.08);
}
</style>
""", unsafe_allow_html=True)

# ── Redirect if already logged in ────────────────────────────────────────────
token = st.session_state.get("session_token")
if token and validate_session(token):
    st.switch_page("pages/1_Chat.py")

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([1.2, 0.9], gap="large")

with left:
    st.markdown("""
    <div class="login-left">
        <h1>Meet <span>KAVI</span><br>Your AI Assistant</h1>
        <p>
            A multi-agent AI platform that handles your weather, emails,
            calendar, news, tasks, reminders, web search, and code execution —
            all through natural language.
        </p>
        <div class="pill-row">
            <span class="pill">Weather & Forecast</span>
            <span class="pill">Email Management</span>
            <span class="pill">Google Calendar</span>
            <span class="pill">Web Search</span>
            <span class="pill">Latest News</span>
            <span class="pill">Task Manager</span>
            <span class="pill">Code Executor</span>
            <span class="pill">Smart Reminders</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="login-right">', unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

    with tab_login:
        st.markdown("<h2>Welcome Back</h2><p>Sign in to your KAVI account</p>", unsafe_allow_html=True)
        with st.form("login_form"):
            username  = st.text_input("Username", placeholder="your_username")
            password  = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

        if submitted:
            if not username or not password:
                st.error("Please fill in both fields.")
            else:
                ok, msg, user = login_user(username, password)
                if ok:
                    token = create_session(user["id"])
                    st.session_state.session_token  = token
                    st.session_state.current_user   = user
                    st.session_state.messages       = []
                    st.session_state.total_queries  = 0
                    st.session_state.agents_used    = {}
                    st.switch_page("pages/1_Chat.py")
                else:
                    st.error(msg)

    with tab_register:
        st.markdown("<h2>Create Account</h2><p>Join KAVI — it's free</p>", unsafe_allow_html=True)
        with st.form("register_form"):
            new_display = st.text_input("Full Name", placeholder="Kavya Goswami")
            new_user    = st.text_input("Username", placeholder="kavya_g")
            new_pass    = st.text_input("Password", type="password", placeholder="min 6 characters")
            new_pass2   = st.text_input("Confirm Password", type="password", placeholder="repeat password")
            submitted   = st.form_submit_button("Create Account", use_container_width=True, type="primary")

        if submitted:
            if not all([new_display, new_user, new_pass, new_pass2]):
                st.error("Please fill in all fields.")
            elif new_pass != new_pass2:
                st.error("Passwords do not match.")
            else:
                ok, msg = register_user(new_user, new_display, new_pass)
                if ok:
                    st.success(f"{msg} You can now sign in.")
                else:
                    st.error(msg)

    st.markdown('</div>', unsafe_allow_html=True)
