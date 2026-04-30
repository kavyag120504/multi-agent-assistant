"""
Shared navbar — fixed, no overlap, attractive styling.
"""
import streamlit as st


def render_navbar(user: dict, active: str = "chat"):
    from tools.auth_db import delete_session

    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@600;700&display=swap');

[data-testid="stSidebar"],[data-testid="collapsedControl"],
#MainMenu,footer,header,[data-testid="stToolbar"],
[data-testid="stDecoration"]{display:none!important}

html,body{margin:0;padding:0;background:#0a0a0a!important}
[data-testid="stAppViewContainer"]{background:#0a0a0a!important;font-family:'Inter',sans-serif!important}
[data-testid="stAppViewContainer"]::before{
    content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
    background:
        radial-gradient(ellipse 80% 60% at 0% 0%,rgba(180,10,10,.22) 0%,transparent 50%),
        radial-gradient(ellipse 60% 50% at 100% 100%,rgba(120,0,0,.18) 0%,transparent 50%);
}
[data-testid="stMain"]{position:relative;z-index:1}
.block-container{padding:0!important;max-width:100%!important}

/* ── Navbar button classes ── */
.nb-btn > button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #c0c0c0 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    padding: 5px 18px !important;
    height: 36px !important;
    white-space: nowrap !important;
    transition: all 0.15s !important;
    letter-spacing: 0.2px !important;
}
.nb-btn > button:hover {
    background: rgba(220,38,38,0.08) !important;
    border-color: rgba(220,38,38,0.3) !important;
    color: #ff6b6b !important;
}
.nb-active > button {
    background: rgba(220,38,38,0.15) !important;
    border: 1px solid rgba(220,38,38,0.5) !important;
    color: #ff6b6b !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    padding: 5px 18px !important;
    height: 36px !important;
    white-space: nowrap !important;
    letter-spacing: 0.2px !important;
    box-shadow: 0 0 14px rgba(220,38,38,0.25) !important;
}
.nb-so > button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #888 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    padding: 4px 14px !important;
    height: 32px !important;
    white-space: nowrap !important;
    transition: all 0.15s !important;
}
.nb-so > button:hover {
    color: #ef4444 !important;
    border-color: rgba(220,38,38,0.4) !important;
    background: rgba(220,38,38,0.08) !important;
}
.nb-btn > button *, .nb-active > button *, .nb-so > button * {
    white-space: nowrap !important;
    word-break: keep-all !important;
}
</style>
""", unsafe_allow_html=True)

    # Fixed navbar background strip
    st.markdown("""
<div id="aria-navbar-bg" style="
    position:fixed;top:0;left:0;right:0;height:52px;
    background:rgba(10,10,10,0.97);
    border-bottom:1px solid rgba(255,255,255,0.08);
    backdrop-filter:blur(20px);
    z-index:9998;
"></div>
""", unsafe_allow_html=True)

    # Navbar row — use a unique container ID to scope CSS
    st.markdown('<div id="aria-navbar-row">', unsafe_allow_html=True)

    col_brand, col_chat, col_hist, col_about, col_sp, col_user, col_so = st.columns(
        [1.0, 0.6, 0.75, 0.65, 5.0, 1.3, 0.75]
    )

    with col_brand:
        st.markdown(
            '<div style="height:52px;display:flex;align-items:center;padding-left:4px">'
            '<span style="font-family:\'Space Grotesk\',sans-serif;font-size:1.4rem;'
            'font-weight:800;background:linear-gradient(135deg,#ff4444,#cc0000);'
            '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
            'letter-spacing:-.5px">KAVI</span></div>',
            unsafe_allow_html=True)

    with col_chat:
        css = "nb-active" if active == "chat" else "nb-btn"
        st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
        if st.button("Chat", key="nb_chat"):
            st.switch_page("pages/1_Chat.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_hist:
        css = "nb-active" if active == "history" else "nb-btn"
        st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
        if st.button("History", key="nb_hist"):
            st.switch_page("pages/2_History.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_about:
        css = "nb-active" if active == "about" else "nb-btn"
        st.markdown(f'<div class="{css}">', unsafe_allow_html=True)
        if st.button("About", key="nb_about"):
            st.switch_page("pages/3_About.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_sp:
        st.empty()

    with col_user:
        st.markdown(
            f'<div style="height:52px;display:flex;align-items:center;justify-content:flex-end;">'
            f'<span style="font-size:12px;color:#555;font-family:\'Inter\',sans-serif;'
            f'white-space:nowrap">{user["display_name"]}</span></div>',
            unsafe_allow_html=True)

    with col_so:
        st.markdown('<div class="nb-so">', unsafe_allow_html=True)
        if st.button("Sign out", key="nb_so"):
            t = st.session_state.get("session_token")
            if t:
                delete_session(t)
            for k in ["session_token","current_user","messages","total_queries","agents_used"]:
                st.session_state.pop(k, None)
            st.switch_page("app.py")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Fix ONLY the aria-navbar-row to the top — scoped by ID
    st.markdown("""
<style>
#aria-navbar-row {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 52px !important;
    z-index: 9999 !important;
    background: transparent !important;
    overflow: hidden !important;
}
#aria-navbar-row > div[data-testid="stHorizontalBlock"] {
    position: static !important;
    height: 52px !important;
    display: flex !important;
    align-items: center !important;
    padding: 0 20px !important;
    margin: 0 !important;
    gap: 4px !important;
    background: transparent !important;
}
#aria-navbar-row > div[data-testid="stHorizontalBlock"] [data-testid="column"] {
    flex: 0 0 auto !important;
    width: auto !important;
    min-width: 0 !important;
    padding: 0 2px !important;
}
#aria-navbar-row > div[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(5) {
    flex: 1 1 auto !important;
}
</style>
""", unsafe_allow_html=True)

    # Spacer so page content starts below navbar
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
