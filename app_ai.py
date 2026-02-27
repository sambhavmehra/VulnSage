import streamlit as st
import json
import logging
from datetime import datetime
from groq_orchestrator import GroqOrchestrator
from subdomain_scanner import SubdomainScanner
from vulnerability_detector import VulnerabilityDetector
from report_generator import ReportGenerator
from landing_page import show_landing_page
from login_page import show_login_page, show_register_page, show_logout_button, update_user_profile
from security_agent import SecurityAgent
from remediation_engine import RemediationEngine
from threat_intel_agent import ThreatIntelAgent
from self_training_agent import SelfTrainingAgent
from agentic_pentest_runner import AgenticPentestRunner
from soc_copilot import SOCCopilot
from reports_db import ReportsDB
from chatbot_component import render_chatbot, _log_activity, ask_chatbot_about_report
from admin_logger import get_all_logs, log_activity as admin_log_activity, get_registered_users_count, get_total_logins, get_failed_logins
from login_page import load_users

# Reduce noisy Tornado websocket disconnect tracebacks when client reconnects/closes.
logging.getLogger("tornado.websocket").setLevel(logging.ERROR)
logging.getLogger("tornado.application").setLevel(logging.ERROR)
logging.getLogger("tornado.general").setLevel(logging.ERROR)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VulnSage — AI Vulnerability Scanner",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="auto"
)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL DARK THEME
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"], .stApp, .main,
[data-testid="stMain"],
[data-testid="stHeader"],
[data-testid="stSidebarContent"],
section[data-testid="stSidebar"] > div:first-child {
    background-color: #06090f !important;
    background: #06090f !important;
    color: #e2e8f0 !important;
}

