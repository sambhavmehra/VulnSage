"""
landing_page.py
Ultra-premium redesign — Deep Space Neon Cybersecurity Theme.
Electric cyan + violet + magenta palette on near-black background.
Returns True when any primary CTA is clicked.
"""
import streamlit as st

LANDING_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ══ RESET & FORCE DARK ══ */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"], .stApp, .main,
[data-testid="stMain"], [data-testid="stHeader"] {
    background-color: #050508 !important;
    background: #050508 !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}
#MainMenu, header, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display:none !important; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
    margin: 0 !important;
}
* { box-sizing: border-box; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #050508; }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,.4); border-radius: 2px; }

/* ══ CSS VARIABLES ══ */
:root {
    --cyan:       #06b6d4;
    --cyan-glow:  rgba(6,182,212,.5);
    --violet:     #8b5cf6;
    --violet-glow:rgba(139,92,246,.5);
    --magenta:    #ec4899;
    --mag-glow:   rgba(236,72,153,.3);
    --green:      #10b981;
    --amber:      #f59e0b;
    --red:        #ef4444;
    --bg:         #050508;
    --bg-1:       #0a0a12;
    --bg-2:       #0f0f1a;
    --bg-card:    rgba(255,255,255,.04);
    --border:     rgba(255,255,255,.08);
    --border-c:   rgba(6,182,212,.25);
    --text-1:     #f1f5f9;
    --text-2:     #94a3b8;
    --text-3:     #475569;
    --font-sans:  'Inter', sans-serif;
    --font-grotesk:'Space Grotesk', sans-serif;
    --font-mono:  'JetBrains Mono', monospace;
    --radius:     12px;
    --radius-lg:  20px;
    --radius-xl:  28px;
}

/* ══ ANIMATED BACKGROUND ══ */
.bg-canvas {
    position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden;
}

/* Radial glow orbs */
.bg-canvas::before {
    content: '';
    position: absolute; inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 10% 10%, rgba(139,92,246,.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 80%, rgba(6,182,212,.1) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 50% 50%, rgba(236,72,153,.06) 0%, transparent 50%);
    animation: bgPulse 14s ease-in-out infinite alternate;
}
@keyframes bgPulse {
    from { opacity: .7; transform: scale(1) rotate(0deg); }
    to   { opacity: 1;  transform: scale(1.05) rotate(1deg); }
}

/* Dot grid pattern */
.bg-canvas::after {
    content: '';
    position: fixed; inset: 0;
    background-image: radial-gradient(circle, rgba(99,102,241,.18) 1px, transparent 1px);
    background-size: 40px 40px;
    mask-image: radial-gradient(ellipse 100% 100% at 50% 50%, black 30%, transparent 80%);
    animation: gridDrift 20s linear infinite;
}
@keyframes gridDrift {
    from { background-position: 0 0; }
    to   { background-position: 40px 40px; }
}

/* Horizontal scan line */
.scan-beam {
    position: fixed; left: 0; right: 0; height: 1px; z-index: 0; pointer-events: none;
    background: linear-gradient(90deg, transparent 0%, rgba(6,182,212,.6) 40%, rgba(139,92,246,.6) 60%, transparent 100%);
    animation: scanBeam 8s ease-in-out infinite;
    top: 0;
}
@keyframes scanBeam {
    0%   { top: 0%; opacity: 0; }
    5%   { opacity: 1; }
    95%  { opacity: .3; }
    100% { top: 100%; opacity: 0; }
}

/* ══ WRAPPER ══ */
.lp { position: relative; z-index: 1; }

/* ══════════════════════════════════════
   NAVBAR
══════════════════════════════════════ */
.navbar {
    position: sticky; top: 0; z-index: 200;
    background: rgba(5,5,8,.8);
    backdrop-filter: blur(32px) saturate(1.8);
    border-bottom: 1px solid rgba(255,255,255,.06);
    padding: 0 40px;
}
.nav-inner {
    max-width: 1280px; margin: 0 auto;
    height: 68px;
    display: flex; align-items: center; justify-content: space-between;
}
.nav-brand {
    display: flex; align-items: center; gap: 12px;
}
.nav-logo-ring {
    position: relative; width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
}
.nav-logo-ring::before {
    content: '';
    position: absolute; inset: 0;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--cyan), var(--violet));
    opacity: .15;
}
.nav-logo-ring::after {
    content: '';
    position: absolute; inset: 0;
    border-radius: 10px;
    border: 1px solid;
    border-image: linear-gradient(135deg, var(--cyan), var(--violet)) 1;
    border-radius: 10px;
    animation: logoSpin 12s linear infinite;
}
@keyframes logoSpin {
    to { transform: rotate(360deg); }
}
.nav-logo-icon {
    font-size: 1rem; position: relative; z-index: 1;
    background: linear-gradient(135deg, var(--cyan), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.nav-wordmark {
    font-family: var(--font-grotesk);
    font-size: .82rem; font-weight: 700;
    letter-spacing: .12em; text-transform: uppercase;
    color: var(--text-1);
}
.nav-wordmark em {
    font-style: normal;
    background: linear-gradient(90deg, var(--cyan), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.nav-status-chip {
    display: flex; align-items: center; gap: 8px;
    padding: 5px 14px;
    background: rgba(16,185,129,.08);
    border: 1px solid rgba(16,185,129,.22);
    border-radius: 50px;
    font-family: var(--font-mono); font-size: .6rem;
    color: var(--green); letter-spacing: .1em;
}
.status-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: statusPulse 2s ease infinite;
}
@keyframes statusPulse { 50% { opacity: .3; transform: scale(.7); } }

/* ══════════════════════════════════════
   HERO
══════════════════════════════════════ */
.hero-section {
    max-width: 1280px; margin: 0 auto;
    padding: 80px 40px 60px;
    display: grid; grid-template-columns: 1.1fr .9fr;
    gap: 64px; align-items: center;
    position: relative;
}
/* Eyebrow badge */
.hero-badge {
    display: inline-flex; align-items: center; gap: 10px;
    padding: 8px 18px;
    background: linear-gradient(90deg, rgba(6,182,212,.1), rgba(139,92,246,.1));
    border: 1px solid rgba(6,182,212,.3);
    border-radius: 50px;
    font-family: var(--font-mono); font-size: .62rem;
    letter-spacing: .14em; color: var(--cyan);
    margin-bottom: 28px;
    opacity: 0; animation: slideUp .6s .1s ease forwards;
}
.hero-badge-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 10px var(--cyan);
    animation: statusPulse 1.8s ease infinite;
}
/* Main heading */
.hero-h1 {
    font-family: var(--font-grotesk);
    font-size: clamp(2.6rem, 4.8vw, 4.8rem);
    font-weight: 800; line-height: 1.05;
    color: var(--text-1);
    letter-spacing: -.03em;
    margin-bottom: 8px;
    opacity: 0; animation: slideUp .6s .2s ease forwards;
}
.hero-h1 .grad {
    background: linear-gradient(135deg, var(--cyan) 0%, var(--violet) 50%, var(--magenta) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-h1-sub {
    font-family: var(--font-grotesk);
    font-size: clamp(1.1rem, 2vw, 1.6rem);
    font-weight: 400; color: var(--text-2);
    letter-spacing: -.01em; margin-bottom: 24px;
    opacity: 0; animation: slideUp .6s .3s ease forwards;
}
.hero-desc {
    font-size: .9rem; color: var(--text-2);
    line-height: 1.8; margin-bottom: 36px;
    opacity: 0; animation: slideUp .6s .4s ease forwards;
    max-width: 520px;
}
.hero-actions {
    display: flex; gap: 14px; flex-wrap: wrap;
    opacity: 0; animation: slideUp .6s .5s ease forwards;
}

/* Stats row */
.hero-stats {
    display: flex; gap: 32px; margin-top: 44px;
    opacity: 0; animation: slideUp .6s .65s ease forwards;
    border-top: 1px solid var(--border);
    padding-top: 28px;
}
.stat-block {}
.stat-value {
    font-family: var(--font-grotesk);
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg, var(--cyan), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1; display: block;
}
.stat-label {
    font-family: var(--font-mono); font-size: .62rem;
    color: var(--text-3); letter-spacing: .1em;
    text-transform: uppercase; margin-top: 4px;
    display: block;
}

/* ══ HERO RIGHT: Live Terminal ══ */
.term-wrap {
    opacity: 0; animation: slideUp .6s .45s ease forwards;
}
.term-frame {
    background: var(--bg-1);
    border: 1px solid rgba(99,102,241,.2);
    border-radius: var(--radius-xl);
    overflow: hidden;
    box-shadow:
        0 0 0 1px rgba(99,102,241,.08),
        0 40px 80px rgba(0,0,0,.6),
        0 0 60px rgba(139,92,246,.08);
    position: relative;
}
.term-frame::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 10%, var(--cyan) 40%, var(--violet) 60%, transparent 90%);
    opacity: .7;
}
.term-topbar {
    background: rgba(255,255,255,.03);
    border-bottom: 1px solid rgba(255,255,255,.06);
    padding: 14px 20px;
    display: flex; align-items: center; gap: 14px;
}
.term-circs { display: flex; gap: 7px; }
.tc { width: 12px; height: 12px; border-radius: 50%; }
.tc-r { background: #ff5f57; }
.tc-y { background: #febc2e; }
.tc-g { background: #28c840; }
.term-title {
    flex: 1; text-align: center;
    font-family: var(--font-mono); font-size: .65rem;
    color: var(--text-3); letter-spacing: .08em;
}
.ping-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--green); box-shadow: 0 0 8px var(--green);
    animation: statusPulse 2.5s ease infinite;
}
.term-body { padding: 22px 22px 26px; }
.t-line {
    display: flex; align-items: flex-start; gap: 10px;
    margin-bottom: 10px;
    font-family: var(--font-mono); font-size: .76rem;
    opacity: 0; animation: termLine .3s ease forwards;
}
.t-line:nth-child(1) { animation-delay: 1.2s; }
.t-line:nth-child(2) { animation-delay: 2.0s; }
.t-line:nth-child(3) { animation-delay: 2.8s; }
.t-line:nth-child(4) { animation-delay: 3.6s; }
.t-line:nth-child(5) { animation-delay: 4.4s; }
.t-line:nth-child(6) { animation-delay: 5.2s; }
.t-line:nth-child(7) { animation-delay: 6.0s; }
@keyframes termLine { to { opacity: 1; } }
.t-prompt { color: var(--cyan); flex-shrink: 0; }
.t-mute   { color: var(--text-3); }
.t-ok     { color: var(--green); }
.t-warn   { color: var(--amber); }
.t-err    { color: var(--red); }
.t-info   { color: var(--violet); }
.t-cursor {
    display: inline-block; width: 7px; height: 14px;
    background: var(--cyan); margin-left: 3px;
    animation: blink .9s step-end infinite;
    vertical-align: text-bottom; border-radius: 1px;
}
@keyframes blink { 50% { opacity: 0; } }

/* Progress bar inside terminal */
.t-progress-bar {
    height: 3px; background: rgba(255,255,255,.06);
    border-radius: 2px; margin: 8px 0 4px; overflow: hidden;
}
.t-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--cyan), var(--violet));
    border-radius: 2px;
    box-shadow: 0 0 8px var(--cyan-glow);
    animation: progFill 4s 1.5s ease forwards;
    width: 0%;
}
@keyframes progFill { to { width: 87%; } }

