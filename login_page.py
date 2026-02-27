"""
VulnSage — AI-Powered Security Dashboard
Login + Register Page (Streamlit)

Drop-in replacement for your existing login_page.py.
Requires: streamlit, bcrypt, pyjwt

Usage in app.py:
    from login_page import auth_gate, show_logout_button, require_admin, get_current_user_role
    if not auth_gate():
        st.stop()
"""

import streamlit as st
import json, os, re, hashlib
from datetime import datetime, timedelta, timezone

# ── Optional secure deps (graceful fallback for demo) ────────────────────────
try:
    import bcrypt
    _BCRYPT = True
except ImportError:
    _BCRYPT = False

try:
    import jwt as pyjwt
    _JWT = True
except ImportError:
    _JWT = False

JWT_SECRET  = os.environ.get("VULNSAGE_JWT_SECRET", "vulnsage-dev-secret-change-me")
JWT_EXPIRY  = 24  # hours

# ── Default users ─────────────────────────────────────────────────────────────
DEFAULT_USERS = {
    "admin": {
        "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqKx8pKvGm",
        "role": "admin", "name": "Administrator", "email": "admin@vulnsage.local",
    },
    "demo": {
        "password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "role": "user",  "name": "Demo User",      "email": "demo@vulnsage.local",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════════════════
AUTH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne+Mono&family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

/* ── FORCE DARK CANVAS ─────────────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"], .stApp, .main,
[data-testid="stMain"], [data-testid="stHeader"] {
    background: #04060f !important;
    color: #d4e0ef !important;
}
#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display:none !important; }

.block-container {
    padding: 20px 24px 40px !important;
    max-width: 1400px !important;
    margin: auto !important;
}

/* ── ANIMATED GRID BACKGROUND ──────────────────────────────────── */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(0,220,255,0.022) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,220,255,0.022) 1px, transparent 1px);
    background-size: 48px 48px;
    animation: gridDrift 30s linear infinite;
}
@keyframes gridDrift { to { background-position: 48px 48px; } }

/* ── GLOWING BLOBS ─────────────────────────────────────────────── */
.vs-blob { position:fixed; border-radius:50%; filter:blur(80px); opacity:.55; pointer-events:none; z-index:0; }
.vs-blob-1 { width:600px;height:600px; background:radial-gradient(circle,rgba(0,160,255,.18),transparent 65%); top:-200px;left:-200px; animation:blob1 18s ease-in-out infinite alternate; }
.vs-blob-2 { width:500px;height:500px; background:radial-gradient(circle,rgba(120,60,255,.15),transparent 65%); bottom:-180px;right:-180px; animation:blob2 14s ease-in-out infinite alternate; }
@keyframes blob1 { to { transform:translate(60px,40px) scale(1.1); } }
@keyframes blob2 { to { transform:translate(-50px,-30px) scale(1.08); } }

/* ── SCAN LINE EFFECT (landing-style) ─────────────────────────── */
.vs-scan-beam {
    position: fixed; left: 0; right: 0; top: 0;
    height: 2px; z-index: 0; pointer-events: none;
    background: linear-gradient(90deg, transparent 0%, rgba(0,212,255,.7) 30%, rgba(168,85,247,.7) 60%, rgba(232,121,249,.4) 80%, transparent 100%);
    filter: blur(1px);
    animation: vsScanBeam 10s ease-in-out infinite;
}
.vs-scan-beam-2 {
    position: fixed; left: 0; right: 0; top: 0;
    height: 1px; z-index: 0; pointer-events: none;
    background: linear-gradient(90deg, transparent 0%, rgba(52,211,153,.5) 50%, transparent 100%);
    animation: vsScanBeam 10s 5s ease-in-out infinite;
}
@keyframes vsScanBeam {
    0%   { top: -2px; opacity: 0; }
    3%   { opacity: 1; }
    97%  { opacity: .4; }
    100% { top: 102%; opacity: 0; }
}

/* ── CARD ──────────────────────────────────────────────────────── */
.vs-card {
    position:relative; z-index:1;
    background: linear-gradient(145deg,rgba(0,220,255,.045) 0%,rgba(8,12,26,.95) 50%,rgba(139,92,246,.04) 100%);
    border: 1px solid rgba(0,220,255,.10);
    border-radius: 20px;
    padding: 36px 36px 32px;
    box-shadow: 0 0 0 1px rgba(0,220,255,.06), 0 40px 80px rgba(0,0,0,.6), 0 0 80px rgba(0,220,255,.04);
    backdrop-filter: blur(20px);
    overflow: hidden;
}
.vs-card::before {
    content:'';
    position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,220,255,.35),rgba(139,92,246,.25),transparent);
}
.vs-card::after {
    content:'';
    position:absolute; inset:0; pointer-events:none;
    background:radial-gradient(ellipse 80% 50% at 50% -20%,rgba(0,220,255,.04),transparent 60%);
}

