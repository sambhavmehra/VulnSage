"""
Login Page — AI POWERED Security Dashboard
Converted from login.html. Matches existing login.py style/patterns.
Additions:
  - "← Back to Home" button on login + register pages
  - Warning banner when user lands directly on login (not via landing CTA)
  - Full mobile responsiveness
"""
import streamlit as st
import hashlib
import json
import os
from datetime import datetime
from admin_logger import log_registration, log_login, log_activity

# ── Default users (admin/admin, demo/demo) ────────────────────────────────────
DEFAULT_USERS = {
    "admin": {
        "password": "21232f297a57a5a743894a0e4a801fc3",  # md5("admin")
        "role": "admin",
        "name": "Administrator",
    },
    "demo": {
        "password": "fe01ce2a7fbac8fafaed7c982a04e229",  # md5("demo")
        "role": "user",
        "name": "Demo User",
    },
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def hash_password(p: str) -> str:
    return hashlib.md5(p.encode()).hexdigest()


def load_users() -> dict:
    if os.path.exists("users.json"):
        try:
            with open("users.json") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_USERS.copy()


def save_user(username: str, password: str, role: str = "user", name: str = "") -> bool:
    users = load_users()
    users[username] = {
        "password": hash_password(password),
        "role": role,
        "name": name or username,
    }
    try:
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)
        return True
    except Exception:
        return False


def verify_credentials(username: str, password: str):
    """Returns (valid: bool, user_info: dict | None)."""
    users = load_users()
    if username in users and users[username]["password"] == hash_password(password):
        return True, users[username]
    return False, None


# ── Shared CSS ────────────────────────────────────────────────────────────────
AUTH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');

/* FORCE DARK */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"], .stApp, .main,
[data-testid="stMain"], [data-testid="stHeader"] {
    background-color: #060a14 !important;
    background: #060a14 !important;
    color: #c9d6e3 !important;
}
#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

.block-container {
    padding: 0 20px !important;
    max-width: 1620px !important;
    margin: auto !important;
}

/* ── ANIMATED GRID BACKGROUND ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(0, 240, 255, 0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 240, 255, 0.025) 1px, transparent 1px);
    background-size: 52px 52px;
}

/* ── MATRIX BLOBS ── */
.matrix-blob-1 {
    position: fixed; width: 560px; height: 560px; border-radius: 50%;
    background: radial-gradient(circle, rgba(0, 200, 255, 0.13) 0%, transparent 68%);
    top: -220px; left: -220px;
    pointer-events: none; z-index: 0;
    animation: blob1 16s ease-in-out infinite alternate;
}
.matrix-blob-2 {
    position: fixed; width: 460px; height: 460px; border-radius: 50%;
    background: radial-gradient(circle, rgba(100, 0, 255, 0.1) 0%, transparent 70%);
    bottom: -180px; right: -180px;
    pointer-events: none; z-index: 0;
    animation: blob2 11s ease-in-out infinite alternate;
}
@keyframes blob1 { to { transform: translate(50px, 35px) scale(1.08); } }
@keyframes blob2 { to { transform: translate(-35px, -28px) scale(1.12); } }

/* ── BACK TO HOME BUTTON (top-left) ── */
.back-home-bar {
    position: relative; z-index: 10;
    padding: 18px 0 0 4px;
    margin-bottom: -8px;
}

div.back-home-btn button {
    background: rgba(0, 240, 255, 0.06) !important;
    color: #00f0ff !important;
    border: 1px solid rgba(0, 240, 255, 0.22) !important;
    border-radius: 50px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: .72rem !important;
    letter-spacing: .14em !important;
    text-transform: uppercase !important;
    padding: 8px 20px !important;
    height: 38px !important;
    transition: all .25s ease !important;
}
div.back-home-btn button:hover {
    background: rgba(0, 240, 255, 0.14) !important;
    border-color: #00f0ff !important;
    box-shadow: 0 0 18px rgba(0, 240, 255, 0.25) !important;
    transform: translateX(-3px) !important;
}