/* ══════════════════════════════════════
   SHARED BUTTON STYLES  (via Streamlit)
══════════════════════════════════════ */
div[data-testid="stButton"] > button {
    height: 50px !important;
    border-radius: var(--radius) !important;
    font-family: var(--font-grotesk) !important;
    font-size: .8rem !important;
    font-weight: 600 !important;
    letter-spacing: .04em !important;
    transition: all .3s cubic-bezier(.23,1,.32,1) !important;
    white-space: nowrap !important;
}
/* PRIMARY — gradient */
div[data-testid="stButton"].btn-primary > button {
    background: linear-gradient(135deg, var(--cyan) 0%, var(--violet) 100%) !important;
    color: #fff !important;
    border: none !important;
    box-shadow: 0 8px 32px rgba(139,92,246,.35), 0 0 0 1px rgba(255,255,255,.1) inset !important;
}
div[data-testid="stButton"].btn-primary > button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 18px 48px rgba(139,92,246,.55), 0 0 30px rgba(6,182,212,.3) !important;
}
div[data-testid="stButton"].btn-primary > button:active {
    transform: translateY(1px) scale(.98) !important;
}
/* GHOST */
div[data-testid="stButton"].btn-ghost > button {
    background: rgba(255,255,255,.04) !important;
    color: var(--text-1) !important;
    border: 1px solid rgba(255,255,255,.12) !important;
    box-shadow: none !important;
}
div[data-testid="stButton"].btn-ghost > button:hover {
    border-color: rgba(6,182,212,.5) !important;
    color: var(--cyan) !important;
    background: rgba(6,182,212,.08) !important;
    box-shadow: 0 8px 24px rgba(6,182,212,.12) !important;
}