/* ── LOGO ──────────────────────────────────────────────────────── */
.vs-logo-wrap { display:flex; align-items:center; justify-content:center; gap:12px; margin-bottom:24px; }
.vs-logo-icon {
    position: relative; width: 40px; height: 40px; flex-shrink:0;
    display:flex; align-items:center; justify-content:center;
}
.vs-logo-bg {
    position: absolute; inset: 0; border-radius: 11px;
    background: linear-gradient(135deg, rgba(0,212,255,.15), rgba(168,85,247,.15));
    border: 1px solid rgba(0,212,255,.25);
}
.vs-logo-spin {
    position: absolute; inset: -3px; border-radius: 13px;
    background: conic-gradient(from 0deg, transparent 0%, #06b6d4 30%, transparent 60%);
    animation: spinGlow 4s linear infinite;
    mask: radial-gradient(farthest-side, transparent calc(100% - 2px), white calc(100% - 2px));
    opacity: .6;
}
@keyframes spinGlow { to { transform: rotate(360deg); } }
.vs-logo-glyph {
    font-size: 1.1rem; position: relative; z-index: 1;
    line-height: 1;
    background: linear-gradient(135deg, #00d4ff, #a855f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 8px rgba(0,212,255,.5));
}
.vs-wordmark {
    font-family:'Syne',sans-serif;
    font-size:1.6rem; letter-spacing:0.18em; line-height:1;
    text-transform: uppercase;
    color: #d4e0ef;
}
.vs-wordmark em {
    font-style: normal;
    background: linear-gradient(90deg, #00d4ff, #a855f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 8px rgba(0,212,255,.35));
}
.vs-brand-stack {
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.vs-brand-sub {
    font-family:'Syne Mono',monospace;
    font-size:.52rem;
    letter-spacing:.14em;
    text-transform:uppercase;
    color:#f5f5f5;
}

/* ── EYEBROW + HEADINGS ────────────────────────────────────────── */
.vs-eyebrow {
    font-family:'Syne Mono',monospace; font-size:.58rem; letter-spacing:.3em;
    text-transform:uppercase; color:#00dcff; opacity:.75; text-align:center; margin-bottom:6px;
}
.vs-title {
    font-family:'Space Grotesk',sans-serif !important;
    font-size:1.5rem !important; font-weight:700 !important;
    color:#e8f0fb !important; text-align:center; letter-spacing:-.01em;
    margin-bottom:4px;
}
.vs-sub {
    font-family:'DM Sans',sans-serif !important;
    font-size:.8rem !important; color:#5a7090 !important;
    text-align:center; margin-bottom:24px;
}

/* ── INPUTS ────────────────────────────────────────────────────── */
.stTextInput label {
    font-family:'Syne Mono',monospace !important;
    font-size:.58rem !important; letter-spacing:.22em !important;
    text-transform:uppercase !important; color:#5a7090 !important;
    margin-bottom:4px !important;
}
.stTextInput > div > div > input {
    background: rgba(255,255,255,.03) !important;
    border: 1px solid rgba(0,220,255,.10) !important;
    border-radius: 8px !important;
    color: #d4e0ef !important;
    font-family: 'DM Sans',sans-serif !important;
    font-size: .9rem !important;
    padding: 13px 16px !important;
    transition: border-color .2s, box-shadow .2s !important;
    caret-color: #00dcff !important;
}
.stTextInput > div > div > input::placeholder { color: rgba(90,112,144,.55) !important; }
.stTextInput > div > div > input:focus {
    border-color: rgba(0,220,255,.38) !important;
    background: rgba(0,220,255,.03) !important;
    box-shadow: 0 0 0 3px rgba(0,220,255,.07) !important;
    outline: none !important;
}

/* ── CHECKBOX ──────────────────────────────────────────────────── */
.stCheckbox label {
    font-family:'DM Sans',sans-serif !important;
    font-size:.78rem !important; color:#8aa0b8 !important;
}
.stCheckbox [data-baseweb="checkbox"] > div:first-child {
    background: rgba(255,255,255,.03) !important;
    border-color: rgba(0,220,255,.22) !important;
    border-radius: 4px !important;
}

/* ── PRIMARY BUTTON ────────────────────────────────────────────── */
div.vs-btn-primary > button,
.stFormSubmitButton > button {
    background: linear-gradient(135deg,#00caf5,#7c3aed) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    height: 50px !important;
    font-family: 'Space Grotesk',sans-serif !important;
    font-size: .88rem !important;
    font-weight: 600 !important;
    letter-spacing: .05em !important;
    transition: transform .2s, box-shadow .2s !important;
    box-shadow: 0 8px 24px rgba(0,200,245,.25), 0 0 40px rgba(124,58,237,.15) !important;
    position: relative; overflow: hidden;
}
div.vs-btn-primary > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 14px 36px rgba(0,200,245,.38), 0 0 60px rgba(124,58,237,.25) !important;
}
div.vs-btn-primary > button:active { transform: translateY(1px) !important; }

/* ── SECONDARY BUTTON ──────────────────────────────────────────── */
div.vs-btn-secondary > button {
    background: rgba(255,255,255,.03) !important;
    color: #8aa0b8 !important;
    border: 1px solid rgba(0,220,255,.18) !important;
    border-radius: 8px !important;
    height: 50px !important;
    font-family: 'Space Grotesk',sans-serif !important;
    font-size: .85rem !important;
    font-weight: 500 !important;
    letter-spacing: .04em !important;
    transition: all .25s !important;
}
div.vs-btn-secondary > button:hover {
    border-color: rgba(0,220,255,.45) !important;
    color: #00dcff !important;
    background: rgba(0,220,255,.06) !important;
    box-shadow: 0 0 20px rgba(0,220,255,.12) !important;
}

/* ── GHOST / SOCIAL BUTTONS ────────────────────────────────────── */
div.vs-btn-social > button {
    background: rgba(255,255,255,.03) !important;
    color: #8aa0b8 !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 8px !important;
    height: 44px !important;
    font-family: 'DM Sans',sans-serif !important;
    font-size: .82rem !important;
    transition: all .2s !important;
}
div.vs-btn-social > button:hover {
    border-color: rgba(255,255,255,.2) !important;
    color: #d4e0ef !important;
    background: rgba(255,255,255,.06) !important;
}

/* ── ALERTS ────────────────────────────────────────────────────── */
.stAlert {
    border-radius: 10px !important;
    font-family: 'DM Sans',sans-serif !important;
    font-size: .8rem !important;
    border: none !important;
}
[data-baseweb="notification"] {
    background: rgba(255,77,106,.08) !important;
    border: 1px solid rgba(255,77,106,.25) !important;
    border-radius: 10px !important;
}

/* ── DEMO CREDS BOX ────────────────────────────────────────────── */
.vs-demo {
    margin-top: 20px;
    padding: 16px 18px;
    border-radius: 14px;
    background: rgba(255,255,255,.02);
    border: 1px solid rgba(0,220,255,.07);
}
.vs-demo-lbl {
    font-family:'Syne Mono',monospace;
    font-size:.58rem; letter-spacing:.22em; text-transform:uppercase;
    color:#00dcff; opacity:.7; margin-bottom:10px;
}
.vs-cred { display:inline-block; padding:6px 14px; border-radius:999px; font-family:'Syne Mono',monospace; font-size:.7rem; letter-spacing:.06em; }
.vs-cred-admin { background:rgba(0,212,255,.08); border:1px solid rgba(0,212,255,.28); color:#00eaff; }
.vs-cred-demo  { background:rgba(139,92,246,.12); border:1px solid rgba(160,130,255,.28); color:#c4b5fd; }

/* ── SECURITY BADGES ───────────────────────────────────────────── */
.vs-badges { display:flex; justify-content:center; gap:8px; flex-wrap:wrap; margin-top:20px; }
.vs-badge {
    display:inline-flex; align-items:center; gap:5px;
    padding:4px 11px; border-radius:999px;
    font-family:'Syne Mono',monospace; font-size:.57rem; letter-spacing:.08em; text-transform:uppercase;
}
.vs-badge-jwt    { background:rgba(0,229,160,.08); border:1px solid rgba(0,229,160,.2); color:#00e5a0; }
.vs-badge-bcrypt { background:rgba(139,92,246,.08); border:1px solid rgba(139,92,246,.2); color:#a78bfa; }
.vs-badge-tls    { background:rgba(0,220,255,.07); border:1px solid rgba(0,220,255,.18); color:#00dcff; }

/* ── DIVIDER ───────────────────────────────────────────────────── */
.vs-divider {
    display:flex; align-items:center; gap:12px; margin:8px 0;
    font-family:'Syne Mono',monospace; font-size:.58rem; letter-spacing:.18em;
    text-transform:uppercase; color:#2e4055;
}
.vs-divider::before,.vs-divider::after { content:''; flex:1; height:1px; background:rgba(0,220,255,.07); }

/* ── PW STRENGTH ───────────────────────────────────────────────── */
.vs-pw-bar { display:flex; gap:4px; margin:6px 0 2px; }
.vs-pw-seg { height:3px; flex:1; border-radius:99px; background:rgba(255,255,255,.06); transition:background .3s; }
.vs-pw-s1 { background:#ff4d6a; }
.vs-pw-s2 { background:#ffb340; }
.vs-pw-s3 { background:#70e0a0; }
.vs-pw-s4 { background:#00e5a0; }
.vs-pw-label { font-family:'Syne Mono',monospace; font-size:.6rem; }

/* ── SIDE PANEL ────────────────────────────────────────────────── */
.vs-side {
    position:relative; z-index:1;
    background:linear-gradient(145deg,rgba(0,220,255,.04),rgba(8,12,26,.92),rgba(139,92,246,.04) 100%);
    border:1px solid rgba(0,220,255,.09);
    border-radius:20px; padding:36px 28px;
    box-shadow:0 0 60px rgba(0,180,255,.05);
}
.vs-side::before { content:''; position:absolute;top:0;left:0;right:0;height:1px; background:linear-gradient(90deg,transparent,rgba(0,220,255,.2),transparent); }
.vs-feat { display:flex; align-items:flex-start; gap:10px; margin-bottom:14px; }
.vs-feat-dot { width:8px;height:8px;border-radius:50%;background:#00dcff;box-shadow:0 0 10px rgba(0,220,255,.7);flex-shrink:0;margin-top:4px; }
.vs-feat-text { font-family:'DM Sans',sans-serif; font-size:.78rem; color:#7a95b0; line-height:1.55; }
.vs-feat-title { color:#c4d4e4; font-weight:600; font-size:.82rem; display:block; margin-bottom:2px; }

/* ── TOP BAR ───────────────────────────────────────────────────── */
div.vs-home-btn > button {
    background: rgba(255,255,255,.03) !important;
    color: #5a7090 !important;
    border: 1px solid rgba(255,255,255,.07) !important;
    border-radius: 999px !important;
    font-family: 'Syne Mono',monospace !important;
    font-size: .62rem !important;
    letter-spacing: .12em !important;
    text-transform: uppercase !important;
    height: 36px !important;
    padding: 0 16px !important;
    transition: all .2s !important;
}
div.vs-home-btn > button:hover {
    border-color: rgba(0,220,255,.3) !important;
    color: #00dcff !important;
}

/* ── STATUS PILL ───────────────────────────────────────────────── */
.vs-status {
    display:inline-flex; align-items:center; gap:6px;
    font-family:'Syne Mono',monospace; font-size:.58rem; letter-spacing:.1em;
    color:#00e5a0; background:rgba(0,229,160,.07); border:1px solid rgba(0,229,160,.18);
    padding:5px 12px; border-radius:999px;
}
.vs-status-dot { width:6px;height:6px;border-radius:50%;background:#00e5a0;box-shadow:0 0 8px #00e5a0; animation:statusPulse 2s ease infinite; }
@keyframes statusPulse { 0%,100%{opacity:1}50%{opacity:.35} }

/* ── WARNING BANNER ────────────────────────────────────────────── */
.vs-warn {
    display:flex; align-items:center; gap:10px;
    background:rgba(255,180,0,.07); border:1px solid rgba(255,180,0,.22);
    border-radius:12px; padding:12px 16px; margin:10px 0;
    font-family:'Syne Mono',monospace; font-size:.68rem; color:#ffc966; letter-spacing:.04em;
}

/* ── SIDEBAR ───────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(4,6,15,.97) !important;
    border-right: 1px solid rgba(0,220,255,.07) !important;
}
[data-testid="stSidebar"] * { font-family:'Space Grotesk',sans-serif !important; }
[data-testid="stSidebar"] label { color:#5a7090 !important; font-size:.78rem !important; }
[data-testid="stSidebar"] hr { border-color:rgba(0,220,255,.06) !important; }

div.vs-logout-btn > button {
    background: rgba(255,50,80,.07) !important;
    color: #ff8fab !important;
    border: 1px solid rgba(255,50,80,.18) !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk',sans-serif !important;
    font-weight: 600 !important; font-size: .8rem !important;
    letter-spacing: .06em !important;
    width: 100% !important; transition: all .2s !important;
}
div.vs-logout-btn > button:hover {
    background: rgba(255,50,80,.14) !important;
    border-color: rgba(255,50,80,.38) !important;
}

/* ── RESPONSIVE ────────────────────────────────────────────────── */
@media(max-width:768px){
    .vs-card  { padding:24px 18px 20px !important; }
    .vs-title { font-size:1.25rem !important; }
    .vs-side  { padding:24px 18px !important; margin-top:16px; }
}
</style>
"""

# ══════════════════════════════════════════════════════════════════════════════
#  AUTH HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _hash_password(password: str) -> str:
    if _BCRYPT:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
    return hashlib.sha256(password.encode()).hexdigest()


def _verify_password(password: str, hashed: str) -> bool:
    if _BCRYPT and hashed.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception:
            return False
    # fallback SHA-256 or plain MD5
    return (hashlib.sha256(password.encode()).hexdigest() == hashed or
            hashlib.md5(password.encode()).hexdigest() == hashed)


def _password_strength(pw: str):
    """Returns (score 0-4, label, colour)."""
    score = 0
    if len(pw) >= 8:            score += 1
    if re.search(r'[A-Z]', pw) and re.search(r'[a-z]', pw): score += 1
    if re.search(r'\d', pw):    score += 1
    if re.search(r'[^A-Za-z0-9]', pw): score += 1
    labels = ["", "Weak", "Fair", "Good", "Strong"]
    colours = ["", "#ff4d6a", "#ffb340", "#70e0a0", "#00e5a0"]
    return score, labels[score], colours[score]


def _create_jwt(user_data: dict) -> str:
    if not _JWT:
        return "no-jwt"
    exp = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY)
    payload = {**user_data, "exp": exp, "iat": datetime.now(timezone.utc)}
    return pyjwt.encode(payload, JWT_SECRET, algorithm="HS256")


def _verify_jwt(token: str):
    if not _JWT or not token or token == "no-jwt":
        return True  # graceful bypass
    try:
        return pyjwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except Exception:
        return None


def _validate_email(email: str) -> bool:
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email.strip()))


# ── User store ────────────────────────────────────────────────────────────────
def _load_users() -> dict:
    if os.path.exists("users.json"):
        try:
            with open("users.json") as f:
                users = json.load(f)
            updated = False
            for k, v in DEFAULT_USERS.items():
                if k not in users:
                    users[k] = v; updated = True
            if updated:
                with open("users.json", "w") as f:
                    json.dump(users, f, indent=2)
            return users
        except Exception:
            pass
    defaults = DEFAULT_USERS.copy()
    try:
        with open("users.json", "w") as f:
            json.dump(defaults, f, indent=2)
    except Exception:
        pass
    return defaults


def _normalize_username(username: str) -> str:
    return str(username or "").strip().lower()


def _normalize_email(email: str) -> str:
    return str(email or "").strip().lower()


def _username_exists(users: dict, username: str, exclude_username: str = "") -> bool:
    target = _normalize_username(username)
    exclude = _normalize_username(exclude_username)
    for existing in users.keys():
        norm = _normalize_username(existing)
        if norm == target and norm != exclude:
            return True
    return False


def _email_in_use(users: dict, email: str, exclude_username: str = "") -> bool:
    target = _normalize_email(email)
    exclude = _normalize_username(exclude_username)
    for uname, data in users.items():
        if _normalize_username(uname) == exclude:
            continue
        if _normalize_email(data.get("email", "")) == target:
            return True
    return False


def load_users() -> dict:
    """
    Backward-compatible public user loader used by app_ai.py admin views.
    """
    return _load_users()


def _save_user(username, password, role="user", name="", email="") -> bool:
    users = _load_users()
    users[username] = {
        "password": _hash_password(password),
        "role": role, "name": name or username, "email": email.strip(),
    }
    try:
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)
        return True
    except Exception:
        return False


def update_user_profile(
    current_username: str,
    new_username: str,
    new_name: str,
    new_email: str
):
    """
    Update current user's profile with uniqueness checks.
    Returns: (success: bool, message: str, updated_user: dict|None, resolved_username: str|None)
    """
    users = _load_users()

    current_key = None
    for uname in users.keys():
        if _normalize_username(uname) == _normalize_username(current_username):
            current_key = uname
            break

    if not current_key:
        return False, "User not found.", None, None

    new_username = str(new_username or "").strip()
    new_name = str(new_name or "").strip()
    new_email = str(new_email or "").strip()

    if len(new_username) < 3:
        return False, "Username must be at least 3 characters.", None, None
    if not _validate_email(new_email):
        return False, "Enter a valid email address.", None, None
    if _username_exists(users, new_username, exclude_username=current_key):
        return False, "Username already exists.", None, None
    if _email_in_use(users, new_email, exclude_username=current_key):
        return False, "Email already in use.", None, None

    existing = users[current_key]
    updated = {
        **existing,
        "name": new_name or new_username,
        "email": new_email
    }

    # If username changed, move record key.
    if _normalize_username(new_username) != _normalize_username(current_key):
        users.pop(current_key, None)
        users[new_username] = updated
        resolved_username = new_username
    else:
        users[current_key] = updated
        resolved_username = current_key

    try:
        with open("users.json", "w") as f:
            json.dump(users, f, indent=2)
        return True, "Profile updated successfully.", updated, resolved_username
    except Exception:
        return False, "Could not save profile changes.", None, None


def _verify_credentials(username: str, password: str):
    users = _load_users()
    if username not in users:
        return False, None
    stored = users[username]["password"]
    if _verify_password(password, stored):
        return True, users[username]
    return False, None


def _authenticate(username: str, password: str):
    valid, info = _verify_credentials(username, password)
    if valid:
        token = _create_jwt({"username": username, "name": info.get("name", username), "role": info.get("role", "user")})
        info = {**info, "token": token}
        return True, info
    return False, None


# ══════════════════════════════════════════════════════════════════════════════
#  COMPONENTS
# ══════════════════════════════════════════════════════════════════════════════
def _logo_html():
    return """
    <div class="vs-logo-wrap">
      <div class="vs-logo-icon">
        <div class="vs-logo-bg"></div>
        <div class="vs-logo-spin"></div>
        <span class="vs-logo-glyph">🛡</span>
      </div>
      <div class="vs-brand-stack">
        <div class="vs-wordmark">
          <em>VULN</em>SAGE
        </div>
        <div class="vs-brand-sub">AI-Powered Web Vulnerability Scanner</div>
      </div>
    </div>"""


def _security_badges():
    return """
    <div class="vs-badges">
      <span class="vs-badge vs-badge-bcrypt">🔒 bcrypt</span>
      <span class="vs-badge vs-badge-jwt">🛡 JWT</span>
      <span class="vs-badge vs-badge-tls">🔐 TLS 1.3</span>
    </div>"""


def _pw_strength_html(score, label, colour):
    segs = ""
    for i in range(1, 5):
        cls = f"vs-pw-s{score}" if i <= score else ""
        segs += f'<div class="vs-pw-seg {cls}"></div>'
    return f"""
    <div class="vs-pw-bar">{segs}</div>
    <div class="vs-pw-label" style="color:{colour}">{label}</div>"""


# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════════════════════════
def show_login_page():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    # Landing-style moving scan lines
    st.markdown('<div class="vs-scan-beam"></div><div class="vs-scan-beam-2"></div>', unsafe_allow_html=True)

    # Blobs
    st.markdown('<div class="vs-blob vs-blob-1"></div><div class="vs-blob vs-blob-2"></div>', unsafe_allow_html=True)

    # Top bar
    top_l, top_r = st.columns([1, 5])
    with top_l:
        st.markdown('<div class="vs-home-btn">', unsafe_allow_html=True)
        if st.button("← Home", key="login_home"):
            st.session_state.page = "landing"
            st.session_state.show_register = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with top_r:
        st.markdown('<div style="text-align:right;padding-top:2px"><span class="vs-status"><span class="vs-status-dot"></span>Systems Online</span></div>', unsafe_allow_html=True)

    # Direct-login warning
    if st.session_state.get("direct_login_attempt"):
        st.markdown("""
        <div class="vs-warn">
          <span style="font-size:1rem;animation:statusPulse 2s ease infinite">⚠</span>
          Please sign in to access the scanner dashboard, or return home to explore the platform first.
        </div>""", unsafe_allow_html=True)

    # Layout: card | gap | side panel
    card_col, _, side_col = st.columns([1.1, 0.05, 0.85])

    # ── LEFT CARD ──
    with card_col:
        st.markdown(f'<div class="vs-card">{_logo_html()}'
                    '<div class="vs-eyebrow">// Secure Access Portal</div>'
                    '<h1 class="vs-title">Welcome Back</h1>'
                    '<p class="vs-sub">Sign in to your security dashboard</p>'
                    '</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Email / Username", placeholder="admin  or  admin@vulnsage.io", key="l_user")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="l_pass")
            remember = st.checkbox("Remember me", key="l_remember")

            st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown('<div class="vs-btn-primary">', unsafe_allow_html=True)
                sign_in = st.form_submit_button("⚡ Authenticate", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with col_b:
                st.markdown('<div class="vs-btn-secondary">', unsafe_allow_html=True)
                go_reg = st.form_submit_button("✦ Register", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # Social login row
        st.markdown('<div class="vs-divider">or continue with</div>', unsafe_allow_html=True)
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown('<div class="vs-btn-social">', unsafe_allow_html=True)
            if st.button("🔵  Google", key="l_google", use_container_width=True):
                st.info("Google OAuth — connect your provider in settings.")
            st.markdown("</div>", unsafe_allow_html=True)
        with sc2:
            st.markdown('<div class="vs-btn-social">', unsafe_allow_html=True)
            if st.button("⚫  GitHub", key="l_github", use_container_width=True):
                st.info("GitHub OAuth — connect your provider in settings.")
            st.markdown("</div>", unsafe_allow_html=True)

       

        st.markdown(_security_badges(), unsafe_allow_html=True)

    # ── RIGHT: Security side panel ──
    with side_col:
        st.markdown("""
<div class="vs-side" style="margin-top:52px">
  <div style="text-align:center;margin-bottom:18px">
    <div style="font-size:2.2rem;margin-bottom:8px">🧠</div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;color:#e0eaf5;letter-spacing:.02em">
      AI-Powered Threat Intelligence
    </div>
    <div style="font-family:'DM Sans',sans-serif;font-size:.76rem;color:#4a6070;margin-top:6px;line-height:1.6">
      VulnSage performs automated web security analysis using AI-driven risk evaluation and intelligent vulnerability classification.
    </div>
  </div>

  <div class="vs-feat"><div class="vs-feat-dot"></div>
    <div class="vs-feat-text">
      <span class="vs-feat-title">Automated Vulnerability Scanning</span>
      Detects misconfigurations, insecure headers, exposed endpoints, and common OWASP Top 10 risks.
    </div>
  </div>

  <div class="vs-feat"><div class="vs-feat-dot"></div>
    <div class="vs-feat-text">
      <span class="vs-feat-title">AI Risk Classification</span>
      Machine learning model categorizes findings into Critical, High, Medium, and Low severity levels.
    </div>
  </div>

  <div class="vs-feat"><div class="vs-feat-dot"></div>
    <div class="vs-feat-text">
      <span class="vs-feat-title">LLM-Powered Analysis</span>
      Generates human-readable security reports with actionable remediation guidance.
    </div>
  </div>

  <div class="vs-feat"><div class="vs-feat-dot"></div>
    <div class="vs-feat-text">
      <span class="vs-feat-title">Real-Time Security Assessment</span>
      Performs live scanning and instant report generation via Streamlit dashboard.
    </div>
  </div>

  <div class="vs-feat"><div class="vs-feat-dot"></div>
    <div class="vs-feat-text">
      <span class="vs-feat-title">Comprehensive Reporting</span>
      Executive summary, risk breakdown, and structured vulnerability insights.
    </div>
  </div>

  <div style="margin-top:22px;padding:14px;background:rgba(0,229,160,.04);border:1px solid rgba(0,229,160,.1);border-radius:10px;">
    <div style="font-family:'Syne Mono',monospace;font-size:.58rem;letter-spacing:.18em;text-transform:uppercase;color:#00e5a0;opacity:.8;margin-bottom:8px">// Security Standards</div>
    <div style="display:flex;gap:8px;flex-wrap:wrap">
      <span style="font-family:'Syne Mono',monospace;font-size:.6rem;padding:3px 8px;border-radius:999px;background:rgba(0,229,160,.07);border:1px solid rgba(0,229,160,.15);color:#00e5a0">OWASP Top 10</span>
      <span style="font-family:'Syne Mono',monospace;font-size:.6rem;padding:3px 8px;border-radius:999px;background:rgba(0,220,255,.07);border:1px solid rgba(0,220,255,.15);color:#00dcff">AI Risk Engine</span>
      <span style="font-family:'Syne Mono',monospace;font-size:.6rem;padding:3px 8px;border-radius:999px;background:rgba(139,92,246,.07);border:1px solid rgba(139,92,246,.15);color:#a78bfa">Real-Time Analysis</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Form handlers ──
    if sign_in:
        if not username or not password:
            st.warning("⚠️ Both username and password are required.")
        else:
            valid, info = _authenticate(username.strip(), password)
            if valid:
                st.session_state.authenticated = True
                st.session_state.username = username.strip()
                st.session_state.user_info = info
                st.session_state.jwt_token = info.get("token", "")
                st.session_state.login_time = datetime.now().isoformat()
                st.session_state.direct_login_attempt = False
                st.success(f"✅ Access granted — welcome, **{info['name']}**!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Authentication failed. Invalid credentials.")

    if go_reg:
        st.session_state.show_register = True
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  REGISTER PAGE
# ══════════════════════════════════════════════════════════════════════════════
def show_register_page():
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    # Landing-style moving scan lines
    st.markdown('<div class="vs-scan-beam"></div><div class="vs-scan-beam-2"></div>', unsafe_allow_html=True)

    st.markdown('<div class="vs-blob vs-blob-1"></div><div class="vs-blob vs-blob-2"></div>', unsafe_allow_html=True)

    # Top bar
    top_l, top_r = st.columns([1, 5])
    with top_l:
        st.markdown('<div class="vs-home-btn">', unsafe_allow_html=True)
        if st.button("← Home", key="reg_home"):
            st.session_state.page = "landing"
            st.session_state.show_register = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with top_r:
        st.markdown('<div style="text-align:right;padding-top:2px"><span class="vs-status"><span class="vs-status-dot"></span>Systems Online</span></div>', unsafe_allow_html=True)

    _, col, _ = st.columns([0.6, 1.1, 0.6])
    with col:
        st.markdown(f'<div class="vs-card">{_logo_html()}'
                    '<div class="vs-eyebrow">// Create Your Account</div>'
                    '<h1 class="vs-title">Get Started</h1>'
                    '<p class="vs-sub">Join VulnSage — scan smarter, defend faster</p>'
                    '</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # Password requirements box
        st.markdown("""
        <div style="background:rgba(0,220,255,.03);border:1px solid rgba(0,220,255,.09);border-radius:10px;
             padding:12px 14px;font-family:'Syne Mono',monospace;font-size:.65rem;color:#5a7090;margin-bottom:10px;">
          <div style="color:#00dcff;font-size:.58rem;letter-spacing:.18em;text-transform:uppercase;margin-bottom:7px">
            // Password Requirements
          </div>
          Minimum 8 characters · Uppercase + lowercase · At least one digit · One special character
        </div>""", unsafe_allow_html=True)

        with st.form("register_form", clear_on_submit=False):
            new_name  = st.text_input("Full Name",        placeholder="Your Name",        key="r_name")
            new_email = st.text_input("Email",       placeholder="youremail@xyz.com",       key="r_email")
            new_user  = st.text_input("Username",         placeholder="Choose a username",    key="r_user")
            new_pass  = st.text_input("Password",         type="password", placeholder="Min. 8 characters", key="r_pass")
            conf_pass = st.text_input("Confirm Password", type="password", placeholder="Repeat your password", key="r_confirm")

            # Live password strength bar
            if new_pass:
                score, label, colour = _password_strength(new_pass)
                st.markdown(_pw_strength_html(score, label, colour), unsafe_allow_html=True)

            # Confirm match indicator
            if conf_pass:
                if new_pass == conf_pass:
                    st.markdown('<div style="font-family:\'Syne Mono\',monospace;font-size:.65rem;color:#00e5a0;margin-top:2px">✓ Passwords match</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="font-family:\'Syne Mono\',monospace;font-size:.65rem;color:#ff4d6a;margin-top:2px">✗ Passwords do not match</div>', unsafe_allow_html=True)

            terms = st.checkbox("I agree to the Terms of Service and Privacy Policy", key="r_terms")

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            ca, cb = st.columns(2)
            with ca:
                st.markdown('<div class="vs-btn-primary">', unsafe_allow_html=True)
                create = st.form_submit_button("✅ Create Account", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            with cb:
                st.markdown('<div class="vs-btn-secondary">', unsafe_allow_html=True)
                back = st.form_submit_button("← Back to Login", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        # Social row
        st.markdown('<div class="vs-divider">or sign up with</div>', unsafe_allow_html=True)
        sa, sb = st.columns(2)
        with sa:
            st.markdown('<div class="vs-btn-social">', unsafe_allow_html=True)
            if st.button("🔵  Google", key="r_google", use_container_width=True):
                st.info("Google OAuth — connect your provider in settings.")
            st.markdown("</div>", unsafe_allow_html=True)
        with sb:
            st.markdown('<div class="vs-btn-social">', unsafe_allow_html=True)
            if st.button("⚫  GitHub", key="r_github", use_container_width=True):
                st.info("GitHub OAuth — connect your provider in settings.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(_security_badges(), unsafe_allow_html=True)

    # Handlers
    if create:
        errors = []
        if not new_user or len(new_user) < 3:
            errors.append("Username must be at least 3 characters.")
        if not new_email or not _validate_email(new_email):
            errors.append("Enter a valid email address.")
        if not new_pass or len(new_pass) < 8:
            errors.append("Password must be at least 8 characters.")
        score, _, _ = _password_strength(new_pass or "")
        if score < 2:
            errors.append("Password too weak — add uppercase, digits, or symbols.")
        if new_pass != conf_pass:
            errors.append("Passwords do not match.")
        if not terms:
            errors.append("Please accept the Terms of Service.")
        users = _load_users()
        if _username_exists(users, new_user):
            errors.append("Username already exists.")
        if _email_in_use(users, new_email):
            errors.append("Email already in use.")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        elif _save_user(new_user, new_pass, "user", new_name, new_email):
            st.success("✅ Account created! Sign in with your new credentials.")
            st.balloons()
            st.session_state.show_register = False
            st.rerun()
        else:
            st.error("❌ Could not save account. Check file permissions.")

    if back:
        st.session_state.show_register = False
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR SESSION PANEL
# ══════════════════════════════════════════════════════════════════════════════
def show_logout_button():
    with st.sidebar:
        info = st.session_state.get("user_info", {})
        name = info.get("name", "User")
        role = info.get("role", "user")
        role_colour = "#ff5080" if role == "admin" else "#a78bfa"
        role_bg     = "rgba(255,0,80,.12)" if role == "admin" else "rgba(139,92,246,.12)"
        role_border = "rgba(255,0,80,.3)"  if role == "admin" else "rgba(160,120,255,.28)"

        st.markdown(f"""
        <div style="background:rgba(0,220,255,.04);border:1px solid rgba(0,220,255,.12);
             border-radius:12px;padding:16px 18px;margin-bottom:6px;font-family:'Space Grotesk',sans-serif;">
          <div style="font-family:'Syne Mono',monospace;font-size:.55rem;letter-spacing:.2em;
               text-transform:uppercase;color:#00dcff;margin-bottom:10px;">// Active Session</div>
          <div style="font-weight:700;color:#c9d6e3;font-size:.92rem;">{name}</div>
          <span style="display:inline-block;margin-top:7px;
               background:{role_bg};border:1px solid {role_border};color:{role_colour};
               font-family:'Syne Mono',monospace;font-size:.6rem;padding:3px 10px;
               border-radius:999px;letter-spacing:.07em;text-transform:uppercase;">{role}</span>
        </div>""", unsafe_allow_html=True)

        if st.session_state.get("jwt_token"):
            st.markdown("""
            <div style="background:rgba(0,229,160,.04);border:1px solid rgba(0,229,160,.1);
                 border-radius:8px;padding:10px 12px;margin-bottom:12px;
                 font-family:'Syne Mono',monospace;font-size:.6rem;color:#00e5a0;">
              🔐 JWT Session Active
              <div style="color:#3a5a4a;margin-top:3px">Expires in 24 hours</div>
            </div>""", unsafe_allow_html=True)

        profile_target = "Dashboard" if st.session_state.get("dashboard_page") == "profile" else "Profile"
        if st.button(f"👤 {profile_target}", use_container_width=True, key="open_profile_btn"):
            st.session_state.dashboard_page = "dashboard" if st.session_state.get("dashboard_page") == "profile" else "profile"
            st.rerun()

        st.markdown('<div class="vs-logout-btn">', unsafe_allow_html=True)
        if st.button("⏻  Sign Out", use_container_width=True, key="logout_btn"):
            for k in ["authenticated", "username", "user_info", "login_time", "jwt_token", "dashboard_page"]:
                st.session_state.pop(k, None)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ROLE HELPERS (same API as original)
# ══════════════════════════════════════════════════════════════════════════════
def check_session_validity() -> bool:
    if not st.session_state.get("authenticated", False):
        return False
    token = st.session_state.get("jwt_token")
    if token and _verify_jwt(token) is None:
        st.session_state.authenticated = False
        st.session_state.pop("jwt_token", None)
        return False
    return bool(st.session_state.get("username") and st.session_state.get("user_info"))


def require_admin() -> bool:
    if not check_session_validity():
        return False
    return st.session_state.get("user_info", {}).get("role") == "admin"


def check_user_role(required_role: str) -> bool:
    if not check_session_validity():
        return False
    hierarchy = {"guest": 0, "user": 1, "admin": 2}
    user_role = st.session_state.get("user_info", {}).get("role", "guest")
    return hierarchy.get(user_role, 0) >= hierarchy.get(required_role, 99)


def get_current_user_role() -> str:
    return st.session_state.get("user_info", {}).get("role", "guest") if check_session_validity() else "guest"


def get_current_username() -> str:
    return st.session_state.get("username", "") if check_session_validity() else ""


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY-POINT ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def auth_gate() -> bool:
    """
    Call at the top of app.py.
    Returns True when user is authenticated; renders auth UI and returns False otherwise.

    Usage:
        from login_page import auth_gate, show_logout_button, require_admin
        if not auth_gate():
            st.stop()
        show_logout_button()
    """
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        if "page" not in st.session_state or st.session_state.get("page") == "login":
            st.session_state.setdefault("direct_login_attempt", True)
        if st.session_state.get("show_register"):
            show_register_page()
        else:
            show_login_page()
        return False

    if not check_session_validity():
        st.session_state.authenticated = False
        st.error("⚠️ Session expired. Please sign in again.")
        show_login_page()
        return False

    return True