/* ── DIRECT LOGIN WARNING BANNER ── */
.direct-login-warning {
    position: relative; z-index: 5;
    background: rgba(255, 180, 0, 0.07);
    border: 1px solid rgba(255, 180, 0, 0.28);
    border-radius: 12px;
    padding: 13px 18px;
    margin: 10px 0 0;
    font-family: 'Share Tech Mono', monospace;
    font-size: .72rem;
    color: #ffc966;
    letter-spacing: .06em;
    display: flex;
    align-items: center;
    gap: 10px;
}
.direct-login-warning .warn-icon {
    font-size: 1rem;
    flex-shrink: 0;
    animation: warnPulse 2s ease infinite;
}
@keyframes warnPulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: .45; }
}

/* ── MAIN CARD ── */
.auth-card {
    position: relative; z-index: 1;
    background: linear-gradient(140deg, rgba(0, 200, 255, 0.06), rgba(100, 0, 255, 0.04));
    border: 1px solid rgba(0, 240, 255, 0.12);
    border-radius: 20px;
    padding: 40px 38px 36px;
    margin-top: 24px;
    font-family: 'Orbitron', monospace;
    box-shadow: 0 0 60px rgba(0, 180, 255, 0.06), inset 0 1px 0 rgba(255,255,255,0.04);
}

/* logo */
.auth-logo {
    display: flex; align-items: center; justify-content: center;
    gap: 10px; margin-bottom: 18px;
}
.auth-logo-icon {
    font-size: 1.7rem; color: #00f0ff;
    text-shadow: 0 0 14px rgba(0,240,255,0.7);
    animation: pulse-icon 3s ease-in-out infinite;
}
@keyframes pulse-icon {
    0%, 100% { text-shadow: 0 0 14px rgba(0,240,255,0.7); }
    50%       { text-shadow: 0 0 28px rgba(0,240,255,1), 0 0 60px rgba(0,240,255,0.4); }
}
.auth-logo-text {
    font-family: 'Orbitron', monospace;
    font-size: 1.05rem; font-weight: 900;
    letter-spacing: 0.18em; color: #00f0ff;
    text-transform: uppercase;
}
.auth-eyebrow {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem; letter-spacing: 0.28em;
    text-transform: uppercase; color: #00f0ff;
    display: block; text-align: center; margin-bottom: 10px;
    opacity: 0.75;
}
.auth-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 1.55rem !important; font-weight: 900 !important;
    color: #e0eaf5 !important; letter-spacing: 0.04em;
    text-align: center; margin: 0 0 6px;
    text-shadow: 0 0 30px rgba(0,240,255,0.15);
}
.auth-sub {
    color: #3d5068 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.75rem !important; text-align: center; margin-bottom: 0;
}

/* ── INPUTS ── */
.stTextInput label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.65rem !important; letter-spacing: 0.2em !important;
    text-transform: uppercase !important; color: #3d5068 !important;
}
.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(0, 240, 255, 0.1) !important;
    border-radius: 10px !important;
    color: #c9d6e3 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.88rem !important;
    padding: 14px 17px !important;
    transition: border-color 0.25s, box-shadow 0.25s !important;
    caret-color: #00f0ff !important;
}
.stTextInput > div > div > input::placeholder { color: #1e2d3d !important; }
.stTextInput > div > div > input:focus {
    border-color: #00f0ff !important;
    box-shadow: 0 0 0 3px rgba(0, 240, 255, 0.09) !important;
    outline: none !important;
}

/* ── CHECKBOX ── */
.stCheckbox label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.73rem !important; color: #4a6070 !important;
}
.stCheckbox [data-baseweb="checkbox"] { gap: 10px !important; }