/* ══════════════════════════════════════
   DIVIDER WAVE
══════════════════════════════════════ */
.wave-div {
    width: 100%; overflow: hidden; line-height: 0;
    margin-top: -2px;
}
.wave-div svg { display: block; width: 100%; }

/* ══════════════════════════════════════
   SECTION SHARED
══════════════════════════════════════ */
.sec-wrap {
    max-width: 1280px; margin: 0 auto; padding: 0 40px;
}
.sec-head { text-align: center; margin-bottom: 60px; }
.sec-eyebrow {
    font-family: var(--font-mono); font-size: .63rem;
    letter-spacing: .22em; text-transform: uppercase;
    color: var(--cyan); margin-bottom: 14px; display: block;
}
.sec-title {
    font-family: var(--font-grotesk);
    font-size: clamp(1.8rem, 3.5vw, 2.8rem);
    font-weight: 800; color: var(--text-1);
    letter-spacing: -.03em; line-height: 1.1;
    margin-bottom: 12px;
}
.sec-title .g {
    background: linear-gradient(135deg, var(--cyan), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sec-sub {
    font-size: .88rem; color: var(--text-2); line-height: 1.7;
}

/* ══════════════════════════════════════
   FEATURES SECTION
══════════════════════════════════════ */
.feats-sec {
    padding: 96px 0;
    background: linear-gradient(180deg, #050508 0%, #080812 50%, #050508 100%);
    position: relative;
}
.feats-sec::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 10%, rgba(99,102,241,.3) 50%, transparent 90%);
}
.feats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}
.feat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 28px 24px;
    position: relative; overflow: hidden;
    transition: all .4s cubic-bezier(.23,1,.32,1);
    cursor: default;
}
.feat-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(6,182,212,.4), transparent);
    opacity: 0; transition: opacity .4s;
}
.feat-card::after {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse 80% 80% at 50% 0%, rgba(6,182,212,.05), transparent);
    opacity: 0; transition: opacity .4s;
}
.feat-card:hover {
    border-color: rgba(6,182,212,.3);
    transform: translateY(-6px);
    box-shadow: 0 24px 60px rgba(0,0,0,.5), 0 0 40px rgba(6,182,212,.06);
}
.feat-card:hover::before { opacity: 1; }
.feat-card:hover::after  { opacity: 1; }
.feat-idx {
    font-family: var(--font-mono); font-size: .6rem;
    color: var(--text-3); letter-spacing: .1em;
    margin-bottom: 18px; display: block;
}
.feat-icon-wrap {
    width: 48px; height: 48px;
    border-radius: 14px;
    border: 1px solid rgba(6,182,212,.2);
    background: linear-gradient(135deg, rgba(6,182,212,.1), rgba(139,92,246,.1));
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 18px;
    transition: all .3s;
    font-size: 1.3rem;
}
.feat-card:hover .feat-icon-wrap {
    border-color: rgba(6,182,212,.5);
    box-shadow: 0 0 24px rgba(6,182,212,.2);
}
.feat-title {
    font-family: var(--font-grotesk); font-size: .82rem;
    font-weight: 700; letter-spacing: .04em;
    color: var(--text-1); margin-bottom: 10px;
}
.feat-desc {
    font-size: .8rem; color: var(--text-2); line-height: 1.72;
}
.feat-tag {
    display: inline-block; margin-top: 14px;
    padding: 3px 10px;
    border-radius: 50px; font-family: var(--font-mono); font-size: .58rem;
    letter-spacing: .06em;
}
.tag-cyan   { background: rgba(6,182,212,.1); border: 1px solid rgba(6,182,212,.25); color: var(--cyan); }
.tag-violet { background: rgba(139,92,246,.1); border: 1px solid rgba(139,92,246,.25); color: var(--violet); }
.tag-green  { background: rgba(16,185,129,.1); border: 1px solid rgba(16,185,129,.25); color: var(--green); }
.tag-mag    { background: rgba(236,72,153,.1); border: 1px solid rgba(236,72,153,.25); color: var(--magenta); }
.tag-amber  { background: rgba(245,158,11,.1); border: 1px solid rgba(245,158,11,.25); color: var(--amber); }
.tag-red    { background: rgba(239,68,68,.1); border: 1px solid rgba(239,68,68,.25); color: var(--red); }