#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }
[data-testid="stToolbar"] { background: transparent !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #06090f; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(99,102,241,.5); }

/* Subtle grid overlay */
.stApp::after {
    content:''; position:fixed; inset:0; z-index:0; pointer-events:none;
    background-image:
        linear-gradient(rgba(99,102,241,.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,102,241,.015) 1px, transparent 1px);
    background-size: 64px 64px;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SCANNER CSS — REDESIGNED
# ══════════════════════════════════════════════════════════════════════════════
SCANNER_CSS = """
<style>
:root {
    --accent: #00d4ff;
    --accent2: #a855f7;
    --accent-glow: rgba(0,212,255,.25);
    --neon: #34d399;
    --neon2: #06b6d4;
    --warn: #fb923c;
    --danger: #f87171;
    --bg: #02020a;
    --card: rgba(255,255,255,.028);
    --card-hover: rgba(255,255,255,.045);
    --border: rgba(255,255,255,.06);
    --border-hover: rgba(0,212,255,.25);
    --text: #e2e8f0;
    --text-secondary: #94a3b8;
    --muted: #475569;
}

.block-container { padding: 1.2rem 2.2rem !important; max-width: 100% !important; }

/* ── TYPOGRAPHY ── */
h1 {
    font-family: 'Syne', sans-serif !important; font-weight: 800 !important;
    font-size: 2rem !important; color: var(--text) !important;
    letter-spacing: -.03em !important; line-height: 1.2 !important;
}
h2 {
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    font-size: 1.35rem !important; color: var(--text) !important;
    letter-spacing: -.02em !important;
}
h3 {
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    font-size: 1.1rem !important; color: var(--text) !important;
}
h4 {
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    font-size: .95rem !important; color: var(--text-secondary) !important;
}
p, li {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-secondary) !important;
    font-size: .9rem !important;
    line-height: 1.6 !important;
}
/* Keep Streamlit/Material icon ligatures working across the app.
   Without this, icon names can render as plain text. */
[class^="material-symbols"],
[class*=" material-symbols"],
.material-icons {
    font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
    font-style: normal !important;
    font-weight: normal !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    display: inline-block !important;
}
[data-testid="stExpander"] [data-testid="stExpanderIcon"],
[data-testid="collapsedControl"] span,
button[kind="header"] span {
    font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
    font-style: normal !important;
    font-weight: normal !important;
}

/* ── DASHBOARD HEADER ── */
.dash-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 20px 28px; flex-wrap: wrap; gap: 14px;
    background: linear-gradient(135deg, rgba(0,212,255,.06) 0%, rgba(168,85,247,.06) 100%);
    border: 1px solid rgba(0,212,255,.12);
    border-radius: 20px; margin-bottom: 28px;
    position: relative; overflow: hidden;
}
.dash-header::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, transparent, #00d4ff, #a855f7, transparent);
}
.dash-header::after {
    content:''; position:absolute; top:-50%; right:-20%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(0,212,255,.08) 0%, transparent 70%);
    border-radius: 50%; pointer-events: none;
}
.hdr-logo { display: flex; align-items: center; gap: 16px; z-index: 1; }
.brand-logo-ring {
    position: relative; width: 40px; height: 40px;
    display: flex; align-items: center; justify-content: center;
}
.brand-logo-bg {
    position: absolute; inset: 0; border-radius: 11px;
    background: linear-gradient(135deg, rgba(0,212,255,.15), rgba(168,85,247,.15));
    border: 1px solid rgba(0,212,255,.25);
}
.brand-logo-spin {
    position: absolute; inset: -3px; border-radius: 13px;
    background: conic-gradient(from 0deg, transparent 0%, #06b6d4 30%, transparent 60%);
    animation: spinGlow 4s linear infinite;
    mask: radial-gradient(farthest-side, transparent calc(100% - 2px), white calc(100% - 2px));
    opacity: .6;
}
@keyframes spinGlow { to { transform: rotate(360deg); } }
.brand-logo-icon {
    font-size: 1.1rem; position: relative; z-index: 1;
    line-height: 1;
    background: linear-gradient(135deg, #00d4ff, #a855f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 8px rgba(0,212,255,.35));
}
.hdr-icon {
    width: 48px; height: 48px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.hdr-title {
    font-family: 'Syne', sans-serif !important; font-size: 1.3rem;
    font-weight: 500; color: #e2e8f0 !important; letter-spacing: -.02em; margin: 0;
    text-transform: uppercase;
}
.hdr-title em {
    font-style: normal;
    background: linear-gradient(90deg, #00d4ff, #a855f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hdr-sub {
    font-family: 'JetBrains Mono', monospace; font-size: .68rem;
    color: #f5f5f5; letter-spacing: .04em; margin-top: 2px;
}
.hdr-badge {
    display: flex; align-items: center; gap: 8px;
    background: rgba(52,211,153,.08); border: 1px solid rgba(52,211,153,.2);
    border-radius: 50px; padding: 8px 16px;
    font-family: 'JetBrains Mono', monospace; font-size: .7rem;
    color: #34d399; letter-spacing: .04em; z-index: 1;
}
.pulse-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #34d399; box-shadow: 0 0 10px #34d399;
    animation: dotPulse 2s ease infinite; flex-shrink: 0;
}
@keyframes dotPulse { 50% { opacity:.25; } }

/* ── METRIC CARDS ── */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, rgba(255,255,255,.03), rgba(255,255,255,.015)) !important;
    border: 1px solid rgba(255,255,255,.06) !important;
    border-radius: 16px !important; padding: 20px 22px !important;
    transition: all .3s cubic-bezier(.4,0,.2,1);
    position: relative; overflow: hidden;
}
[data-testid="stMetric"]::before {
    content:''; position: absolute; top:0; left:0; right:0; height: 2px;
    background: linear-gradient(90deg, #818cf8, #34d399);
    opacity: 0; transition: opacity .3s;
}
[data-testid="stMetric"]:hover {
    border-color: rgba(99,102,241,.2) !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99,102,241,.08);
}
[data-testid="stMetric"]:hover::before { opacity: 1; }
[data-testid="stMetricLabel"] {
    font-family: 'JetBrains Mono', monospace !important; font-size: .68rem !important;
    letter-spacing: .1em !important; text-transform: uppercase !important;
    color: #64748b !important; font-weight: 500 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important; font-size: 1.8rem !important;
    font-weight: 800 !important; color: #e2e8f0 !important;
}

/* ── TEXT INPUT ── */
.stTextInput label {
    font-family: 'JetBrains Mono', monospace !important; font-size: .7rem !important;
    letter-spacing: .1em !important; text-transform: uppercase !important;
    color: #64748b !important; font-weight: 500 !important;
}
.stTextInput > div > div > input {
    background: rgba(255,255,255,.035) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 14px !important; color: #e2e8f0 !important;
    font-family: 'Space Grotesk', sans-serif !important; font-size: .9rem !important;
    padding: 14px 18px !important;
    transition: all .25s cubic-bezier(.4,0,.2,1) !important;
    caret-color: #818cf8 !important;
}
.stTextInput > div > div > input::placeholder { color: #334155 !important; }
.stTextInput > div > div > input:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,.12) !important;
}

/* ── BUTTONS ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #06b6d4, #a855f7) !important;
    color: #fff !important;
    font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    font-size: .92rem !important; border: none !important; border-radius: 14px !important;
    padding: 14px 24px !important; letter-spacing: .01em !important;
    box-shadow: 0 4px 20px rgba(0,212,255,.26) !important;
    transition: all .25s cubic-bezier(.4,0,.2,1) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(0,212,255,.35) !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,.035) !important; color: #e2e8f0 !important;
    border: 1px solid rgba(255,255,255,.08) !important; border-radius: 14px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    transition: all .25s !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: rgba(0,212,255,.35) !important; color: #00d4ff !important;
}

/* Sign-out */
div.sign-out-btn button {
    background: rgba(248,113,113,.06) !important; color: #fca5a5 !important;
    border: 1px solid rgba(248,113,113,.15) !important; border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    width: 100% !important; transition: all .2s !important;
}
div.sign-out-btn button:hover {
    background: rgba(248,113,113,.12) !important; border-color: rgba(248,113,113,.3) !important;
}

/* ── SLIDERS ── */
[data-baseweb="slider"] [data-testid="stThumb"],
[role="slider"] { background: #818cf8 !important; border-color: #818cf8 !important; }

/* ── CHECKBOXES ── */
.stCheckbox label { color: #94a3b8 !important; font-size: .88rem !important; }

/* ── PROGRESS ── */
.stProgress > div { background: rgba(255,255,255,.04) !important; border-radius: 12px !important; }
.stProgress > div > div {
    background: linear-gradient(90deg, #6366f1, #34d399) !important;
    border-radius: 12px !important; box-shadow: 0 0 14px rgba(99,102,241,.25) !important;
}

/* ── EXPANDERS ── */
[data-testid="stExpander"] summary {
    background: rgba(255,255,255,.025) !important;
    border: 1px solid rgba(255,255,255,.06) !important;
    border-radius: 14px !important; color: #e2e8f0 !important;
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    font-size: .92rem !important;
    transition: all .25s !important;
}
[data-testid="stExpander"] summary:hover { border-color: rgba(99,102,241,.2) !important; }
[data-testid="stExpander"] details[open] summary { border-radius: 14px 14px 0 0 !important; }
[data-testid="stExpander"] > div > div {
    background: rgba(255,255,255,.012) !important;
    border: 1px solid rgba(255,255,255,.05) !important;
    border-top: none !important; border-radius: 0 0 14px 14px !important;
}

/* ── ALERTS ── */
.stAlert {
    border-radius: 14px !important;
    font-family: 'Space Grotesk', sans-serif !important; font-size: .85rem !important;
    border: none !important;
}

/* ── DOWNLOAD BUTTONS ── */
.stDownloadButton > button {
    background: rgba(255,255,255,.03) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 14px !important; color: #e2e8f0 !important;
    font-family: 'Syne', sans-serif !important; font-weight: 600 !important;
    transition: all .25s !important;
}
.stDownloadButton > button:hover {
    border-color: #818cf8 !important; color: #818cf8 !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: rgba(6,9,15,.98) !important;
    border-right: 1px solid rgba(255,255,255,.04) !important;
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #e2e8f0 !important; font-size: .78rem !important;
    font-weight: 700 !important; letter-spacing: .08em !important;
    text-transform: uppercase !important;
    font-family: 'JetBrains Mono', monospace !important;
}
[data-testid="stSidebar"] label { color: #94a3b8 !important; font-size: .88rem !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.04) !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #94a3b8 !important; }

/* ── SCAN ROW ── */
.scan-row {
    background: linear-gradient(135deg, rgba(99,102,241,.04), rgba(52,211,153,.02));
    border: 1px solid rgba(99,102,241,.1);
    border-radius: 18px; padding: 22px 26px; margin-bottom: 20px;
    position: relative; overflow: hidden;
}
.scan-row::before {
    content:''; position:absolute; bottom:0; left:0; right:0; height:1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,.2), transparent);
}

/* ── STEP CARDS ── */
.step-card {
    background: rgba(255,255,255,.02);
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 16px; padding: 18px 20px;
    text-align: center;
    transition: all .3s cubic-bezier(.4,0,.2,1);
    position: relative;
}
.step-card:hover {
    border-color: rgba(99,102,241,.2);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99,102,241,.06);
}
.step-card-num {
    font-family: 'JetBrains Mono', monospace; font-size: .62rem;
    letter-spacing: .12em; color: #818cf8; display: block;
    margin-bottom: 6px; text-transform: uppercase; font-weight: 600;
}
.step-card-text {
    font-size: .88rem; color: #94a3b8; font-family: 'Syne', sans-serif;
    font-weight: 500;
}

/* ── DIVIDER LABEL ── */
.div-label { display: flex; align-items: center; gap: 16px; margin: 32px 0 22px; }
.div-label span {
    font-family: 'JetBrains Mono', monospace; font-size: .65rem;
    letter-spacing: .15em; color: #818cf8; text-transform: uppercase;
    white-space: nowrap; font-weight: 600;
}
.div-label::before, .div-label::after {
    content:''; flex:1; height:1px;
    background: linear-gradient(90deg, transparent, rgba(99,102,241,.15), transparent);
}

/* ── FOOTER ── */
.site-footer {
    display: flex; align-items: center; justify-content: center; gap: 12px;
    text-align: center; padding: 28px;
    font-family: 'JetBrains Mono', monospace; font-size: .9rem;
    letter-spacing: .06em; color: #475569; margin-top: 36px;
    border-top: 1px solid rgba(255,255,255,.04);
}
.site-footer em { color: #00d4ff; font-style: normal; }
.site-footer-text {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 3px;
}
.site-footer-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: .56rem;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #64748b;
}
.foot-logo { width: 30px; height: 30px; }
.foot-logo .brand-logo-bg { border-radius: 8px; }
.foot-logo .brand-logo-spin { inset: -2px; border-radius: 10px; }
.foot-logo .brand-logo-icon { font-size: .72rem; }

/* ── CODE BLOCKS ── */
[data-testid="stCode"] {
    background: rgba(255,255,255,.02) !important;
    border: 1px solid rgba(255,255,255,.06) !important;
    border-radius: 14px !important;
}

button[kind="header"] { color: #818cf8 !important; }
section[data-testid="stSidebar"] { transition: transform .3s ease !important; }

/* ── STAT GLOW CARDS ── */
.glow-card {
    background: linear-gradient(145deg, rgba(255,255,255,.03), rgba(255,255,255,.01));
    border: 1px solid rgba(255,255,255,.06);
    border-radius: 18px; padding: 22px 24px;
    position: relative; overflow: hidden;
    transition: all .3s cubic-bezier(.4,0,.2,1);
}
.glow-card:hover {
    border-color: rgba(99,102,241,.25);
    box-shadow: 0 8px 32px rgba(99,102,241,.08);
    transform: translateY(-2px);
}
.glow-card .glow-orb {
    position: absolute; top: -30px; right: -30px;
    width: 100px; height: 100px;
    border-radius: 50%; opacity: .12;
    filter: blur(30px); pointer-events: none;
}
.glow-card .card-label {
    font-family: 'JetBrains Mono', monospace; font-size: .65rem;
    letter-spacing: .12em; text-transform: uppercase;
    color: #64748b; margin-bottom: 8px; font-weight: 500;
}
.glow-card .card-value {
    font-family: 'Syne', sans-serif; font-size: 1.9rem;
    font-weight: 500; color: #e2e8f0; line-height: 1;
}
.glow-card .card-delta {
    font-family: 'JetBrains Mono', monospace; font-size: .7rem;
    margin-top: 6px;
}

/* ══════════════════════════════════════════
   MOBILE RESPONSIVE
══════════════════════════════════════════ */
@media (max-width: 768px) {
    .block-container { padding: 0.8rem 1rem !important; }
    .dash-header { padding: 14px 18px; border-radius: 14px; margin-bottom: 18px; }
    .hdr-title { font-size: 1rem !important; }
    .hdr-sub { font-size: .58rem !important; }
    .hdr-badge { font-size: .6rem !important; padding: 6px 12px !important; }
    [data-testid="stMetric"] { padding: 14px 16px !important; }
    [data-testid="stMetricValue"] { font-size: 1.5rem !important; }
    [data-testid="stMetricLabel"] { font-size: .6rem !important; }
    .scan-row { padding: 16px 16px; border-radius: 14px; }
    .step-card { padding: 14px 14px; border-radius: 12px; }
    .step-card-num { font-size: .56rem; }
    .step-card-text { font-size: .78rem; }
    .div-label { margin: 22px 0 16px; }
    .div-label span { font-size: .58rem; }
    .site-footer { padding: 20px; font-size: .62rem; }
    .stDownloadButton > button { font-size: .8rem !important; }
    .stAlert { font-size: .78rem !important; }
    h1 { font-size: 1.5rem !important; }
    h2 { font-size: 1.15rem !important; }
}

@media (max-width: 480px) {
    .block-container { padding: 0.6rem 0.7rem !important; }
    .dash-header { padding: 12px 14px; }
    .hdr-title { font-size: .9rem !important; }
    .hdr-icon { width: 38px; height: 38px; font-size: 1.1rem; }
    [data-testid="stMetricValue"] { font-size: 1.3rem !important; }
    .stButton > button[kind="primary"] {
        font-size: .82rem !important; padding: 12px 16px !important;
    }
    h1 { font-size: 1.3rem !important; }
}
</style>
"""


# ── Session defaults ──────────────────────────────────────────────────────────
for k, v in {
    'page': 'landing',
    'dashboard_page': 'dashboard',
    'authenticated': False,
    'show_register': False,
    'scan_completed': False,
    'domain_info': None,
    'subdomains': [],
    'vulnerabilities': [],
    'final_report': None,
    'scan_history': [],
    'direct_login_attempt': False,
    'agent_analysis': None,
    'agent_active': False,
    'remediation_plan': None,
    'fix_codes': {},
    'threat_intel_summary': None,
    'self_training_result': None,
    'agentic_pentest_result': None,
    'soc_triage_result': None,
    'last_saved_scan_report_id': None,
    'last_saved_pentest_report_id': None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
# ROUTING
# ══════════════════════════════════════════════════════════════════════════════

# ── LANDING PAGE ──────────────────────────────────────────────────────────────
if st.session_state.page == 'landing' and not st.session_state.authenticated:
    navigated = show_landing_page()
    if navigated:
        st.session_state.page = 'login'
        st.session_state.direct_login_attempt = False
        st.rerun()

# ── LOGIN / REGISTER ──────────────────────────────────────────────────────────
elif not st.session_state.authenticated:
    if st.session_state.page != 'login' or st.session_state.get('direct_login_attempt') is None:
        st.session_state.direct_login_attempt = True

    if st.session_state.show_register:
        show_register_page()
    else:
        show_login_page()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN SCANNER DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.markdown(SCANNER_CSS, unsafe_allow_html=True)

    # ── Dashboard Header ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="dash-header">
        <div class="hdr-logo">
            <div class="hdr-icon">
                <div class="brand-logo-ring">
                    <div class="brand-logo-bg"></div>
                    <div class="brand-logo-spin"></div>
                    <span class="brand-logo-icon">🛡</span>
                </div>
            </div>
            <div>
                <div class="hdr-title"><em>VULN</em>SAGE </div>
                <div class="hdr-sub">AI-Powered Web Vulnerability Scanner</div>
            </div>
        </div>
        <div class="hdr-badge">
            <div class="pulse-dot"></div>SYSTEM ONLINE
        </div>
    </div>
    """, unsafe_allow_html=True)

    show_logout_button()

    # Separate profile page for authenticated users
    if st.session_state.get("dashboard_page", "dashboard") == "profile":
        st.markdown('<div class="div-label"><span>Profile</span></div>', unsafe_allow_html=True)

        current_user = st.session_state.get("user_info", {})
        current_username = st.session_state.get("username", "")
        current_name = current_user.get("name", current_username)
        current_email = current_user.get("email", "")

        p_left, p_right = st.columns([2, 1])
        with p_left:
            st.markdown("""
            <div style="background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.14);
                border-radius:14px;padding:16px 18px;margin-bottom:12px;">
                <div style="font-family:'Syne',sans-serif;color:#e2e8f0;font-size:1.05rem;font-weight:700;">Update Your Profile</div>
                <div style="font-family:'Space Grotesk',sans-serif;color:#94a3b8;font-size:.85rem;margin-top:4px;">
                    Manage your account details. Username and email must remain unique.
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("profile_page_update_form", clear_on_submit=False):
                p_name = st.text_input("Full Name", value=current_name, key="profile_page_name")
                p_username = st.text_input("Username", value=current_username, key="profile_page_username")
                p_email = st.text_input("Email", value=current_email, key="profile_page_email")

                c_save, c_back = st.columns(2)
                with c_save:
                    save_profile = st.form_submit_button("Save Profile", use_container_width=True)
                with c_back:
                    back_dashboard = st.form_submit_button("Back to Dashboard", use_container_width=True)

            if save_profile:
                ok, msg, updated_user, resolved_username = update_user_profile(
                    current_username=current_username,
                    new_username=p_username,
                    new_name=p_name,
                    new_email=p_email
                )
                if ok:
                    st.session_state.username = resolved_username
                    st.session_state.user_info = {**st.session_state.get("user_info", {}), **(updated_user or {})}
                    admin_log_activity(resolved_username, "Updated profile details")
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

            if back_dashboard:
                st.session_state.dashboard_page = "dashboard"
                st.rerun()

        with p_right:
            st.markdown(f"""
            <div style="background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);
                border-radius:14px;padding:14px 16px;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:.12em;color:#64748b;text-transform:uppercase;">Current Account</div>
                <div style="margin-top:10px;font-family:'Syne',sans-serif;color:#e2e8f0;font-size:.92rem;">{current_name}</div>
                <div style="font-family:'JetBrains Mono',monospace;color:#94a3b8;font-size:.72rem;margin-top:2px;">@{current_username}</div>
                <div style="font-family:'Space Grotesk',sans-serif;color:#94a3b8;font-size:.8rem;margin-top:10px;">{current_email}</div>
                <div style="margin-top:10px;font-family:'JetBrains Mono',monospace;color:#34d399;font-size:.62rem;">Role: {current_user.get('role', 'user')}</div>
            </div>
            """, unsafe_allow_html=True)
        st.stop()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.header("⚙️ Config")
        scan_depth = st.select_slider("Scan Depth", ["Quick","Standard","Deep","Comprehensive"], value="Standard")
        max_subdomains = st.slider("Max Subdomains", 5, 50, 20)
        max_pages_per_domain = st.slider("Pages per Domain", 5, 30, 10)
        st.markdown("---")
        st.header("🤖 AI Features")
        enable_ai_recognition  = st.checkbox("AI Domain Recognition",  value=True)
        enable_smart_crawl     = st.checkbox("Smart Crawling",          value=True)
        enable_ml_model        = st.checkbox("ML Vuln Detection",       value=True, help="Random Forest model")
        enable_ai_validation   = st.checkbox("AI Vuln Validation",      value=True)
        enable_detailed_report = st.checkbox("Detailed AI Report",      value=True)
        enable_threat_intel_model = st.checkbox(
            "Threat-Intel Model",
            value=True,
            help="Use a self-trained model built from latest public CVE/KEV intelligence."
        )

        st.markdown("---")
        st.header("Threat Intel Agents")
        if st.button("Sync Latest Bugs", use_container_width=True):
            with st.spinner("Collecting latest vulnerabilities from public feeds..."):
                try:
                    intel_agent = ThreatIntelAgent()
                    intel_summary = intel_agent.collect_latest_bugs(max_items=250, days=45)
                    st.session_state.threat_intel_summary = intel_summary
                    st.success(
                        f"Synced {intel_summary.get('total_items', 0)} vulnerabilities "
                        f"(NVD: {intel_summary.get('sources', {}).get('nvd', 0)}, "
                        f"CISA KEV: {intel_summary.get('sources', {}).get('cisa_kev', 0)})."
                    )
                except Exception as e:
                    st.error(f"Threat intel sync failed: {e}")

        if st.button("Train Self-Learning Bug Model", use_container_width=True):
            with st.spinner("Training bug classifier from latest threat intelligence..."):
                try:
                    intel_agent = ThreatIntelAgent()
                    intel_summary = st.session_state.threat_intel_summary or intel_agent.load_cached_bugs()
                    trainer = SelfTrainingAgent()
                    result = trainer.train_from_intel(intel_summary)
                    st.session_state.self_training_result = result
                    if result.get("success"):
                        st.success(
                            f"Model trained on {result['samples']} samples across "
                            f"{len(result['classes'])} classes. Accuracy: {result['accuracy']}"
                        )
                    else:
                        st.warning(result.get("message", "Training did not complete."))
                except Exception as e:
                    st.error(f"Self-training failed: {e}")

        st.markdown("---")
        st.header("🤖 AI Security Agent")
        st.markdown("""
        <div style="background:rgba(99,102,241,.06);border:1px solid rgba(99,102,241,.12);
            border-radius:12px;padding:13px 16px;font-family:'Space Grotesk',sans-serif;font-size:.8rem;color:#94a3b8;margin-bottom:14px;">
            Autonomous vulnerability analysis &amp; remediation
        </div>""", unsafe_allow_html=True)

        agent_active = st.checkbox("Activate AI Agent", value=st.session_state.agent_active, key="agent_toggle")
        if agent_active != st.session_state.agent_active:
            st.session_state.agent_active = agent_active
            st.rerun()

        if st.session_state.agent_active and st.session_state.vulnerabilities:
            if st.button("🚀 Run Agent Analysis", use_container_width=True, type="primary"):
                with st.spinner("🤖 Agent analyzing vulnerabilities..."):
                    try:
                        orchestrator = GroqOrchestrator()
                        agent = SecurityAgent(orchestrator)
                        agent_results = agent.analyze_scan_results(
                            st.session_state.vulnerabilities,
                            st.session_state.domain_info
                        )
                        st.session_state.agent_analysis = agent_results
                        st.session_state.remediation_plan = agent_results.get('remediation_plan')
                        remediation_engine = RemediationEngine(orchestrator)
                        fix_codes = {}
                        for vuln in st.session_state.vulnerabilities:
                            if vuln.get('severity') in ['Critical', 'High']:
                                fix = remediation_engine.generate_fix(vuln)
                                fix_codes[vuln.get('type', 'unknown')] = fix
                        st.session_state.fix_codes = fix_codes
                        st.success("✅ Agent analysis complete!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Agent analysis failed: {e}")

        if st.session_state.agent_active:
            st.markdown("---")
            st.markdown("**Agent Status:**")
            if st.session_state.agent_analysis:
                progress = st.session_state.agent_analysis.get('progress', {})
                st.progress(progress.get('percentage', 0) / 100)
                st.markdown(f"""
                <div style="font-family:'JetBrains Mono',monospace;font-size:.7rem;color:#34d399;">
                    ✓ {progress.get('completed', 0)} tasks completed<br>
                    ⏳ {progress.get('pending', 0)} tasks pending
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="font-family:'JetBrains Mono',monospace;font-size:.7rem;color:#64748b;">
                    Agent ready. Run analysis after scan.
                </div>""", unsafe_allow_html=True)

        if st.session_state.scan_history:
            st.markdown("---")
            st.header("📊 History")
            st.markdown(f"""
            <div style="background:rgba(99,102,241,.06);border:1px solid rgba(99,102,241,.12);
                border-radius:12px;padding:13px 16px;font-family:'Space Grotesk',sans-serif;font-size:.8rem;color:#94a3b8;">
                Total Scans: <span style="color:#818cf8;font-weight:700;">{len(st.session_state.scan_history)}</span>
            </div>""", unsafe_allow_html=True)
            if st.button("Clear History"):
                st.session_state.scan_history = []
                st.rerun()

    # ── Scan Input ────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="scan-row">', unsafe_allow_html=True)
    c1, c2 = st.columns([4, 1])
    with c1:
        target_url = st.text_input(
            "Target URL or Domain",
            placeholder="example.com  or  https://example.com/page",
            help="Enter any URL — AI automatically extracts the domain"
        )
    with c2:
        st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
        scan_button = st.button("⚡  Scan", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="step-card"><span class="step-card-num">Step 01</span><div class="step-card-text">AI Domain Recognition</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="step-card"><span class="step-card-num">Step 02</span><div class="step-card-text">Subdomain Discovery</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="step-card"><span class="step-card-num">Step 03</span><div class="step-card-text">AI + ML Detection</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Scan Logic ────────────────────────────────────────────────────────────
    st.markdown('<div class="div-label"><span>Agentic Pentesting</span></div>', unsafe_allow_html=True)
    with st.expander("Advanced SQLi/XSS Pentesting + AI Agent Analysis", expanded=False):
        pentest_target_url = st.text_input(
            "Pentest Target URL",
            value=target_url if target_url else "",
            key="agentic_pentest_target_url",
            help="Authorized scope only",
        )
        pentest_params_text = st.text_area(
            "Parameters JSON",
            value='{"id":"1","q":"test"}',
            key="agentic_pentest_params_json",
            height=110,
        )

        p1, p2, p3 = st.columns(3)
        with p1:
            pentest_enable_time_based = st.checkbox("Time-based blind SQLi", value=True, key="agentic_pentest_enable_time")
        with p2:
            pentest_enable_ai = st.checkbox("Agentic AI analysis", value=True, key="agentic_pentest_enable_ai")
        with p3:
            pentest_time_retries = st.slider("Timing retries", 1, 5, 2, key="agentic_pentest_timing_retries")

        p4, p5, p6 = st.columns(3)
        with p4:
            pentest_enable_paths = st.checkbox("Attack path correlation", value=True, key="agentic_pentest_enable_paths")
        with p5:
            pentest_enable_fixes = st.checkbox("AI remediation fixes", value=True, key="agentic_pentest_enable_fixes")
        with p6:
            pentest_enable_training = st.checkbox("Self-training model", value=False, key="agentic_pentest_enable_training")

        p7, p8, p9 = st.columns(3)
        with p7:
            pentest_intel_mode = st.selectbox("Threat Intel Source", ["cached", "live", "off"], index=0, key="agentic_pentest_intel_mode")
        with p8:
            pentest_intel_days = st.slider("Intel lookback days", 7, 90, 30, key="agentic_pentest_intel_days")
        with p9:
            pentest_intel_items = st.slider("Max intel items", 50, 300, 120, 10, key="agentic_pentest_intel_items")

        pentest_run_button = st.button("Run Agentic Pentest", type="primary", use_container_width=True)

        if pentest_run_button:
            if not pentest_target_url:
                st.warning("Please enter a pentest target URL.")
            else:
                try:
                    pentest_params = json.loads(pentest_params_text)
                    if not isinstance(pentest_params, dict):
                        raise ValueError("Parameters must be a JSON object.")

                    with st.spinner("Running penetration tests and agentic analysis..."):
                        pentest_runner = AgenticPentestRunner()
                        pentest_result = pentest_runner.run(
                            url=pentest_target_url.strip(),
                            params=pentest_params,
                            method="GET",
                            enable_time_based=pentest_enable_time_based,
                            time_retries=pentest_time_retries,
                            enable_agentic_ai=pentest_enable_ai,
                            enable_attack_paths=pentest_enable_paths,
                            enable_remediation_fixes=pentest_enable_fixes,
                            threat_intel_mode=pentest_intel_mode,
                            intel_days=pentest_intel_days,
                            intel_max_items=pentest_intel_items,
                            enable_self_training=pentest_enable_training,
                        )
                    st.session_state.agentic_pentest_result = pentest_result
                    pentest_report_id = ReportsDB().save_pentest_report(
                        pentest_data=pentest_result,
                        target_url=pentest_target_url.strip(),
                        username=st.session_state.get("username", "unknown"),
                    )
                    st.session_state.last_saved_pentest_report_id = pentest_report_id
                    _log_activity(f"Agentic pentest complete on: {pentest_target_url}")
                    if pentest_report_id:
                        st.success(f"Agentic pentest completed. Report saved as: {pentest_report_id}")
                    else:
                        st.success("Agentic pentest completed.")
                except Exception as e:
                    st.error(f"Agentic pentest failed: {e}")

        pentest_output = st.session_state.get("agentic_pentest_result")
        if pentest_output:
            pentest_summary = pentest_output.get("summary", {})
            sm1, sm2, sm3, sm4 = st.columns(4)
            with sm1:
                st.metric("Total Findings", pentest_summary.get("total_findings", 0))
            with sm2:
                st.metric("Likely SQLi", pentest_summary.get("likely_sqli_count", 0))
            with sm3:
                st.metric("Reflected XSS", pentest_summary.get("reflected_xss_count", 0))
            with sm4:
                st.metric("Time-based SQLi", pentest_summary.get("time_based_vulnerable_count", 0))

            findings_tab, ai_tab, path_tab, fix_tab, intel_tab = st.tabs(
                ["Pentest Findings", "Agent Analysis", "Attack Paths", "Remediation Fixes", "Threat Intel"]
            )

            with findings_tab:
                pentest_findings = pentest_output.get("findings", [])
                if not pentest_findings:
                    st.info("No high-confidence pentest findings.")
                else:
                    for idx, f in enumerate(pentest_findings, 1):
                        sev = f.get("severity", "Medium")
                        color = {"Critical": "#f87171", "High": "#fb923c", "Medium": "#fbbf24", "Low": "#34d399"}.get(sev, "#94a3b8")
                        st.markdown(
                            f"""
                            <div style="background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.05);
                                border-left:3px solid {color};border-radius:0 12px 12px 0;padding:12px 14px;margin-bottom:8px;">
                                <div style="font-weight:600;color:#e2e8f0;">#{idx} {f.get('type', 'Unknown')}</div>
                                <div style="font-size:.82rem;color:#94a3b8;">Severity: {sev} | Risk Score: {f.get('risk_score', 'N/A')} | CWE: {f.get('cwe_id', 'N/A')}</div>
                                <div style="font-size:.82rem;color:#64748b;margin-top:6px;word-break:break-all;">{f.get('url', '')}</div>
                                <div style="font-size:.86rem;color:#cbd5e1;margin-top:6px;">{f.get('description', '')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        with st.expander(f"Evidence #{idx}", expanded=False):
                            st.json(f.get("evidence", {}))

                cta1, cta2 = st.columns([2, 2])
                with cta1:
                    if st.button("Ask Chatbot About Pentest Report", key="ask_chatbot_pentest", use_container_width=True):
                        st.session_state.report_chat_context = {
                            "source": "agentic_pentest",
                            "target_url": pentest_output.get("url"),
                            "summary": pentest_summary,
                            "findings": pentest_output.get("findings", [])[:20],
                            "attack_paths": pentest_output.get("attack_paths", {}),
                            "remediation_fixes": pentest_output.get("remediation_fixes", {}),
                        }
                        ask_chatbot_about_report(
                            "Explain this pentest report in simple terms and give me top priorities with exact next actions.",
                            source="agentic_pentest"
                        )
                        st.success("Chatbot opened with pentest context.")
                        st.rerun()
                with cta2:
                    if st.button("Ask for Technical Fix Plan", key="ask_chatbot_pentest_fix", use_container_width=True):
                        st.session_state.report_chat_context = {
                            "source": "agentic_pentest_fix_plan",
                            "target_url": pentest_output.get("url"),
                            "summary": pentest_summary,
                            "findings": pentest_output.get("findings", [])[:20],
                            "remediation_fixes": pentest_output.get("remediation_fixes", {}),
                        }
                        ask_chatbot_about_report(
                            "Create a technical remediation plan from this report with priorities, verification steps, and rollback notes.",
                            source="agentic_pentest"
                        )
                        st.success("Chatbot opened with fix-planning context.")
                        st.rerun()

            with ai_tab:
                if pentest_output.get("agentic_error"):
                    st.warning(f"AI analysis error: {pentest_output['agentic_error']}")
                agentic = pentest_output.get("agentic_analysis", {})
                if not agentic:
                    st.info("No agent analysis available for this run.")
                elif not isinstance(agentic, dict):
                    st.warning("AI analysis returned unexpected format.")
                    st.write(str(agentic))
                else:
                    summary = agentic.get("analysis_summary", {})
                    ac1, ac2, ac3 = st.columns(3)
                    with ac1:
                        st.metric("Total Analyzed", summary.get("total_vulnerabilities", 0))
                    with ac2:
                        st.metric("Critical", summary.get("critical_count", 0))
                    with ac3:
                        st.metric("High", summary.get("high_count", 0))
                    with st.expander("Priority Queue", expanded=True):
                        st.json(agentic.get("prioritized_vulnerabilities", [])[:10])
                    with st.expander("AI Remediation Plan", expanded=False):
                        st.json(agentic.get("remediation_plan", {}))

            with path_tab:
                paths = pentest_output.get("attack_paths", {})
                if not paths:
                    st.info("No attack-path analysis generated.")
                else:
                    pc1, pc2 = st.columns(2)
                    with pc1:
                        st.metric("Attack Chains", paths.get("attack_chains_count", 0))
                    with pc2:
                        st.metric("Critical Paths", len(paths.get("critical_paths", [])))
                    with st.expander("Critical Attack Paths", expanded=True):
                        st.json(paths.get("critical_paths", []))

            with fix_tab:
                fixes = pentest_output.get("remediation_fixes", {})
                if not fixes:
                    st.info("No remediation fix payload generated.")
                else:
                    for vuln_type, payload in fixes.items():
                        with st.expander(vuln_type, expanded=False):
                            st.json(payload)

            with intel_tab:
                intel = pentest_output.get("threat_intel", {})
                if not intel:
                    st.info("Threat intel enrichment disabled in this run.")
                else:
                    st.write({
                        "collected_at": intel.get("collected_at"),
                        "total_items": intel.get("total_items", 0),
                        "sources": intel.get("sources", {}),
                    })
                    st.json(intel.get("items", [])[:20])
    if scan_button:
        if not target_url:
            st.warning("⚠️ Please enter a target URL or domain.")
            st.stop()

        pb  = st.progress(0)
        stx = st.empty()

        def status(msg, col="#818cf8"):
            stx.markdown(
                f"<div style='font-family:JetBrains Mono,monospace;font-size:.8rem;"
                f"color:{col};letter-spacing:.03em;padding:6px 0;'>⬡ {msg}</div>",
                unsafe_allow_html=True
            )

        try:
            orchestrator = GroqOrchestrator()
            _log_activity(f"Started scan on: {target_url}")

            status("Initializing AI domain recognition...")
            pb.progress(10)
            domain_info = orchestrator.recognize_domain(target_url)
            st.success(f"✅ Domain identified: **{domain_info['domain']}**")

            with st.expander("🧠 AI Domain Analysis", expanded=False):
                st.json(domain_info)

            status("Enumerating subdomains...")
            pb.progress(25)
            scanner    = SubdomainScanner(max_subdomains=max_subdomains)
            subdomains = scanner.find_subdomains(domain_info['domain'])
            st.success(f"✅ Discovered **{len(subdomains)}** active subdomains")

            with st.expander("🌐 Discovered Subdomains", expanded=True):
                for i, sub in enumerate(subdomains, 1):
                    ip = sub.get('ip_address', 'N/A')
                    code = sub.get('status', '?')
                    server = sub.get('server', 'Unknown')
                    title = sub.get('title', 'N/A')
                    # Color HTTP status badge by code range
                    if isinstance(code, int) and code < 300:
                        badge_bg = 'rgba(52,211,153,.08)'
                        badge_border = 'rgba(52,211,153,.2)'
                        badge_color = '#34d399'
                    elif isinstance(code, int) and code < 400:
                        badge_bg = 'rgba(251,191,36,.08)'
                        badge_border = 'rgba(251,191,36,.2)'
                        badge_color = '#fbbf24'
                    else:
                        badge_bg = 'rgba(248,113,113,.08)'
                        badge_border = 'rgba(248,113,113,.2)'
                        badge_color = '#f87171'
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:14px;padding:13px 16px;
                        background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.05);
                        border-radius:12px;margin-bottom:6px;
                        font-family:'Space Grotesk',sans-serif;font-size:.82rem;flex-wrap:wrap;">
                        <span style="color:#64748b;font-family:'JetBrains Mono',monospace;font-size:.7rem;min-width:22px;">{i:02d}</span>
                        <div style="flex:1;min-width:180px;">
                            <div style="color:#e2e8f0;word-break:break-all;font-weight:500;">{sub['url']}</div>
                            <div style="display:flex;gap:16px;margin-top:4px;flex-wrap:wrap;">
                                <span style="font-family:'JetBrains Mono',monospace;font-size:.68rem;color:#818cf8;"
                                    title="Resolved IP">🌐 {ip}</span>
                                <span style="font-family:'JetBrains Mono',monospace;font-size:.68rem;color:#64748b;"
                                    title="Server">⚙️ {server}</span>
                                <span style="font-family:'Space Grotesk',sans-serif;font-size:.68rem;color:#94a3b8;"
                                    title="Page Title">📄 {title[:40]}</span>
                            </div>
                        </div>
                        <span style="background:{badge_bg};
                            border:1px solid {badge_border};color:{badge_color};
                            padding:4px 14px;border-radius:50px;font-size:.7rem;white-space:nowrap;
                            font-family:'JetBrains Mono',monospace;font-weight:600;">HTTP {code}</span>
                    </div>""", unsafe_allow_html=True)

            status("Running AI + ML vulnerability analysis...")
            pb.progress(50)

            model_path = 'vulnerability_model.pkl' if enable_ml_model else None
            detector   = VulnerabilityDetector(
                enable_ai=enable_ai_validation,
                max_pages=max_pages_per_domain,
                smart_crawl=enable_smart_crawl,
                model_path=model_path,
                enable_intel_model=enable_threat_intel_model,
                intel_model_path='bug_intel_model.pkl',
                max_ai_validations=20
            )

            all_vulns = []
            for idx, sub in enumerate(subdomains):
                pb.progress(50 + int(40*(idx+1)/len(subdomains)))
                status(f"Scanning {sub['url']}  ({idx+1}/{len(subdomains)})", "#94a3b8")
                v = detector.scan_target(sub['url'], orchestrator)
                if v:
                    all_vulns.extend(v)

            status("Generating AI security report...")
            pb.progress(95)

            rep_gen      = ReportGenerator()
            final_report = rep_gen.generate_report(
                domain_info=domain_info, subdomains=subdomains,
                vulnerabilities=all_vulns, orchestrator=orchestrator,
                detailed=enable_detailed_report
            )
            soc_triage = SOCCopilot(orchestrator=orchestrator).triage(
                vulnerabilities=all_vulns,
                domain_info=domain_info
            )

            pb.progress(100)
            stx.empty()

            st.session_state.update({
                'scan_completed': True,
                'domain_info': domain_info,
                'subdomains': subdomains,
                'vulnerabilities': all_vulns,
                'final_report': final_report,
                'soc_triage_result': soc_triage,
            })
            st.session_state.scan_history.append({
                'timestamp': datetime.now().isoformat(),
                'domain': domain_info['domain'],
                'subdomains_count': len(subdomains),
                'vulnerabilities_count': len(all_vulns),
                'scanned_by': st.session_state.username
            })
            saved_scan_report_id = ReportsDB().save_report(
                report_data=final_report,
                domain=domain_info['domain'],
                username=st.session_state.get("username", "unknown"),
            )
            st.session_state.last_saved_scan_report_id = saved_scan_report_id
            _log_activity(f"Scan complete: {domain_info['domain']} — {len(all_vulns)} vulns found")
            admin_log_activity(st.session_state.username, f"Scanned {domain_info['domain']} — {len(subdomains)} subdomains, {len(all_vulns)} vulns")
            if saved_scan_report_id:
                st.success(f"✅ Scan complete! Report saved as: {saved_scan_report_id}")
            else:
                st.success("✅ Scan complete!")

        except Exception as e:
            st.error(f"❌ Scan failed: {e}")
            import traceback
            with st.expander("🔍 Error Details"):
                st.code(traceback.format_exc())

    # ── Results ───────────────────────────────────────────────────────────────
    if st.session_state.scan_completed:
        di    = st.session_state.domain_info
        subs  = st.session_state.subdomains
        vulns = st.session_state.vulnerabilities
        rep   = st.session_state.final_report

        st.markdown('<div class="div-label"><span>Scan Results</span></div>', unsafe_allow_html=True)

        crit = sum(1 for v in vulns if v.get('severity')=='Critical')
        high = sum(1 for v in vulns if v.get('severity')=='High')

        # Custom glow metric cards
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            st.markdown(f"""
            <div class="glow-card">
                <div class="glow-orb" style="background:#818cf8;"></div>
                <div class="card-label">Domain</div>
                <div class="card-value" style="font-size:1.1rem;">{di['domain']}</div>
            </div>""", unsafe_allow_html=True)
        with mc2:
            st.markdown(f"""
            <div class="glow-card">
                <div class="glow-orb" style="background:#34d399;"></div>
                <div class="card-label">Subdomains</div>
                <div class="card-value">{len(subs)}</div>
                <div class="card-delta" style="color:#34d399;">● discovered</div>
            </div>""", unsafe_allow_html=True)
        with mc3:
            st.markdown(f"""
            <div class="glow-card">
                <div class="glow-orb" style="background:#f87171;"></div>
                <div class="card-label">Critical</div>
                <div class="card-value" style="color:#f87171;">{crit}</div>
                <div class="card-delta" style="color:#fb923c;">{high} high severity</div>
            </div>""", unsafe_allow_html=True)
        with mc4:
            st.markdown(f"""
            <div class="glow-card">
                <div class="glow-orb" style="background:#818cf8;"></div>
                <div class="card-label">Total Findings</div>
                <div class="card-value">{len(vulns)}</div>
                <div class="card-delta" style="color:#94a3b8;">vulnerabilities</div>
            </div>""", unsafe_allow_html=True)

        if vulns:
            st.markdown('<br>', unsafe_allow_html=True)
            st.markdown('<div class="div-label"><span>Vulnerabilities</span></div>', unsafe_allow_html=True)

            SEV_ORDER  = ['Critical','High','Medium','Low','Info']
            SEV_ICONS  = {'Critical':'🔴','High':'🟠','Medium':'🟡','Low':'🟢','Info':'⚪'}
            SEV_COLORS = {'Critical':'#f87171','High':'#fb923c','Medium':'#fbbf24','Low':'#34d399','Info':'#94a3b8'}

            groups = {s:[] for s in SEV_ORDER}
            for v in vulns:
                groups[v.get('severity','Info')].append(v)

            for sev in SEV_ORDER:
                if not groups[sev]: continue
                with st.expander(
                    f"{SEV_ICONS[sev]}  {sev}  —  {len(groups[sev])} finding{'s' if len(groups[sev])>1 else ''}",
                    expanded=(sev in ['Critical','High'])
                ):
                    for v in groups[sev]:
                        verification_label = v.get('confidence_band', 'Suspected')
                        verification_status = str(v.get('verification_status', 'suspected')).lower()
                        verification_color = {
                            'confirmed': '#34d399',
                            'probable': '#fbbf24',
                            'suspected': '#fb923c',
                            'info': '#94a3b8'
                        }.get(verification_status, '#94a3b8')
                        st.markdown(f"""
                        <div style="background:rgba(255,255,255,.02);
                            border:1px solid rgba(255,255,255,.05);
                            border-left:3px solid {SEV_COLORS[sev]};
                            border-radius:0 14px 14px 0;padding:18px 20px;margin-bottom:10px;">
                            <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;flex-wrap:wrap;">
                                <span style="font-weight:700;color:#e2e8f0;font-size:.95rem;font-family:'Syne',sans-serif;">{v['type']}</span>
                                <span style="font-family:'JetBrains Mono',monospace;font-size:.68rem;
                                    color:{SEV_COLORS[sev]};background:rgba(255,255,255,.03);
                                    border:1px solid rgba(255,255,255,.08);padding:3px 12px;border-radius:50px;">
                                    {v['confidence']}% confidence
                                </span>
                                <span style="font-family:'JetBrains Mono',monospace;font-size:.68rem;
                                    color:{verification_color};background:rgba(255,255,255,.03);
                                    border:1px solid rgba(255,255,255,.08);padding:3px 12px;border-radius:50px;">
                                    {verification_label}
                                </span>
                            </div>
                            <div style="font-family:'JetBrains Mono',monospace;font-size:.78rem;color:#64748b;margin-bottom:10px;word-break:break-all;">{v['url']}</div>
                            <div style="font-size:.88rem;color:#94a3b8;margin-bottom:8px;font-family:'Space Grotesk',sans-serif;line-height:1.6;">
                                <strong style="color:#cbd5e1;">Description:</strong> {v['description']}
                            </div>
                            <div style="font-size:.88rem;color:#94a3b8;font-family:'Space Grotesk',sans-serif;line-height:1.6;">
                                <strong style="color:#cbd5e1;">Fix:</strong> {v['recommendation']}
                            </div>
                        </div>""", unsafe_allow_html=True)
                        if 'proof' in v:
                            st.code(v['proof'], language='http')

        soc_data = st.session_state.get("soc_triage_result")
        if soc_data:
            st.markdown('<div class="div-label"><span>SOC Triage & Response</span></div>', unsafe_allow_html=True)

            sla = soc_data.get("sla_status", {})
            containment = soc_data.get("containment_steps", [])
            tasks = soc_data.get("tasks", [])

            sc1, sc2, sc3, sc4 = st.columns(4)
            with sc1:
                st.metric("SOC Tasks", soc_data.get("task_count", 0))
            with sc2:
                st.metric("Overdue", sla.get("overdue", 0))
            with sc3:
                st.metric("On Track", sla.get("on_track", 0))
            with sc4:
                st.metric("Containment", len(containment))

            st.markdown(f"""
            <div style="background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.14);
                border-radius:14px;padding:14px 16px;margin-bottom:12px;">
                <div style="font-family:'Syne',sans-serif;color:#e2e8f0;font-size:1rem;font-weight:700;">Incident Summary</div>
                <div style="font-family:'Space Grotesk',sans-serif;color:#94a3b8;font-size:.88rem;line-height:1.6;margin-top:6px;">
                    {soc_data.get('incident_summary', 'No summary available.')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if containment:
                with st.expander("Containment Steps", expanded=True):
                    for step in containment:
                        pri = step.get("priority", "ROUTINE")
                        pri_color = {"IMMEDIATE": "#f87171", "URGENT": "#fb923c", "ROUTINE": "#34d399"}.get(pri, "#94a3b8")
                        st.markdown(f"""
                        <div style="background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.05);
                            border-left:3px solid {pri_color};border-radius:0 12px 12px 0;padding:12px 14px;margin-bottom:8px;">
                            <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
                                <span style="font-family:'JetBrains Mono',monospace;font-size:.66rem;color:{pri_color};
                                    background:{pri_color}20;border:1px solid {pri_color}40;padding:3px 10px;border-radius:50px;">{pri}</span>
                                <span style="font-family:'Syne',sans-serif;font-size:.88rem;color:#e2e8f0;font-weight:600;">{step.get('action', '')}</span>
                            </div>
                            <div style="font-family:'Space Grotesk',sans-serif;font-size:.82rem;color:#94a3b8;margin-top:6px;">
                                {step.get('detail', '')}
                            </div>
                            <div style="font-family:'JetBrains Mono',monospace;font-size:.66rem;color:#64748b;margin-top:6px;">
                                SLA: {step.get('sla', 'N/A')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            if tasks:
                with st.expander("Remediation Task Queue", expanded=False):
                    task_rows = []
                    for t in tasks:
                        task_rows.append({
                            "Task ID": t.get("task_id"),
                            "Severity": t.get("severity"),
                            "Priority": t.get("priority"),
                            "Type": t.get("vuln_type"),
                            "Owner": t.get("owner"),
                            "Status": t.get("status"),
                            "Response Due": t.get("response_due", "")[:19].replace("T", " "),
                            "Fix Due": t.get("fix_due", "")[:19].replace("T", " "),
                        })
                    st.dataframe(task_rows, use_container_width=True, hide_index=True)

            if soc_data.get("ai_triage"):
                with st.expander("AI SOC Triage Notes", expanded=False):
                    st.markdown(soc_data["ai_triage"])

        # ── AI Agent Results ──────────────────────────────────────────────────
        if st.session_state.agent_active and st.session_state.agent_analysis:
            st.markdown('<div class="div-label"><span>🤖 AI Agent Analysis</span></div>', unsafe_allow_html=True)

            agent_data = st.session_state.agent_analysis

            with st.expander("🎯 Prioritized Vulnerabilities", expanded=True):
                st.markdown("""
                <div style="background:rgba(99,102,241,.06);border:1px solid rgba(99,102,241,.12);
                    border-radius:14px;padding:16px;margin-bottom:16px;">
                    <h4 style="color:#818cf8;margin:0 0 8px 0;font-family:'Syne',sans-serif;font-size:1rem;">Agent Prioritization</h4>
                    <p style="color:#94a3b8;font-size:.85rem;margin:0;font-family:'Space Grotesk',sans-serif;">
                        AI agent analyzed and prioritized vulnerabilities based on risk, exploitability, and business impact.
                    </p>
                </div>""", unsafe_allow_html=True)

                for i, vuln in enumerate(agent_data.get('prioritized_vulnerabilities', [])[:5], 1):
                    priority = vuln.get('priority_rank', i)
                    severity = vuln.get('severity', 'Unknown')
                    color = {'Critical': '#f87171', 'High': '#fb923c', 'Medium': '#fbbf24', 'Low': '#34d399'}.get(severity, '#94a3b8')

                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:14px;padding:14px 16px;
                        background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.05);
                        border-left:3px solid {color};border-radius:0 12px 12px 0;margin-bottom:8px;">
                        <span style="font-family:'JetBrains Mono',monospace;font-size:1rem;color:{color};font-weight:700;">#{priority}</span>
                        <div style="flex:1;">
                            <div style="font-weight:600;color:#e2e8f0;font-size:.9rem;font-family:'Syne',sans-serif;">{vuln.get('type', 'Unknown')}</div>
                            <div style="font-family:'JetBrains Mono',monospace;font-size:.7rem;color:#64748b;">{vuln.get('url', '')}</div>
                        </div>
                        <span style="background:{color}15;border:1px solid {color}30;color:{color};
                            padding:4px 12px;border-radius:50px;font-size:.7rem;font-family:'JetBrains Mono',monospace;">
                            {severity}
                        </span>
                    </div>""", unsafe_allow_html=True)

            # Remediation Plan
            if st.session_state.remediation_plan:
                with st.expander("📋 AI Remediation Plan", expanded=True):
                    plan = st.session_state.remediation_plan

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        immediate = len(plan.get('immediate_actions', []))
                        st.metric("Immediate (24h)", immediate, delta=f"Fix now" if immediate > 0 else None)
                    with col2:
                        short_term = len(plan.get('short_term_actions', []))
                        st.metric("Short-term (7d)", short_term)
                    with col3:
                        long_term = len(plan.get('long_term_improvements', []))
                        st.metric("Long-term (30d)", long_term)

                    if plan.get('immediate_actions'):
                        st.markdown("#### 🚨 Immediate Actions")
                        for action in plan['immediate_actions']:
                            st.markdown(f"""
                            <div style="background:rgba(248,113,113,.06);border:1px solid rgba(248,113,113,.15);
                                border-radius:12px;padding:14px;margin-bottom:8px;">
                                <div style="font-weight:600;color:#fca5a5;font-size:.9rem;font-family:'Syne',sans-serif;">{action.get('action', 'Action')}</div>
                                <div style="color:#94a3b8;font-size:.8rem;margin-top:6px;font-family:'Space Grotesk',sans-serif;">
                                    Est. time: {action.get('estimated_time', 'Unknown')} |
                                    Risk if delayed: {action.get('risk_if_delayed', 'Unknown')}
                                </div>
                            </div>""", unsafe_allow_html=True)

            # Fix Code Snippets
            if st.session_state.fix_codes:
                with st.expander("🔧 Generated Fix Code", expanded=True):
                    st.markdown("""
                    <div style="background:rgba(99,102,241,.06);border:1px solid rgba(99,102,241,.12);
                        border-radius:14px;padding:16px;margin-bottom:16px;">
                        <h4 style="color:#818cf8;margin:0 0 8px 0;font-family:'Syne',sans-serif;font-size:1rem;">Production-Ready Fixes</h4>
                        <p style="color:#94a3b8;font-size:.85rem;margin:0;font-family:'Space Grotesk',sans-serif;">
                            AI-generated fix code for critical and high-severity vulnerabilities.
                        </p>
                    </div>""", unsafe_allow_html=True)

                    for vuln_type, fix_data in st.session_state.fix_codes.items():
                        with st.expander(f"🔨 {vuln_type}", expanded=False):
                            if 'code_examples' in fix_data:
                                for lang, code_example in fix_data['code_examples'].items():
                                    st.markdown(f"**{code_example.get('description', lang)}**")
                                    if 'vulnerable_code' in code_example:
                                        st.markdown("❌ **Vulnerable:**")
                                        st.code(code_example['vulnerable_code'], language=code_example.get('language', 'python'))
                                    if 'secure_code' in code_example:
                                        st.markdown("✅ **Secure:**")
                                        st.code(code_example['secure_code'], language=code_example.get('language', 'python'))
                                    if 'explanation' in code_example:
                                        st.info(code_example['explanation'])

                            if 'configuration_fix' in fix_data:
                                st.markdown("**⚙️ Configuration Fix:**")
                                config = fix_data['configuration_fix']
                                if 'nginx_config' in config:
                                    with st.expander("Nginx Config"):
                                        st.code(config['nginx_config'], language='nginx')
                                if 'apache_config' in config:
                                    with st.expander("Apache Config"):
                                        st.code(config['apache_config'], language='apache')

                            if 'deployment_steps' in fix_data:
                                st.markdown("**🚀 Deployment Steps:**")
                                for step in fix_data['deployment_steps']:
                                    st.markdown(f"- {step}")

                            if 'verification_commands' in fix_data:
                                st.markdown("**✅ Verification:**")
                                for cmd in fix_data['verification_commands']:
                                    st.code(cmd, language='bash')
        st.markdown('<div class="div-label"><span>AI Report</span></div>', unsafe_allow_html=True)
        with st.expander("Full AI Security Analysis Report", expanded=True):
            st.markdown(rep['markdown_report'])

        rc1, rc2 = st.columns(2)
        with rc1:
            if st.button("Ask Chatbot About This Scan Report", key="ask_chatbot_scan_report", use_container_width=True):
                st.session_state.report_chat_context = {
                    "source": "scan_report",
                    "domain_info": di,
                    "subdomains_count": len(subs),
                    "vulnerability_count": len(vulns),
                    "vulnerabilities": vulns[:25],
                    "agent_analysis": st.session_state.get("agent_analysis"),
                    "remediation_plan": st.session_state.get("remediation_plan"),
                    "report_markdown_preview": rep.get("markdown_report", "")[:4000],
                }
                ask_chatbot_about_report(
                    "Summarize this scan report for stakeholders and list top 5 urgent fixes with rationale.",
                    source="scan_report"
                )
                st.success("Chatbot opened with scan-report context.")
                st.rerun()

        with rc2:
            if st.button("Ask Chatbot For Dev Fix Steps", key="ask_chatbot_scan_fix", use_container_width=True):
                st.session_state.report_chat_context = {
                    "source": "scan_report_dev_fix",
                    "domain_info": di,
                    "vulnerabilities": vulns[:25],
                    "fix_codes": st.session_state.get("fix_codes", {}),
                    "remediation_plan": st.session_state.get("remediation_plan"),
                }
                ask_chatbot_about_report(
                    "Give me developer-focused remediation steps from this report including code-level fixes and verification commands.",
                    source="scan_report"
                )
                st.success("Chatbot opened with developer-fix context.")
                st.rerun()

        st.markdown('<div class="div-label"><span>Export</span></div>', unsafe_allow_html=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        d  = di['domain']
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("📥 JSON", data=json.dumps(rep['json_report'], indent=2), file_name=f"scan_{d}_{ts}.json", mime="application/json", use_container_width=True)
        with c2:
            st.download_button("📥 Markdown", data=rep['markdown_report'], file_name=f"report_{d}_{ts}.md", mime="text/markdown", use_container_width=True)
        with c3:
            csv = "URL,Type,Severity,Confidence,Verification,Description\n" + "".join(
                f'"{v["url"]}","{v["type"]}","{v["severity"]}","{v["confidence"]}","{v.get("confidence_band","Suspected")}","{v["description"]}"\n'
                for v in vulns)
            st.download_button("📥 CSV", data=csv, file_name=f"vulns_{d}_{ts}.csv", mime="text/csv", use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # ADMIN PANEL — only visible to admin users
    # ══════════════════════════════════════════════════════════════════════════
    if st.session_state.get('user_info', {}).get('role') == 'admin':
        st.markdown('<div class="div-label"><span>Admin Panel</span></div>', unsafe_allow_html=True)

        logs = get_all_logs()
        all_users = load_users()

        admin_scanning_tab, admin_logs_tab = st.tabs(["Scanning", "Logs"])

        with admin_scanning_tab:
            scan_history = st.session_state.get('scan_history', [])
            total_scans = len(scan_history)
            total_vulns_found = sum(item.get('vulnerabilities_count', 0) for item in scan_history)
            total_subdomains_seen = sum(item.get('subdomains_count', 0) for item in scan_history)

            sm1, sm2, sm3, sm4 = st.columns(4)
            with sm1:
                st.markdown(f"""
                <div class="glow-card">
                    <div class="glow-orb" style="background:#818cf8;"></div>
                    <div class="card-label">Total Scans</div>
                    <div class="card-value">{total_scans}</div>
                </div>""", unsafe_allow_html=True)
            with sm2:
                st.markdown(f"""
                <div class="glow-card">
                    <div class="glow-orb" style="background:#34d399;"></div>
                    <div class="card-label">Subdomains Seen</div>
                    <div class="card-value">{total_subdomains_seen}</div>
                </div>""", unsafe_allow_html=True)
            with sm3:
                st.markdown(f"""
                <div class="glow-card">
                    <div class="glow-orb" style="background:#f59e0b;"></div>
                    <div class="card-label">Vulns Found</div>
                    <div class="card-value">{total_vulns_found}</div>
                </div>""", unsafe_allow_html=True)
            with sm4:
                last_scan = "N/A"
                if scan_history:
                    last_scan = scan_history[-1].get('timestamp', '').replace('T', ' ')[:19]
                st.markdown(f"""
                <div class="glow-card">
                    <div class="glow-orb" style="background:#06b6d4;"></div>
                    <div class="card-label">Last Scan</div>
                    <div class="card-value" style="font-size:1rem;">{last_scan}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown('<div class="div-label"><span>Recent Scan History</span></div>', unsafe_allow_html=True)
            if scan_history:
                for item in reversed(scan_history[-50:]):
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:14px;padding:10px 16px;
                        background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.04);
                        border-radius:10px;margin-bottom:5px;flex-wrap:wrap;">
                        <span style="color:#818cf8;font-size:.72rem;letter-spacing:.08em;">SCAN</span>
                        <div style="flex:1;">
                            <span style="color:#e2e8f0;font-weight:600;font-size:.88rem;">{item.get('domain', 'Unknown')}</span>
                            <span style="color:#64748b;font-size:.78rem;"> by @{item.get('scanned_by', 'unknown')}</span>
                        </div>
                        <span style="color:#34d399;font-size:.72rem;letter-spacing:.08em;">SUB: {item.get('subdomains_count', 0)}</span>
                        <span style="color:#f59e0b;font-size:.72rem;letter-spacing:.08em;">VULN: {item.get('vulnerabilities_count', 0)}</span>
                        <span style="font-family:'JetBrains Mono',monospace;font-size:.68rem;color:#64748b;">
                            {item.get('timestamp', '').replace('T', ' ')[:19]}
                        </span>
                    </div>""", unsafe_allow_html=True)
            else:
                st.info("No scans recorded yet in this session.")

        with admin_logs_tab:
            # Admin metrics row
            am1, am2, am3, am4 = st.columns(4)
            with am1:
                st.markdown(f"""
                <div class="glow-card">
                    <div class="glow-orb" style="background:#818cf8;"></div>
                    <div class="card-label">Total Users</div>
                    <div class="card-value">{len(all_users)}</div>
                </div>""", unsafe_allow_html=True)
            with am2:
                st.markdown(f"""
                <div class="glow-card">
                    <div class="glow-orb" style="background:#34d399;"></div>
                    <div class="card-label">New Registrations</div>
                    <div class="card-value">{len(logs.get('registrations', []))}</div>
                </div>""", unsafe_allow_html=True)
            with am3:
                st.markdown(f"""
                <div class="glow-card">
                    <div class="glow-orb" style="background:#818cf8;"></div>
                    <div class="card-label">Successful Logins</div>
                    <div class="card-value">{get_total_logins()}</div>
                </div>""", unsafe_allow_html=True)
            with am4:
                st.markdown(f"""
                <div class="glow-card">
                    <div class="glow-orb" style="background:#f87171;"></div>
                    <div class="card-label">Failed Logins</div>
                    <div class="card-value" style="color:#f87171;">{get_failed_logins()}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown('<br>', unsafe_allow_html=True)

            with st.expander("Registered Users", expanded=True):
                if all_users:
                    for uname, udata in all_users.items():
                        role_color = '#818cf8' if udata.get('role') == 'admin' else '#34d399'
                        role_label = udata.get('role', 'user').upper()
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:14px;padding:12px 16px;
                            background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.05);
                            border-radius:12px;margin-bottom:6px;flex-wrap:wrap;">
                            <span style="font-size:.65rem;color:#818cf8;letter-spacing:.08em;">USR</span>
                            <div style="flex:1;">
                                <div style="color:#e2e8f0;font-weight:600;font-family:'Syne',sans-serif;font-size:.92rem;">{udata.get('name', uname)}</div>
                                <div style="font-family:'JetBrains Mono',monospace;font-size:.7rem;color:#64748b;">@{uname}</div>
                            </div>
                            <span style="background:{role_color}15;border:1px solid {role_color}30;color:{role_color};
                                padding:4px 14px;border-radius:50px;font-size:.68rem;
                                font-family:'JetBrains Mono',monospace;font-weight:600;">{role_label}</span>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.info("No registered users yet.")

            st.markdown('<div class="div-label"><span>Admin Logs</span></div>', unsafe_allow_html=True)
            registration_tab, login_tab, activity_tab = st.tabs([
                "Registration Log",
                "Login History",
                "Activity Log"
            ])

            with registration_tab:
                regs = logs.get('registrations', [])
                if regs:
                    for reg in reversed(regs[-50:]):
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:14px;padding:10px 16px;
                            background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.04);
                            border-radius:10px;margin-bottom:5px;flex-wrap:wrap;">
                            <span style="color:#34d399;font-size:.75rem;letter-spacing:.08em;">NEW</span>
                            <div style="flex:1;">
                                <span style="color:#e2e8f0;font-weight:500;font-size:.88rem;">{reg.get('name', reg['username'])}</span>
                                <span style="color:#64748b;font-size:.8rem;"> (@{reg['username']})</span>
                            </div>
                            <span style="font-family:'JetBrains Mono',monospace;font-size:.68rem;color:#64748b;">
                                {reg['date']} - {reg['time']}
                            </span>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.info("No registrations recorded yet.")

            with login_tab:
                logins = logs.get('logins', [])
                if logins:
                    for entry in reversed(logins[-50:]):
                        if entry['success']:
                            icon = 'OK'
                            label_color = '#34d399'
                            label_text = 'SUCCESS'
                        else:
                            icon = 'NO'
                            label_color = '#f87171'
                            label_text = 'FAILED'
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:14px;padding:10px 16px;
                            background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.04);
                            border-radius:10px;margin-bottom:5px;flex-wrap:wrap;">
                            <span style="font-size:.72rem;color:{label_color};letter-spacing:.08em;">{icon}</span>
                            <div style="flex:1;">
                                <span style="color:#e2e8f0;font-weight:500;font-size:.88rem;">@{entry['username']}</span>
                                <span style="color:#64748b;font-size:.78rem;"> ({entry.get('role', '?')})</span>
                            </div>
                            <span style="background:{label_color}15;border:1px solid {label_color}30;color:{label_color};
                                padding:3px 12px;border-radius:50px;font-size:.65rem;
                                font-family:'JetBrains Mono',monospace;font-weight:600;">{label_text}</span>
                            <span style="font-family:'JetBrains Mono',monospace;font-size:.68rem;color:#64748b;">
                                {entry['date']} - {entry['time']}
                            </span>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.info("No login history recorded yet.")

            with activity_tab:
                activities = logs.get('activity', [])
                if activities:
                    for act in reversed(activities[-50:]):
                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:14px;padding:9px 16px;
                            background:rgba(255,255,255,.012);border:1px solid rgba(255,255,255,.03);
                            border-radius:10px;margin-bottom:4px;flex-wrap:wrap;">
                            <span style="color:#818cf8;font-size:.7rem;letter-spacing:.08em;">LOG</span>
                            <span style="color:#94a3b8;font-size:.82rem;flex:1;">{act['action']}</span>
                            <span style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:#475569;">@{act['username']}</span>
                            <span style="font-family:'JetBrains Mono',monospace;font-size:.65rem;color:#475569;">{act['time']}</span>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.info("No activity recorded yet.")

    # AGENTIC AI CHATBOT - positioned above footer
    render_chatbot()

    st.markdown("""
    <div class="site-footer">
        <span class="brand-logo-ring foot-logo">
            <span class="brand-logo-bg"></span>
            <span class="brand-logo-spin"></span>
            <span class="brand-logo-icon">🛡</span>
        </span>        <span class="site-footer-text">
            <span>Powered by <em>VulnSage</em></span>
            <span class="site-footer-sub">AI-Powered Web Vulnerability Scanner</span>
            <span>� For authorized security testing only</span>
        </span>
    </div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # AGENTIC AI CHATBOT — bottom-right corner
    # ══════════════════════════════════════════════════════════════════════════