/* ── BUTTON SYSTEM ── */
div.auth-primary-btn button,
.stFormSubmitButton button {
    height: 50px !important;
    border-radius: 12px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: .8rem !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
    transition: all .35s ease !important;
    backdrop-filter: blur(10px);
}

div.auth-primary-btn button {
    background: linear-gradient(135deg, #00d4ff, #7b61ff) !important;
    color: #05070f !important;
    border: none !important;
    font-weight: 700 !important;
    box-shadow:
        0 0 0 1px rgba(255,255,255,.08) inset,
        0 10px 28px rgba(0,212,255,.35),
        0 0 28px rgba(0,212,255,.25);
}
div.auth-primary-btn button:hover {
    transform: translateY(-4px) scale(1.02) !important;
    box-shadow:
        0 0 0 1px rgba(255,255,255,.15) inset,
        0 18px 48px rgba(0,212,255,.55),
        0 0 40px rgba(123,97,255,.35);
}
div.auth-primary-btn button:active {
    transform: translateY(1px) scale(.98) !important;
}

div.auth-secondary-btn button {
    background: rgba(255,255,255,.03) !important;
    color: #c9d6e3 !important;
    border: 1px solid rgba(0,212,255,.25) !important;
    border-radius: 12px !important;
    height: 50px !important;
    font-family: 'Orbitron', monospace !important;
    font-size: .78rem !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
    box-shadow: 0 0 0 1px rgba(255,255,255,.05) inset, 0 6px 22px rgba(0,0,0,.35);
    transition: all .3s ease !important;
}
div.auth-secondary-btn button:hover {
    border-color: #00d4ff !important;
    color: #00d4ff !important;
    background: rgba(0,212,255,.08) !important;
    box-shadow: 0 12px 34px rgba(0,212,255,.25), 0 0 25px rgba(0,212,255,.2);
}

/* ── ALERTS ── */
.stAlert {
    border-radius: 10px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.76rem !important; border: none !important;
}

/* ── DEMO CREDENTIALS CARD ── */
.auth-demo {
    margin-top: 22px;
    padding: 16px 18px 18px;
    border-radius: 16px;
    background: rgba(255,255,255,.02);
    border: 1px solid rgba(0,240,255,.08);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.03);
}
.auth-demo-lbl {
    font-family: 'Share Tech Mono', monospace;
    font-size: .6rem; letter-spacing: .22em;
    text-transform: uppercase; color: #00f0ff; opacity: .75;
}
.auth-demo-row {
    display: flex; justify-content: space-between;
    margin-top: 14px; gap: 10px; flex-wrap: wrap;
}
.auth-cred-label {
    font-family: 'Orbitron', monospace;
    font-size: .7rem; color: #7d92a8; margin-bottom: 6px;
}
.auth-cred-chip {
    display: inline-block; padding: 6px 12px;
    border-radius: 50px; font-family: 'Share Tech Mono', monospace;
    font-size: .68rem; letter-spacing: .06em; border: 1px solid;
}
.chip-cyan   { background: rgba(0,212,255,.08); border-color: rgba(0,212,255,.3);   color: #00eaff; }
.chip-purple { background: rgba(123,97,255,.12); border-color: rgba(140,120,255,.35); color: #b7a7ff; }

/* ── SECURITY SIDE PANEL ── */
.auth-side-panel {
    position: relative; z-index: 1;
    background: linear-gradient(140deg, rgba(0, 200, 255, 0.05), rgba(100, 0, 255, 0.04));
    border: 1px solid rgba(0, 240, 255, 0.12);
    border-radius: 20px; padding: 38px 32px; margin-top: 24px;
    font-family: 'Orbitron', monospace;
    box-shadow: 0 0 60px rgba(0, 180, 255, 0.05), inset 0 1px 0 rgba(255,255,255,0.04);
}
.side-badge-icon  { font-size: 2.2rem; text-align: center; margin-bottom: 10px; }
.side-badge-title { font-size: 1rem; font-weight: 800; text-align: center; color: #e0eaf5; letter-spacing: .04em; }
.side-badge-text  { text-align: center; font-family: 'Share Tech Mono', monospace; font-size: .76rem; color: #4f637c; margin-bottom: 24px; line-height: 1.6; }
.side-feature     { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; font-family: 'Share Tech Mono', monospace; font-size: .76rem; color: #9bb2c9; }
.side-feature-dot { width: 8px; height: 8px; border-radius: 50%; background: #00f0ff; box-shadow: 0 0 12px rgba(0,240,255,.8); flex-shrink: 0; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: rgba(6,10,20,.97) !important;
    border-right: 1px solid rgba(0,240,255,0.07) !important;
}
[data-testid="stSidebar"] * { font-family: 'Orbitron', monospace !important; }
/* Preserve Streamlit/Material icons; otherwise ligature names render as text
   (e.g., "keyboard_double_arrow_right"). */
[data-testid="stSidebar"] [class*="material-symbols"],
[data-testid="stSidebar"] .material-icons {
    font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
    font-style: normal !important;
    font-weight: normal !important;
}
[data-testid="stSidebar"] label { color: #6880a0 !important; font-size: 0.78rem !important; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #c9d6e3 !important; font-size: 0.75rem !important;
    font-weight: 700 !important; letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(0,240,255,0.06) !important; }

/* ══════════════════════════════════════════
   MOBILE RESPONSIVE OVERRIDES
══════════════════════════════════════════ */
@media (max-width: 768px) {
    .block-container { padding: 0 12px !important; }

    .auth-card {
        padding: 28px 20px 24px !important;
        margin-top: 12px !important;
    }
    .auth-title { font-size: 1.25rem !important; }
    .auth-logo-text { font-size: .85rem !important; }
    .auth-logo-icon { font-size: 1.4rem !important; }

    /* Stack the two-column layout vertically on mobile */
    .auth-side-panel {
        margin-top: 16px !important;
        padding: 24px 18px !important;
    }

    div.auth-primary-btn button,
    div.auth-secondary-btn button { font-size: .7rem !important; letter-spacing: .05em !important; }

    .auth-demo-row { flex-direction: column; gap: 14px; }

    .direct-login-warning { font-size: .68rem !important; padding: 11px 14px !important; }

    div.back-home-btn button { font-size: .66rem !important; height: 34px !important; }

    /* Side panel hidden on very small screens */
    .auth-side-panel .side-badge-text { font-size: .7rem !important; }
    .side-feature { font-size: .7rem !important; }
}

@media (max-width: 480px) {
    .auth-card { padding: 22px 14px 20px !important; }
    .auth-title { font-size: 1.1rem !important; }
    .auth-sub   { font-size: .68rem !important; }
    .auth-demo  { padding: 14px 14px 16px !important; }
}
</style>
"""


# ── Login page ────────────────────────────────────────────────────────────────
def show_login_page():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    # Animated blobs
    st.markdown(
        '<div class="matrix-blob-1"></div><div class="matrix-blob-2"></div>',
        unsafe_allow_html=True,
    )

    # ── Back to Home button (top row) ─────────────────────────────────────────
    st.markdown('<div class="back-home-bar">', unsafe_allow_html=True)
    back_col, _ = st.columns([1, 5])
    with back_col:
        st.markdown('<div class="back-home-btn">', unsafe_allow_html=True)
        go_home = st.button("← Home", key="login_go_home", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if go_home:
        st.session_state.page = 'landing'
        st.session_state.show_register = False
        st.rerun()

    # ── Direct-login warning banner ───────────────────────────────────────────
    if st.session_state.get("direct_login_attempt"):
        st.markdown("""
        <div class="direct-login-warning">
            <span class="warn-icon">⚠</span>
            You navigated directly to the login page. Please sign in to access
            the scanner dashboard, or &nbsp;<strong>return home</strong>&nbsp; to explore the platform first.
        </div>
        """, unsafe_allow_html=True)

    # Two-column layout: form left, security panel right
    form_col, gap_col, side_col = st.columns([1.1, 0.06, 0.9])

    # ── LEFT: Login form ──────────────────────────────────────────────────────
    with form_col:
        st.markdown("""
        <div class="auth-card">
            <div class="auth-logo">
                <span class="auth-logo-icon">◈</span>
                <span class="auth-logo-text">AI Powered</span>
            </div>
            <span class="auth-eyebrow">// Access Control</span>
            <h1 class="auth-title">Authenticate</h1>
            <p class="auth-sub">Sign in to access the security dashboard</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            remember = st.checkbox("Remember me")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="auth-primary-btn">', unsafe_allow_html=True)
                sign_in = st.form_submit_button("⚡  Authenticate", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="auth-secondary-btn">', unsafe_allow_html=True)
                go_reg = st.form_submit_button("✦  Register", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # Demo credentials box
        st.markdown("""
        <div class="auth-demo">
            <span class="auth-demo-lbl">// Quick Demo Access</span>
            <div class="auth-demo-row">
                <div>
                    <div class="auth-cred-label">Admin</div>
                    <span class="auth-cred-chip chip-cyan">admin / admin</span>
                </div>
                <div>
                    <div class="auth-cred-label">Demo User</div>
                    <span class="auth-cred-chip chip-purple">demo / demo</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── RIGHT: Security side panel ────────────────────────────────────────────
    with side_col:
        st.markdown("""
        <div class="auth-side-panel">
            <div class="side-badge-icon">🛡️</div>
            <p class="side-badge-title">Secure Authentication</p>
            <p class="side-badge-text">
                Your credentials are encrypted and protected with
                military-grade security protocols.
            </p>
            <div class="side-feature">
                <div class="side-feature-dot"></div>
                AI-powered threat detection
            </div>
            <div class="side-feature">
                <div class="side-feature-dot"></div>
                Real-time vulnerability scanning
            </div>
            <div class="side-feature">
                <div class="side-feature-dot"></div>
                Comprehensive security reports
            </div>
            <div class="side-feature">
                <div class="side-feature-dot"></div>
                Multi-layer encryption protocols
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Form handlers ─────────────────────────────────────────────────────────
    if sign_in:
        if not username or not password:
            st.warning("⚠️ Both username and password are required.")
        else:
            valid, info = verify_credentials(username, password)
            if valid:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.user_info = info
                st.session_state.login_time = datetime.now().isoformat()
                st.session_state.direct_login_attempt = False
                log_login(username, info.get('role', 'user'), True)
                if remember:
                    st.session_state.remember_me = True
                st.success(f"✅ Access granted — welcome, {info['name']}!")
                st.balloons()
                st.rerun()
            else:
                log_login(username, 'unknown', False)
                st.error("❌ Authentication failed. Invalid credentials.")

    if go_reg:
        st.session_state.show_register = True
        st.rerun()


# ── Register page ─────────────────────────────────────────────────────────────
def show_register_page():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="matrix-blob-1"></div><div class="matrix-blob-2"></div>',
        unsafe_allow_html=True,
    )

    # ── Back to Home button ───────────────────────────────────────────────────
    st.markdown('<div class="back-home-bar">', unsafe_allow_html=True)
    back_col, _ = st.columns([1, 5])
    with back_col:
        st.markdown('<div class="back-home-btn">', unsafe_allow_html=True)
        go_home_reg = st.button("← Home", key="reg_go_home", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if go_home_reg:
        st.session_state.page = 'landing'
        st.session_state.show_register = False
        st.rerun()

    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("""
        <div class="auth-card">
            <div class="auth-logo">
                <span class="auth-logo-icon">◈</span>
                <span class="auth-logo-text">AI Powered</span>
            </div>
            <span class="auth-eyebrow">// Create Account</span>
            <h1 class="auth-title">New Account</h1>
            <p class="auth-sub">Join the AI security platform</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        with st.form("register_form", clear_on_submit=False):
            new_u  = st.text_input("Username",         placeholder="Choose a username")
            new_n  = st.text_input("Full Name",         placeholder="Your full name")
            new_p  = st.text_input("Password",          type="password", placeholder="Choose a strong password")
            conf_p = st.text_input("Confirm Password",  type="password", placeholder="Repeat your password")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="auth-primary-btn">', unsafe_allow_html=True)
                create = st.form_submit_button("✅  Create Account", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="auth-secondary-btn">', unsafe_allow_html=True)
                back = st.form_submit_button("← Back to Login", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

    if create:
        if not new_u or not new_p:
            st.error("❌ Username and password are required.")
        elif len(new_p) < 4:
            st.error("❌ Password must be at least 4 characters.")
        elif new_p != conf_p:
            st.error("❌ Passwords do not match.")
        elif new_u in load_users():
            st.error("❌ Username already taken.")
        elif save_user(new_u, new_p, "user", new_n):
            log_registration(new_u, new_n)
            st.success("✅ Account created! Sign in with your new credentials.")
            st.session_state.show_register = False
            st.balloons()
            st.rerun()
        else:
            st.error("❌ Could not save account. Check file permissions.")

    if back:
        st.session_state.show_register = False
        st.rerun()


# ── Sidebar session panel + sign-out button ───────────────────────────────────
def show_logout_button():
    with st.sidebar:
        name = st.session_state.user_info.get("name", "")
        role = st.session_state.user_info.get("role", "")

        st.markdown(f"""
        <div style="
            background: rgba(0,240,255,0.04);
            border: 1px solid rgba(0,240,255,0.13);
            border-radius: 12px; padding: 16px 18px; margin-bottom: 6px;
            font-family: 'Orbitron', monospace;">
            <div style="font-family:'Share Tech Mono',monospace;font-size:.56rem;
                letter-spacing:.18em;text-transform:uppercase;color:#00f0ff;margin-bottom:10px;">
                // Session
            </div>
            <div style="font-weight:700;color:#c9d6e3;font-size:.92rem;">{name}</div>
            <span style="
                display:inline-block;margin-top:7px;
                background:rgba(100,0,255,.12);border:1px solid rgba(140,80,255,.28);
                color:#a88fff;font-family:'Share Tech Mono',monospace;font-size:.62rem;
                padding:3px 10px;border-radius:50px;letter-spacing:.06em;text-transform:uppercase;">
                {role}
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <style>
        div.logout-btn > button {
            background: rgba(255,50,80,.07) !important;
            color: #ff8fab !important;
            border: 1px solid rgba(255,50,80,.18) !important;
            border-radius: 10px !important;
            font-family: 'Orbitron', monospace !important;
            font-weight: 700 !important; font-size: .78rem !important;
            letter-spacing: .1em !important; text-transform: uppercase !important;
            width: 100% !important; transition: all .2s ease !important;
        }
        div.logout-btn > button:hover {
            background: rgba(255,50,80,.14) !important;
            border-color: rgba(255,50,80,.38) !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("⏻  Sign Out", use_container_width=True):
            for k in ["authenticated", "username", "user_info", "login_time", "remember_me"]:
                st.session_state.pop(k, None)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ── Entry-point router ────────────────────────────────────────────────────────
def auth_gate() -> bool:
    """
    Call this at the top of your main app.py.
    Returns True when the user is authenticated and the app should render.

    Usage:
        from login_page import auth_gate, show_logout_button
        if not auth_gate():
            st.stop()
        show_logout_button()
        # ... rest of your app
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        # Flag that this is a direct login attempt (not from landing CTA)
        if "page" not in st.session_state or st.session_state.page == "login":
            st.session_state.setdefault("direct_login_attempt", True)

        if st.session_state.get("show_register"):
            show_register_page()
        else:
            show_login_page()
        return False

    return True