/* ══════════════════════════════════════
   HOW IT WORKS SECTION
══════════════════════════════════════ */
.how-sec {
    padding: 96px 0;
    position: relative;
}
.how-sec::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 10%, rgba(139,92,246,.3) 50%, transparent 90%);
}
.steps-row {
    display: grid; grid-template-columns: 1fr 48px 1fr 48px 1fr;
    align-items: start; gap: 0;
}
.step-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 36px 28px;
    text-align: center;
    transition: all .4s cubic-bezier(.23,1,.32,1);
    position: relative; overflow: hidden;
}
.step-card::after {
    content: '';
    position: absolute; bottom: 0; left: 10%; right: 10%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    opacity: 0; transition: opacity .4s;
}
.step-card:hover {
    border-color: rgba(6,182,212,.3);
    transform: translateY(-5px);
    box-shadow: 0 20px 50px rgba(0,0,0,.5);
}
.step-card:hover::after { opacity: 1; }
.step-number {
    font-family: var(--font-grotesk);
    font-size: 3.8rem; font-weight: 800;
    line-height: 1;
    background: linear-gradient(135deg, rgba(6,182,212,.2), rgba(139,92,246,.15));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 14px; display: block;
}
.step-title {
    font-family: var(--font-grotesk); font-size: .82rem;
    font-weight: 700; color: var(--text-1);
    letter-spacing: .04em; margin-bottom: 10px;
}
.step-desc {
    font-size: .78rem; color: var(--text-2); line-height: 1.7;
}
.step-connector {
    display: flex; align-items: center; justify-content: center;
    margin-top: 56px;
}
.conn-line {
    width: 38px; height: 1px;
    background: linear-gradient(90deg, var(--cyan), var(--violet));
    position: relative;
}
.conn-line::after {
    content: '▸';
    position: absolute; right: -8px; top: 50%;
    transform: translateY(-50%);
    color: var(--violet); font-size: .5rem;
}

/* ══════════════════════════════════════
   TRUST / STATS BANNER
══════════════════════════════════════ */
.trust-sec {
    padding: 60px 0;
    background: rgba(99,102,241,.04);
    border-top: 1px solid rgba(99,102,241,.1);
    border-bottom: 1px solid rgba(99,102,241,.1);
}
.trust-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 24px; text-align: center;
}
.trust-item {}
.trust-num {
    font-family: var(--font-grotesk);
    font-size: 2.4rem; font-weight: 800;
    background: linear-gradient(135deg, var(--cyan), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    display: block; line-height: 1;
}
.trust-lbl {
    font-family: var(--font-mono); font-size: .62rem;
    color: var(--text-3); letter-spacing: .12em;
    text-transform: uppercase; margin-top: 6px;
    display: block;
}

/* ══════════════════════════════════════
   CTA SECTION
══════════════════════════════════════ */
.cta-sec {
    padding: 100px 0;
    position: relative; overflow: hidden;
}
.cta-sec::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 10%, rgba(236,72,153,.3) 50%, transparent 90%);
}
.cta-box {
    background: linear-gradient(135deg,
        rgba(6,182,212,.06) 0%,
        rgba(139,92,246,.08) 50%,
        rgba(236,72,153,.05) 100%);
    border: 1px solid rgba(139,92,246,.25);
    border-radius: var(--radius-xl);
    padding: 80px 60px;
    text-align: center; position: relative; overflow: hidden;
    box-shadow: 0 0 80px rgba(139,92,246,.08), inset 0 1px 0 rgba(255,255,255,.06);
}
.cta-box::before {
    content: '';
    position: absolute; top: -1px; left: 20%; right: 20%; height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), var(--violet), transparent);
}
.cta-box::after {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse 60% 60% at 50% 0%, rgba(139,92,246,.08), transparent);
    pointer-events: none;
}
.cta-badge {
    display: inline-block; padding: 6px 16px;
    border-radius: 50px; font-family: var(--font-mono); font-size: .62rem;
    letter-spacing: .14em; text-transform: uppercase;
    background: rgba(236,72,153,.1); border: 1px solid rgba(236,72,153,.3);
    color: var(--magenta); margin-bottom: 24px;
}
.cta-title {
    font-family: var(--font-grotesk);
    font-size: clamp(2rem, 4vw, 3.2rem);
    font-weight: 800; letter-spacing: -.03em;
    color: var(--text-1); line-height: 1.1; margin-bottom: 16px;
}
.cta-title .g {
    background: linear-gradient(135deg, var(--cyan), var(--violet), var(--magenta));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.cta-desc {
    font-size: .9rem; color: var(--text-2);
    line-height: 1.75; margin-bottom: 40px;
}
.cta-actions {
    display: flex; gap: 14px; justify-content: center; flex-wrap: wrap;
}

/* ══════════════════════════════════════
   FOOTER
══════════════════════════════════════ */
.footer-sec {
    border-top: 1px solid rgba(255,255,255,.05);
    padding: 60px 0 28px;
    background: #030306;
}
.footer-grid {
    display: grid; grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 40px; margin-bottom: 44px;
}
.footer-brand-name {
    font-family: var(--font-grotesk); font-size: .78rem;
    font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: var(--text-1);
    display: flex; align-items: center; gap: 10px; margin-bottom: 10px;
}
.footer-brand-name em {
    font-style: normal;
    background: linear-gradient(90deg, var(--cyan), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.footer-tagline {
    font-size: .78rem; color: var(--text-3); line-height: 1.7;
    max-width: 240px;
}
.footer-col-head {
    font-family: var(--font-mono); font-size: .6rem;
    letter-spacing: .2em; text-transform: uppercase;
    color: var(--cyan); margin-bottom: 16px;
}
.footer-lnk {
    display: block; font-size: .78rem;
    color: var(--text-3); text-decoration: none;
    margin-bottom: 10px; transition: color .2s;
}
.footer-lnk:hover { color: var(--cyan); }
.footer-bottom {
    border-top: 1px solid rgba(255,255,255,.05);
    padding-top: 22px;
    display: flex; align-items: center; justify-content: space-between;
    font-family: var(--font-mono); font-size: .65rem;
    color: var(--text-3); letter-spacing: .05em;
}
.footer-copy-sig {
    background: linear-gradient(90deg, var(--cyan), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ══════════════════════════════════════
   ANIMATIONS
══════════════════════════════════════ */
@keyframes slideUp {
    from { opacity:0; transform:translateY(28px); }
    to   { opacity:1; transform:translateY(0); }
}

/* ══════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════ */
@media (max-width: 1024px) {
    .hero-section  { grid-template-columns: 1fr; gap:40px; padding:60px 28px 48px; }
    .feats-grid    { grid-template-columns: repeat(2,1fr); }
    .steps-row     { grid-template-columns: 1fr; gap:14px; }
    .step-connector{ display:none; }
    .trust-grid    { grid-template-columns: repeat(2,1fr); }
    .footer-grid   { grid-template-columns: 1fr 1fr; gap:32px; }
}
@media (max-width: 768px) {
    .block-container { padding: 0 !important; }
    .navbar { padding: 0 20px; }
    .nav-inner { height: 60px; }
    .hero-section { padding: 44px 20px 32px; }
    .hero-stats { gap:20px; }
    .feats-grid { grid-template-columns: 1fr; padding: 0 20px; gap:12px; }
    .sec-wrap, .footer-inner { padding: 0 20px; }
    .cta-box { padding: 48px 20px; border-radius: 16px; }
    .footer-grid { grid-template-columns: 1fr; gap:24px; }
    .footer-bottom { flex-direction: column; gap:8px; text-align:center; }
    div[data-testid="stButton"] > button { height: 46px !important; font-size:.75rem !important; }
    .hero-actions, .cta-actions { flex-direction: column; }
    div[data-testid="stButton"].btn-primary > button,
    div[data-testid="stButton"].btn-ghost > button { width: 100% !important; }
}
@media (max-width: 480px) {
    .trust-grid { grid-template-columns: 1fr 1fr; }
    .hero-stats { flex-wrap: wrap; gap: 18px; }
    .feats-sec, .how-sec, .cta-sec { padding: 64px 0; }
}
</style>
"""


def show_landing_page():
    """
    Renders the ultra-premium landing page.
    Returns True when any CTA button is clicked.
    """
    st.markdown(LANDING_CSS, unsafe_allow_html=True)

    # Background layers
    st.markdown("""
    <div class="bg-canvas"></div>
    <div class="scan-beam"></div>
    <div class="lp">
    """, unsafe_allow_html=True)

    # ─── NAVBAR ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="navbar">
        <div class="nav-inner">
            <div class="nav-brand">
                <div class="nav-logo-ring">
                    <span class="nav-logo-icon">⬡</span>
                </div>
                <span class="nav-wordmark"><em>VULN</em>SAGE</span>
            </div>
            <div class="nav-status-chip">
                <div class="status-dot"></div>
                SYSTEM ONLINE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, nav_btn_col = st.columns([5, 1])
    with nav_btn_col:
        st.markdown('<div class="btn-primary" style="margin-top:-52px;margin-right:8px">',
                    unsafe_allow_html=True)
        nav_launch = st.button("Launch →", key="nav_launch", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ─── HERO ──────────────────────────────────────────────────────────────────
    h_left, h_right = st.columns([1.1, 0.9], gap="large")

    with h_left:
        st.markdown("""
        <div class="hero-section" style="display:block;padding:80px 40px 0;">
            <div class="hero-badge">
                <div class="hero-badge-dot"></div>
                Agentic AI Security Platform · v4.0
            </div>
            <h1 class="hero-h1">
                Detect Threats<br><span class="grad">Before Attackers</span><br>Strike
            </h1>
            <p class="hero-h1-sub">Precision vulnerability scanning, operationally ready.</p>
            <p class="hero-desc">
                VulnSage combines deep crawling, machine-learning detection, and Groq AI
                orchestration to surface XSS, SQL injection, misconfigured headers, and
                critical risks — with evidence-first output and auto-generated fixes.
            </p>
        </div>
        """, unsafe_allow_html=True)

        bc1, bc2 = st.columns([1, 1])
        with bc1:
            st.markdown('<div class="btn-primary" style="padding-left:40px">', unsafe_allow_html=True)
            hero_launch = st.button("🚀 Launch VulnSage", key="hero_launch", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with bc2:
            st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
            st.button("▶ Watch Demo", key="hero_demo", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div style="padding-left:40px;">
            <div class="hero-stats">
                <div class="stat-block">
                    <span class="stat-value">10K+</span>
                    <span class="stat-label">Sites Scanned</span>
                </div>
                <div class="stat-block">
                    <span class="stat-value">99.8%</span>
                    <span class="stat-label">Accuracy</span>
                </div>
                <div class="stat-block">
                    <span class="stat-value">847K</span>
                    <span class="stat-label">Threats in DB</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with h_right:
        st.markdown("""
        <div class="term-wrap" style="padding:80px 40px 0 0;">
            <div class="term-frame">
                <div class="term-topbar">
                    <div class="term-circs">
                        <span class="tc tc-r"></span>
                        <span class="tc tc-y"></span>
                        <span class="tc tc-g"></span>
                    </div>
                    <span class="term-title">vulnsage — live-scan.log</span>
                    <span class="ping-dot"></span>
                </div>
                <div class="term-body">
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-mute">Initializing VulnSage v4.0 engine...</span></div>
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-ok">✓  Neural model loaded — 2.4 GB weights</span></div>
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-ok">✓  Threat DB synced — 847,312 entries</span></div>
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-info">⬡  Crawling target subdomains...</span></div>
                    <div class="t-line">
                        <span class="t-prompt">›</span>
                        <span class="t-mute">Progress: <span class="t-ok">87%</span></span>
                    </div>
                    <div class="t-progress-bar"><div class="t-progress-fill"></div></div>
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-warn">⚠  XSS detected · severity: MEDIUM · conf: 94%</span></div>
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-err">✗  SQLi risk · severity: CRITICAL · conf: 99%</span></div>
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-info">⬡  Generating remediation report…<span class="t-cursor"></span></span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ─── FEATURE CARDS ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="feats-sec">
        <div class="sec-wrap">
            <div class="sec-head">
                <span class="sec-eyebrow">// Capabilities</span>
                <h2 class="sec-title">A Full <span class="g">Arsenal</span> of Detection</h2>
                <p class="sec-sub">Military-grade vulnerability analysis powered by AI and machine learning</p>
            </div>
            <div class="feats-grid">
                <div class="feat-card">
                    <span class="feat-idx">01 — XSS Detection</span>
                    <div class="feat-icon-wrap">🎯</div>
                    <div class="feat-title">Cross-Site Scripting</div>
                    <p class="feat-desc">Identify reflected, stored, and DOM-based XSS with deep pattern recognition and contextual AI analysis.</p>
                    <span class="feat-tag tag-cyan">AI-Powered</span>
                </div>
                <div class="feat-card">
                    <span class="feat-idx">02 — SQL Injection</span>
                    <div class="feat-icon-wrap">💉</div>
                    <div class="feat-title">Injection Attacks</div>
                    <p class="feat-desc">Advanced detection of SQL, NoSQL, and command injection before they compromise your data layer.</p>
                    <span class="feat-tag tag-red">Critical Risk</span>
                </div>
                <div class="feat-card">
                    <span class="feat-idx">03 — Headers</span>
                    <div class="feat-icon-wrap">🛡️</div>
                    <div class="feat-title">Header Analysis</div>
                    <p class="feat-desc">Audit security headers — CSP, X-Frame-Options, HSTS, CORS, and content-type policies.</p>
                    <span class="feat-tag tag-violet">Deep Audit</span>
                </div>
                <div class="feat-card">
                    <span class="feat-idx">04 — Real-time</span>
                    <div class="feat-icon-wrap">⚡</div>
                    <div class="feat-title">Live Scanning</div>
                    <p class="feat-desc">Instant multi-subdomain assessment with live status updates, progress tracking, and granular logs.</p>
                    <span class="feat-tag tag-amber">< 60 Seconds</span>
                </div>
                <div class="feat-card">
                    <span class="feat-idx">05 — Intelligence</span>
                    <div class="feat-icon-wrap">🤖</div>
                    <div class="feat-title">Agentic AI Engine</div>
                    <p class="feat-desc">Groq LLM integration for intelligent threat assessment, risk prioritization, and automated remediation plans.</p>
                    <span class="feat-tag tag-green">Groq Powered</span>
                </div>
                <div class="feat-card">
                    <span class="feat-idx">06 — Reporting</span>
                    <div class="feat-icon-wrap">📋</div>
                    <div class="feat-title">Detailed Reports</div>
                    <p class="feat-desc">Comprehensive security reports with CVSS scores, risk levels, evidence chains, and step-by-step fixes.</p>
                    <span class="feat-tag tag-mag">Auto-Generated</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── HOW IT WORKS ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="how-sec">
        <div class="sec-wrap">
            <div class="sec-head">
                <span class="sec-eyebrow">// Process</span>
                <h2 class="sec-title">How <span class="g">It Works</span></h2>
                <p class="sec-sub">Three precise steps to comprehensive security intelligence</p>
            </div>
            <div class="steps-row">
                <div class="step-card">
                    <span class="step-number">01</span>
                    <div class="step-title">Submit Target URL</div>
                    <p class="step-desc">Enter any URL or domain — our AI engine automatically identifies and maps the target attack surface.</p>
                </div>
                <div class="step-connector"><div class="conn-line"></div></div>
                <div class="step-card">
                    <span class="step-number">02</span>
                    <div class="step-title">AI Analysis</div>
                    <p class="step-desc">Multi-layer security checks, ML-based threat modelling, and agentic deep inspection run in parallel.</p>
                </div>
                <div class="step-connector"><div class="conn-line"></div></div>
                <div class="step-card">
                    <span class="step-number">03</span>
                    <div class="step-title">Get Report</div>
                    <p class="step-desc">Receive a detailed vulnerability report with CVSS scores, risk assessment, and auto-generated code fixes.</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── TRUST STATS ───────────────────────────────────────────────────────────
    st.markdown("""
    <div class="trust-sec">
        <div class="sec-wrap">
            <div class="trust-grid">
                <div class="trust-item">
                    <span class="trust-num">10K+</span>
                    <span class="trust-lbl">Sites Scanned</span>
                </div>
                <div class="trust-item">
                    <span class="trust-num">99.8%</span>
                    <span class="trust-lbl">Detection Accuracy</span>
                </div>
                <div class="trust-item">
                    <span class="trust-num">847K</span>
                    <span class="trust-lbl">Threat Signatures</span>
                </div>
                <div class="trust-item">
                    <span class="trust-num">&lt; 60s</span>
                    <span class="trust-lbl">Avg. Scan Time</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── CTA ───────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="cta-sec">
        <div class="sec-wrap">
            <div class="cta-box">
                <span class="cta-badge">✦ Get Started — Free</span>
                <h2 class="cta-title">
                    Ready to Secure<br><span class="g">Your Applications?</span>
                </h2>
                <p class="cta-desc">
                    Start scanning now and shield your systems from critical vulnerabilities.<br>
                    No setup required. Results in under a minute. No credit card needed.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, cta_col, _ = st.columns([1, 2, 1])
    with cta_col:
        st.markdown('<div class="btn-primary" style="margin-top:-42px">', unsafe_allow_html=True)
        cta_launch = st.button("🚀 Start VulnSage Scan — Free", key="cta_launch", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ─── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="footer-sec">
        <div class="sec-wrap footer-inner">
            <div class="footer-grid">
                <div>
                    <div class="footer-brand-name">⬡ &nbsp;<em>VULN</em>SAGE</div>
                    <p class="footer-tagline">Agentic web security scanning with AI-powered remediation intelligence. Built for defenders.</p>
                </div>
                <div>
                    <div class="footer-col-head">Product</div>
                    <a href="#" class="footer-lnk">Features</a>
                    <a href="#" class="footer-lnk">How It Works</a>
                    <a href="#" class="footer-lnk">Dashboard</a>
                    <a href="#" class="footer-lnk">Changelog</a>
                </div>
                <div>
                    <div class="footer-col-head">Resources</div>
                    <a href="#" class="footer-lnk">Documentation</a>
                    <a href="#" class="footer-lnk">API Reference</a>
                    <a href="#" class="footer-lnk">Security Guide</a>
                    <a href="#" class="footer-lnk">Blog</a>
                </div>
                <div>
                    <div class="footer-col-head">Company</div>
                    <a href="#" class="footer-lnk">About</a>
                    <a href="#" class="footer-lnk">Privacy Policy</a>
                    <a href="#" class="footer-lnk">Terms of Use</a>
                    <a href="#" class="footer-lnk">Contact</a>
                </div>
            </div>
            <div class="footer-bottom">
                <span>© 2026 VulnSage. All rights reserved.</span>
                <span class="footer-copy-sig">Built for defenders. Powered by AI.</span>
            </div>
        </div>
    </div>
    </div><!-- /lp -->
    """, unsafe_allow_html=True)

    return nav_launch or hero_launch or cta_launch
