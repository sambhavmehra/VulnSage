"""
landing_page.py
Ultra-premium redesign — Deep Space Neon Cybersecurity Theme.
Electric cyan + violet + magenta palette on near-black background.
Enhanced with advanced animations, particle effects, and visual depth.
Returns True when any primary CTA is clicked.
"""
import streamlit as st

LANDING_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@300;400;500&family=Cabinet+Grotesk:wght@400;500;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ══ RESET & FORCE DARK ══ */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"], .stApp, .main,
[data-testid="stMain"], [data-testid="stHeader"] {
    background-color: #02020a !important;
    background: #02020a !important;
    color: #e2e8f0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
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
::-webkit-scrollbar-track { background: #02020a; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, rgba(6,182,212,.6), rgba(139,92,246,.6));
    border-radius: 2px;
}

/* ══ CSS VARIABLES ══ */
:root {
    --cyan:        #00d4ff;
    --cyan-dim:    #06b6d4;
    --cyan-glow:   rgba(0,212,255,.5);
    --violet:      #a855f7;
    --violet-dim:  #8b5cf6;
    --violet-glow: rgba(168,85,247,.5);
    --magenta:     #f0abfc;
    --mag-bright:  #e879f9;
    --mag-glow:    rgba(232,121,249,.4);
    --green:       #34d399;
    --amber:       #fbbf24;
    --red:         #f87171;
    --bg:          #02020a;
    --bg-1:        #070710;
    --bg-2:        #0c0c1a;
    --bg-card:     rgba(255,255,255,.03);
    --bg-card-hover: rgba(255,255,255,.055);
    --border:      rgba(255,255,255,.07);
    --border-c:    rgba(0,212,255,.2);
    --text-1:      #f8fafc;
    --text-2:      #94a3b8;
    --text-3:      #475569;
    --font-display: 'Syne', sans-serif;
    --font-sans:   'Space Grotesk', sans-serif;
    --font-mono:   'JetBrains Mono', monospace;
    --radius:      12px;
    --radius-lg:   20px;
    --radius-xl:   28px;
}

/* ══ PARTICLE CANVAS ══ */
#particle-canvas {
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
}

/* ══ ANIMATED BACKGROUND ══ */
.bg-canvas {
    position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden;
}
.bg-canvas::before {
    content: '';
    position: absolute; inset: 0;
    background:
        radial-gradient(ellipse 90% 70% at 5% 5%, rgba(168,85,247,.14) 0%, transparent 55%),
        radial-gradient(ellipse 70% 60% at 95% 85%, rgba(0,212,255,.12) 0%, transparent 50%),
        radial-gradient(ellipse 60% 50% at 50% 50%, rgba(232,121,249,.05) 0%, transparent 45%),
        radial-gradient(ellipse 40% 40% at 80% 20%, rgba(52,211,153,.05) 0%, transparent 40%);
    animation: bgPulse 16s ease-in-out infinite alternate;
}
@keyframes bgPulse {
    0%   { opacity: .6; transform: scale(1) rotate(0deg); }
    50%  { opacity: .9; transform: scale(1.03) rotate(.5deg); }
    100% { opacity: 1;  transform: scale(1.06) rotate(1deg); }
}
.bg-canvas::after {
    content: '';
    position: fixed; inset: 0;
    background-image:
        radial-gradient(circle, rgba(0,212,255,.15) 1px, transparent 1px),
        radial-gradient(circle, rgba(168,85,247,.08) 1px, transparent 1px);
    background-size: 48px 48px, 96px 96px;
    background-position: 0 0, 24px 24px;
    mask-image: radial-gradient(ellipse 100% 100% at 50% 50%, black 20%, transparent 80%);
    animation: gridDrift 24s linear infinite;
}
@keyframes gridDrift {
    from { background-position: 0 0, 24px 24px; }
    to   { background-position: 48px 48px, 72px 72px; }
}

/* Horizontal scan lines — multiple */
.scan-beam {
    position: fixed; left: 0; right: 0; height: 2px; z-index: 0; pointer-events: none;
    background: linear-gradient(90deg, transparent 0%, rgba(0,212,255,.7) 30%, rgba(168,85,247,.7) 60%, rgba(232,121,249,.4) 80%, transparent 100%);
    filter: blur(1px);
    animation: scanBeam 10s ease-in-out infinite;
    top: 0;
}
.scan-beam-2 {
    position: fixed; left: 0; right: 0; height: 1px; z-index: 0; pointer-events: none;
    background: linear-gradient(90deg, transparent 0%, rgba(52,211,153,.5) 50%, transparent 100%);
    animation: scanBeam 10s 5s ease-in-out infinite;
    top: 0;
}
@keyframes scanBeam {
    0%   { top: -2px; opacity: 0; }
    3%   { opacity: 1; }
    97%  { opacity: .4; }
    100% { top: 102%; opacity: 0; }
}

/* ── Floating hex shapes ── */
.hex-float {
    position: fixed; pointer-events: none; z-index: 0;
    font-size: 1.5rem; opacity: 0;
    animation: hexFloat linear infinite;
    color: var(--violet);
    filter: blur(0px);
}
.hex-float:nth-child(1) { left: 5%;  animation-duration: 22s; animation-delay: 0s;   font-size:1.2rem; color: var(--cyan-dim); }
.hex-float:nth-child(2) { left: 15%; animation-duration: 28s; animation-delay: 3s;   font-size:0.8rem; color: var(--violet); }
.hex-float:nth-child(3) { left: 30%; animation-duration: 19s; animation-delay: 7s;   font-size:1.8rem; color: var(--mag-bright); opacity-target:.04; }
.hex-float:nth-child(4) { left: 55%; animation-duration: 25s; animation-delay: 2s;   font-size:1rem; }
.hex-float:nth-child(5) { left: 70%; animation-duration: 20s; animation-delay: 11s;  font-size:2.2rem; color: var(--cyan-dim); }
.hex-float:nth-child(6) { left: 85%; animation-duration: 32s; animation-delay: 5s;   font-size:0.7rem; color: var(--green); }
.hex-float:nth-child(7) { left: 92%; animation-duration: 18s; animation-delay: 14s;  font-size:1.4rem; }
@keyframes hexFloat {
    0%   { top: 110%; opacity: 0;     transform: rotate(0deg)   translateX(0px); }
    5%   { opacity: .08; }
    95%  { opacity: .05; }
    100% { top: -10%;  opacity: 0;    transform: rotate(360deg) translateX(30px); }
}

/* ══ WRAPPER ══ */
.lp { position: relative; z-index: 1; }

/* ══════════════════════════════════════
   NAVBAR — frosted glass with glow edge
══════════════════════════════════════ */
.navbar {
    position: sticky; top: 0; z-index: 200;
    background: rgba(2,2,10,.75);
    backdrop-filter: blur(40px) saturate(2) brightness(1.1);
    border-bottom: 1px solid rgba(0,212,255,.1);
    padding: 0 48px;
    box-shadow: 0 1px 0 rgba(0,212,255,.08), 0 4px 32px rgba(0,0,0,.4);
}
.nav-inner {
    max-width: 1320px; margin: 0 auto;
    height: 70px;
    display: flex; align-items: center; justify-content: space-between;
}
.nav-brand { display: flex; align-items: center; gap: 14px; }
.nav-logo-ring, .brand-logo-ring {
    position: relative; width: 40px; height: 40px;
    display: flex; align-items: center; justify-content: center;
}
.nav-logo-bg, .brand-logo-bg {
    position: absolute; inset: 0; border-radius: 11px;
    background: linear-gradient(135deg, rgba(0,212,255,.15), rgba(168,85,247,.15));
    border: 1px solid rgba(0,212,255,.25);
}
.nav-logo-spin, .brand-logo-spin {
    position: absolute; inset: -3px; border-radius: 13px;
    background: conic-gradient(from 0deg, transparent 0%, var(--cyan-dim) 30%, transparent 60%);
    animation: spinGlow 4s linear infinite;
    mask: radial-gradient(farthest-side, transparent calc(100% - 2px), white calc(100% - 2px));
    opacity: .6;
}
@keyframes spinGlow { to { transform: rotate(360deg); } }
.nav-logo-icon, .brand-logo-icon {
    font-size: 1.1rem; position: relative; z-index: 1;
    background: linear-gradient(135deg, var(--cyan), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 8px var(--cyan-glow));
}
.nav-wordmark, .brand-wordmark {
    font-family: var(--font-display);
    font-size: 1.7rem;
    letter-spacing: .18em; text-transform: uppercase;
    color: var(--text-1);
    
}
.nav-wordmark em, .brand-wordmark em {
    font-style: normal;
    background: linear-gradient(90deg, var(--cyan), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 12px rgba(0,212,255,.4));
}
.nav-brand-stack {
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.nav-brand-sub {
    font-family: var(--font-mono);
    font-size: .58rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--text-3: white;);
}
.nav-center-links {
    display: flex; align-items: center; gap: 32px;
}
.nav-link {
    font-family: var(--font-mono); font-size: .65rem;
    color: var(--text-3); letter-spacing: .1em; text-decoration: none;
    text-transform: uppercase; transition: color .2s;
    position: relative;
}
.nav-link::after {
    content: '';
    position: absolute; bottom: -4px; left: 0; right: 0; height: 1px;
    background: var(--cyan); transform: scaleX(0); transition: transform .3s;
}
.nav-link:hover { color: var(--cyan); }
.nav-link:hover::after { transform: scaleX(1); }
.nav-status-chip {
    display: flex; align-items: center; gap: 8px;
    padding: 6px 16px;
    background: rgba(52,211,153,.06);
    border: 1px solid rgba(52,211,153,.2);
    border-radius: 50px;
    font-family: var(--font-mono); font-size: .6rem;
    color: var(--green); letter-spacing: .12em;
    box-shadow: 0 0 20px rgba(52,211,153,.05);
}
.status-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 10px var(--green), 0 0 20px rgba(52,211,153,.4);
    animation: statusPulse 2s ease infinite;
}
@keyframes statusPulse {
    0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 10px var(--green), 0 0 20px rgba(52,211,153,.4); }
    50%       { opacity: .4; transform: scale(.65); box-shadow: 0 0 4px var(--green); }
}

/* ══════════════════════════════════════
   HERO
══════════════════════════════════════ */
.hero-outer {
    position: relative; overflow: hidden;
}
/* Diagonal accent line */
.hero-outer::before {
    content: '';
    position: absolute; top: -100px; right: -100px;
    width: 600px; height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(168,85,247,.07) 0%, transparent 70%);
    pointer-events: none;
}
.hero-section {
    max-width: 1320px; margin: 0 auto;
    padding: 88px 48px 64px;
    display: grid; grid-template-columns: 1.15fr .85fr;
    gap: 72px; align-items: center;
    position: relative;
}

/* Eyebrow badge */
.hero-badge {
    display: inline-flex; align-items: center; gap: 12px;
    padding: 8px 20px;
    background: linear-gradient(90deg, rgba(0,212,255,.08), rgba(168,85,247,.08));
    border: 1px solid rgba(0,212,255,.25);
    border-radius: 50px;
    font-family: var(--font-mono); font-size: .63rem;
    letter-spacing: .16em; color: var(--cyan);
    margin-bottom: 30px;
    opacity: 0; animation: slideUp .7s .1s ease forwards;
    position: relative; overflow: hidden;
}
.hero-badge::before {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,.12), transparent);
    transform: translateX(-100%);
    animation: shimmer 3s 1.5s ease infinite;
}
@keyframes shimmer {
    to { transform: translateX(100%); }
}
.hero-badge-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 12px var(--cyan), 0 0 24px rgba(0,212,255,.4);
    animation: statusPulse 1.8s ease infinite;
}

/* Main heading */
.hero-h1 {
    font-family: var(--font-display);
    font-size: clamp(2.8rem, 5vw, 5.2rem);
    font-weight: 800; line-height: 1.02;
    color: var(--text-1);
    letter-spacing: -.04em;
    margin-bottom: 10px;
    opacity: 0; animation: slideUp .7s .2s ease forwards;
}
.hero-h1 .grad {
    background: linear-gradient(135deg, var(--cyan) 0%, var(--violet) 45%, var(--mag-bright) 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 20px rgba(0,212,255,.25));
    position: relative; display: inline-block;
}
/* Underline glow on gradient text */
.hero-h1 .grad::after {
    content: '';
    position: absolute; bottom: -4px; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--cyan), var(--violet), var(--mag-bright));
    opacity: .6; border-radius: 1px;
    animation: lineGlow 3s ease-in-out infinite alternate;
}
@keyframes lineGlow {
    from { opacity: .4; filter: blur(0px); }
    to   { opacity: .9; filter: blur(1px); }
}
.hero-h1-sub {
    font-family: var(--font-display);
    font-size: clamp(1.1rem, 2vw, 1.65rem);
    font-weight: 400; color: var(--text-2);
    letter-spacing: -.01em; margin-bottom: 26px;
    opacity: 0; animation: slideUp .7s .3s ease forwards;
}
.hero-desc {
    font-size: .9rem; color: var(--text-2);
    line-height: 1.85; margin-bottom: 38px;
    opacity: 0; animation: slideUp .7s .4s ease forwards;
    max-width: 540px;
    border-left: 2px solid rgba(0,212,255,.2);
    padding-left: 16px;
}
.hero-actions {
    display: flex; gap: 14px; flex-wrap: wrap;
    opacity: 0; animation: slideUp .7s .5s ease forwards;
}

/* Stats row */
.hero-stats {
    display: flex; gap: 36px; margin-top: 48px;
    opacity: 0; animation: slideUp .7s .65s ease forwards;
    border-top: 1px solid rgba(0,212,255,.1);
    padding-top: 32px;
    position: relative;
}
.hero-stats::before {
    content: '';
    position: absolute; top: -1px; left: 0; width: 80px; height: 1px;
    background: linear-gradient(90deg, var(--cyan), transparent);
}
.stat-block { position: relative; }
.stat-value {
    font-family: var(--font-display);
    font-size: 2.2rem; font-weight: 800;
    background: linear-gradient(135deg, var(--cyan), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1; display: block;
    filter: drop-shadow(0 0 8px rgba(0,212,255,.2));
}
.stat-label {
    font-family: var(--font-mono); font-size: .6rem;
    color: var(--text-3); letter-spacing: .12em;
    text-transform: uppercase; margin-top: 5px;
    display: block;
}

/* ══ HERO RIGHT: Live Terminal ══ */
.term-wrap {
    opacity: 0; animation: slideUp .7s .45s ease forwards;
    position: relative;
}
/* Glow behind terminal */
.term-wrap::before {
    content: '';
    position: absolute; inset: -40px;
    background: radial-gradient(ellipse 80% 80% at 50% 50%, rgba(168,85,247,.08), transparent 70%);
    pointer-events: none; z-index: -1;
    animation: termGlowPulse 4s ease-in-out infinite alternate;
}
@keyframes termGlowPulse {
    from { opacity: .5; }
    to   { opacity: 1; }
}
.term-frame {
    background: rgba(7,7,16,.95);
    border: 1px solid rgba(0,212,255,.18);
    border-radius: var(--radius-xl);
    overflow: hidden;
    box-shadow:
        0 0 0 1px rgba(168,85,247,.06),
        0 40px 100px rgba(0,0,0,.7),
        0 0 80px rgba(168,85,247,.07),
        inset 0 1px 0 rgba(0,212,255,.1);
    position: relative;
}
/* Top gradient line */
.term-frame::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent 5%, var(--cyan-dim) 35%, var(--violet) 65%, transparent 95%);
    box-shadow: 0 0 20px rgba(0,212,255,.5);
    z-index: 2;
}
/* Corner accents */
.term-frame::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent 5%, rgba(168,85,247,.4) 50%, transparent 95%);
    z-index: 2;
}
.term-topbar {
    background: rgba(255,255,255,.025);
    border-bottom: 1px solid rgba(255,255,255,.06);
    padding: 15px 22px;
    display: flex; align-items: center; gap: 14px;
}
.term-circs { display: flex; gap: 8px; }
.tc { width: 13px; height: 13px; border-radius: 50%; position: relative; }
.tc::after {
    content: ''; position: absolute; inset: 0; border-radius: 50%;
    animation: tcGlow 3s ease infinite;
}
.tc-r { background: #ff5f57; }
.tc-r::after { box-shadow: 0 0 6px rgba(255,95,87,.6); }
.tc-y { background: #febc2e; }
.tc-y::after { box-shadow: 0 0 6px rgba(254,188,46,.6); animation-delay: 1s; }
.tc-g { background: #28c840; }
.tc-g::after { box-shadow: 0 0 6px rgba(40,200,64,.6); animation-delay: 2s; }
@keyframes tcGlow {
    0%, 100% { opacity: 1; }
    50%       { opacity: .4; }
}
.term-title {
    flex: 1; text-align: center;
    font-family: var(--font-mono); font-size: .66rem;
    color: var(--text-3); letter-spacing: .1em;
}
.ping-dot {
    width: 9px; height: 9px; border-radius: 50%;
    background: var(--green); box-shadow: 0 0 10px var(--green), 0 0 20px rgba(52,211,153,.5);
    animation: statusPulse 2.5s ease infinite;
}
.term-body { padding: 24px 24px 28px; }
.t-line {
    display: flex; align-items: flex-start; gap: 10px;
    margin-bottom: 11px;
    font-family: var(--font-mono); font-size: .76rem;
    opacity: 0; animation: termLine .4s ease forwards;
    position: relative;
}
/* Line highlight on last active */
.t-line:last-child { background: rgba(0,212,255,.02); border-radius: 4px; }
.t-line:nth-child(1) { animation-delay: 1.0s; }
.t-line:nth-child(2) { animation-delay: 1.8s; }
.t-line:nth-child(3) { animation-delay: 2.6s; }
.t-line:nth-child(4) { animation-delay: 3.4s; }
.t-line:nth-child(5) { animation-delay: 4.2s; }
.t-line:nth-child(6) { animation-delay: 5.0s; }
.t-line:nth-child(7) { animation-delay: 5.8s; }
.t-line:nth-child(8) { animation-delay: 6.6s; }
@keyframes termLine {
    from { opacity:0; transform: translateX(-8px); }
    to   { opacity:1; transform: translateX(0); }
}
.t-prompt { color: var(--cyan-dim); flex-shrink: 0; font-weight: 500; }
.t-mute   { color: var(--text-3); }
.t-ok     { color: var(--green); }
.t-warn   { color: var(--amber); }
.t-err    { color: var(--red); }
.t-info   { color: var(--violet); }
.t-cursor {
    display: inline-block; width: 8px; height: 15px;
    background: var(--cyan); margin-left: 4px;
    animation: blink 1s step-end infinite;
    vertical-align: text-bottom; border-radius: 1px;
    box-shadow: 0 0 8px var(--cyan);
}
@keyframes blink { 50% { opacity: 0; } }

/* Progress bar inside terminal */
.t-progress-bar {
    height: 4px; background: rgba(255,255,255,.05);
    border-radius: 3px; margin: 9px 0 5px; overflow: hidden;
    position: relative;
}
.t-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--cyan-dim), var(--violet), var(--mag-bright));
    border-radius: 3px;
    box-shadow: 0 0 12px var(--cyan-glow), 0 0 24px rgba(168,85,247,.3);
    animation: progFill 4.5s 1.5s ease forwards;
    width: 0%;
    position: relative;
}
.t-progress-fill::after {
    content: '';
    position: absolute; right: 0; top: -3px; bottom: -3px; width: 20px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.8));
    border-radius: 2px;
    filter: blur(3px);
}
@keyframes progFill { to { width: 87%; } }

/* ── Terminal severity badges ── */
.t-badge {
    display: inline-flex; align-items: center;
    padding: 1px 7px; border-radius: 3px;
    font-size: .6rem; letter-spacing: .05em;
    font-weight: 600; margin-left: 4px;
}
.t-badge-crit { background: rgba(248,113,113,.15); color: var(--red); border: 1px solid rgba(248,113,113,.3); }
.t-badge-med  { background: rgba(251,191,36,.1);   color: var(--amber); border: 1px solid rgba(251,191,36,.25); }
.t-badge-low  { background: rgba(52,211,153,.1);   color: var(--green); border: 1px solid rgba(52,211,153,.25); }

/* ══════════════════════════════════════
   SHARED BUTTON STYLES  (via Streamlit)
══════════════════════════════════════ */
div[data-testid="stButton"] > button {
    height: 52px !important;
    border-radius: var(--radius) !important;
    font-family: var(--font-display) !important;
    font-size: .8rem !important;
    font-weight: 700 !important;
    letter-spacing: .06em !important;
    transition: all .35s cubic-bezier(.23,1,.32,1) !important;
    white-space: nowrap !important;
    text-transform: uppercase !important;
    position: relative !important;
    overflow: hidden !important;
}
/* PRIMARY — gradient with animated shine */
div[data-testid="stButton"].btn-primary > button {
    background: linear-gradient(135deg, var(--cyan-dim) 0%, var(--violet-dim) 60%, var(--mag-bright) 100%) !important;
    color: #fff !important;
    border: none !important;
    box-shadow:
        0 8px 32px rgba(168,85,247,.4),
        0 0 0 1px rgba(255,255,255,.12) inset,
        0 0 40px rgba(0,212,255,.15) !important;
}
div[data-testid="stButton"].btn-primary > button::before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important; left: -100% !important;
    width: 60% !important; height: 100% !important;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,.25), transparent) !important;
    animation: btnShine 3s ease infinite !important;
    pointer-events: none !important;
}
@keyframes btnShine {
    0%   { left: -100%; }
    40%  { left: 150%; }
    100% { left: 150%; }
}
div[data-testid="stButton"].btn-primary > button:hover {
    transform: translateY(-4px) scale(1.03) !important;
    box-shadow:
        0 20px 56px rgba(168,85,247,.6),
        0 0 40px rgba(0,212,255,.35),
        0 0 80px rgba(232,121,249,.15) !important;
}
div[data-testid="stButton"].btn-primary > button:active {
    transform: translateY(1px) scale(.98) !important;
}
/* GHOST */
div[data-testid="stButton"].btn-ghost > button {
    background: rgba(255,255,255,.03) !important;
    color: var(--text-1) !important;
    border: 1px solid rgba(255,255,255,.1) !important;
    box-shadow: none !important;
    text-transform: uppercase !important;
}
div[data-testid="stButton"].btn-ghost > button:hover {
    border-color: rgba(0,212,255,.45) !important;
    color: var(--cyan) !important;
    background: rgba(0,212,255,.06) !important;
    box-shadow: 0 8px 28px rgba(0,212,255,.1), 0 0 0 1px rgba(0,212,255,.15) inset !important;
    transform: translateY(-2px) !important;
}

/* ══════════════════════════════════════
   SECTION SHARED
══════════════════════════════════════ */
.sec-wrap {
    max-width: 1320px; margin: 0 auto; padding: 0 48px;
}
.sec-head { text-align: center; margin-bottom: 64px; }
.sec-eyebrow {
    font-family: var(--font-mono); font-size: .63rem;
    letter-spacing: .28em; text-transform: uppercase;
    color: var(--cyan-dim); margin-bottom: 16px; display: block;
    position: relative; display: inline-block;
}
.sec-eyebrow::before, .sec-eyebrow::after {
    content: '──';
    margin: 0 10px;
    opacity: .3;
}
.sec-title {
    font-family: var(--font-display);
    font-size: clamp(2rem, 3.8vw, 3rem);
    font-weight: 800; color: var(--text-1);
    letter-spacing: -.04em; line-height: 1.08;
    margin-bottom: 14px;
}
.sec-title .g {
    background: linear-gradient(135deg, var(--cyan-dim), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sec-sub {
    font-size: .9rem; color: var(--text-2); line-height: 1.7;
}

/* ══════════════════════════════════════
   FEATURES SECTION
══════════════════════════════════════ */
.feats-sec {
    padding: 104px 0;
    background: linear-gradient(180deg, #02020a 0%, #06060f 40%, #0a0a18 60%, #02020a 100%);
    position: relative;
}
.feats-sec::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 5%, rgba(0,212,255,.25) 30%, rgba(168,85,247,.35) 70%, transparent 95%);
}
.feats-sec::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 5%, rgba(168,85,247,.2) 50%, transparent 95%);
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
    padding: 30px 26px;
    position: relative; overflow: hidden;
    transition: all .45s cubic-bezier(.23,1,.32,1);
    cursor: default;
}
/* Animated corner accent */
.feat-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,.5), transparent);
    opacity: 0; transition: opacity .4s;
    box-shadow: 0 0 20px rgba(0,212,255,.3);
}
.feat-card::after {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse 70% 70% at 50% -20%, rgba(0,212,255,.04), transparent);
    opacity: 0; transition: opacity .4s;
}
/* Left border accent that fills on hover */
.feat-card .card-left-border {
    position: absolute; left: 0; top: 20%; bottom: 20%; width: 2px;
    background: linear-gradient(180deg, transparent, var(--cyan-dim), transparent);
    opacity: 0; transition: opacity .4s, top .4s, bottom .4s;
    border-radius: 1px;
}
.feat-card:hover {
    border-color: rgba(0,212,255,.25);
    transform: translateY(-8px) scale(1.01);
    box-shadow: 0 28px 70px rgba(0,0,0,.55), 0 0 50px rgba(0,212,255,.05);
    background: var(--bg-card-hover);
}
.feat-card:hover::before { opacity: 1; }
.feat-card:hover::after  { opacity: 1; }
.feat-card:hover .card-left-border { opacity: 1; top: 10%; bottom: 10%; }
.feat-idx {
    font-family: var(--font-mono); font-size: .6rem;
    color: var(--text-3); letter-spacing: .12em;
    margin-bottom: 18px; display: block;
}
.feat-icon-wrap {
    width: 52px; height: 52px;
    border-radius: 15px;
    border: 1px solid rgba(0,212,255,.18);
    background: linear-gradient(135deg, rgba(0,212,255,.08), rgba(168,85,247,.08));
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 18px;
    transition: all .4s;
    font-size: 1.4rem;
    position: relative;
}
.feat-icon-wrap::after {
    content: '';
    position: absolute; inset: 0; border-radius: 15px;
    background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.08), transparent);
}
.feat-card:hover .feat-icon-wrap {
    border-color: rgba(0,212,255,.45);
    box-shadow: 0 0 30px rgba(0,212,255,.18), 0 0 60px rgba(168,85,247,.08);
    transform: scale(1.05);
}
.feat-title {
    font-family: var(--font-display); font-size: .85rem;
    font-weight: 700; letter-spacing: .03em;
    color: var(--text-1); margin-bottom: 10px;
}
.feat-desc {
    font-size: .8rem; color: var(--text-2); line-height: 1.75;
}
.feat-tag {
    display: inline-block; margin-top: 16px;
    padding: 4px 12px;
    border-radius: 50px; font-family: var(--font-mono); font-size: .58rem;
    letter-spacing: .08em; font-weight: 500;
}
.tag-cyan   { background: rgba(0,212,255,.08);   border: 1px solid rgba(0,212,255,.22);  color: var(--cyan); }
.tag-violet { background: rgba(168,85,247,.08);  border: 1px solid rgba(168,85,247,.22); color: var(--violet); }
.tag-green  { background: rgba(52,211,153,.08);  border: 1px solid rgba(52,211,153,.22); color: var(--green); }
.tag-mag    { background: rgba(232,121,249,.08); border: 1px solid rgba(232,121,249,.22);color: var(--mag-bright); }
.tag-amber  { background: rgba(251,191,36,.08);  border: 1px solid rgba(251,191,36,.22); color: var(--amber); }
.tag-red    { background: rgba(248,113,113,.08); border: 1px solid rgba(248,113,113,.22);color: var(--red); }

/* ══════════════════════════════════════
   THREAT TICKER / LIVE FEED
══════════════════════════════════════ */
.ticker-sec {
    padding: 24px 0;
    background: rgba(0,212,255,.025);
    border-top: 1px solid rgba(0,212,255,.08);
    border-bottom: 1px solid rgba(0,212,255,.08);
    overflow: hidden; position: relative;
}
.ticker-inner {
    display: flex; align-items: center; gap: 0;
    white-space: nowrap;
    animation: tickerScroll 40s linear infinite;
    width: max-content;
}
@keyframes tickerScroll {
    from { transform: translateX(0); }
    to   { transform: translateX(-50%); }
}
.ticker-item {
    display: inline-flex; align-items: center; gap: 10px;
    padding: 0 32px;
    font-family: var(--font-mono); font-size: .65rem;
    letter-spacing: .08em; color: var(--text-3);
    border-right: 1px solid rgba(255,255,255,.06);
}
.ticker-item .t-ok  { color: var(--green); }
.ticker-item .t-err { color: var(--red); }
.ticker-item .t-warn{ color: var(--amber); }
.ticker-sep { color: var(--cyan-dim); opacity: .4; }

/* ══════════════════════════════════════
   HOW IT WORKS SECTION
══════════════════════════════════════ */
.how-sec {
    padding: 104px 0;
    position: relative;
}
.how-sec::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 5%, rgba(168,85,247,.25) 50%, transparent 95%);
}
.steps-row {
    display: grid; grid-template-columns: 1fr 56px 1fr 56px 1fr;
    align-items: start; gap: 0;
}
.step-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 40px 30px;
    text-align: center;
    transition: all .45s cubic-bezier(.23,1,.32,1);
    position: relative; overflow: hidden;
}
.step-card::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse 60% 50% at 50% 110%, rgba(168,85,247,.08), transparent);
    opacity: 0; transition: opacity .4s;
}
.step-card::after {
    content: '';
    position: absolute; bottom: 0; left: 10%; right: 10%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--cyan-dim), var(--violet), transparent);
    opacity: 0; transition: opacity .4s;
    box-shadow: 0 0 15px rgba(0,212,255,.3);
}
.step-card:hover {
    border-color: rgba(168,85,247,.3);
    transform: translateY(-8px);
    box-shadow: 0 24px 60px rgba(0,0,0,.55), 0 0 40px rgba(168,85,247,.06);
    background: var(--bg-card-hover);
}
.step-card:hover::before { opacity: 1; }
.step-card:hover::after  { opacity: 1; }
.step-number {
    font-family: var(--font-display);
    font-size: 4.5rem; font-weight: 900;
    line-height: 1;
    background: linear-gradient(135deg, rgba(0,212,255,.18), rgba(168,85,247,.12));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 16px; display: block;
    transition: all .4s;
}
.step-card:hover .step-number {
    background: linear-gradient(135deg, rgba(0,212,255,.5), rgba(168,85,247,.4));
    -webkit-background-clip: text; background-clip: text;
    filter: drop-shadow(0 0 20px rgba(0,212,255,.2));
}
.step-icon {
    font-size: 2rem; margin-bottom: 12px; display: block;
    transition: transform .3s;
}
.step-card:hover .step-icon { transform: scale(1.15) rotate(-5deg); }
.step-title {
    font-family: var(--font-display); font-size: .85rem;
    font-weight: 700; color: var(--text-1);
    letter-spacing: .04em; margin-bottom: 12px;
}
.step-desc {
    font-size: .8rem; color: var(--text-2); line-height: 1.75;
}
.step-connector {
    display: flex; align-items: center; justify-content: center;
    margin-top: 64px;
}
.conn-arrow {
    width: 44px; height: 2px;
    background: linear-gradient(90deg, var(--cyan-dim), var(--violet));
    position: relative;
    box-shadow: 0 0 8px rgba(0,212,255,.3);
    animation: connPulse 2s ease-in-out infinite;
}
.conn-arrow::after {
    content: '';
    position: absolute; right: -6px; top: -5px;
    border: 6px solid transparent;
    border-left: 9px solid var(--violet);
}
@keyframes connPulse {
    0%, 100% { opacity: .5; box-shadow: 0 0 8px rgba(0,212,255,.2); }
    50%       { opacity: 1; box-shadow: 0 0 20px rgba(0,212,255,.5); }
}

/* ══════════════════════════════════════
   TRUST / STATS BANNER
══════════════════════════════════════ */
.trust-sec {
    padding: 64px 0;
    background: linear-gradient(90deg,
        rgba(0,212,255,.03) 0%,
        rgba(168,85,247,.04) 50%,
        rgba(0,212,255,.03) 100%);
    border-top: 1px solid rgba(168,85,247,.1);
    border-bottom: 1px solid rgba(168,85,247,.1);
    position: relative;
}
.trust-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 32px; text-align: center;
}
.trust-item {
    position: relative; padding: 16px;
    border-right: 1px solid rgba(255,255,255,.05);
    transition: transform .3s;
}
.trust-item:last-child { border-right: none; }
.trust-item:hover { transform: translateY(-4px); }
.trust-num {
    font-family: var(--font-display);
    font-size: 2.8rem; font-weight: 900;
    background: linear-gradient(135deg, var(--cyan), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    display: block; line-height: 1;
    filter: drop-shadow(0 0 12px rgba(0,212,255,.2));
}
.trust-lbl {
    font-family: var(--font-mono); font-size: .62rem;
    color: var(--text-3); letter-spacing: .14em;
    text-transform: uppercase; margin-top: 8px;
    display: block;
}

/* ══════════════════════════════════════
   CTA SECTION
══════════════════════════════════════ */
.cta-sec {
    padding: 110px 0;
    position: relative; overflow: hidden;
}
.cta-sec::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent 5%, rgba(232,121,249,.3) 50%, transparent 95%);
}
/* Animated radial glow behind CTA box */
.cta-sec::after {
    content: '';
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 600px; height: 400px;
    background: radial-gradient(ellipse, rgba(168,85,247,.06), transparent 70%);
    pointer-events: none;
    animation: ctaGlow 6s ease-in-out infinite alternate;
}
@keyframes ctaGlow {
    from { transform: translate(-50%, -50%) scale(1); opacity: .6; }
    to   { transform: translate(-50%, -50%) scale(1.3); opacity: 1; }
}
.cta-box {
    background: linear-gradient(135deg,
        rgba(0,212,255,.04) 0%,
        rgba(168,85,247,.07) 40%,
        rgba(232,121,249,.04) 100%);
    border: 1px solid rgba(168,85,247,.22);
    border-radius: var(--radius-xl);
    padding: 88px 64px;
    text-align: center; position: relative; overflow: hidden;
    box-shadow: 0 0 100px rgba(168,85,247,.07), inset 0 1px 0 rgba(255,255,255,.05);
    z-index: 1;
}
.cta-box::before {
    content: '';
    position: absolute; top: -1px; left: 15%; right: 15%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--cyan-dim), var(--violet), var(--mag-bright), transparent);
    box-shadow: 0 0 20px rgba(0,212,255,.4);
}
/* Animated inner glow orb */
.cta-box::after {
    content: '';
    position: absolute; top: -80px; left: 50%; transform: translateX(-50%);
    width: 400px; height: 300px;
    background: radial-gradient(ellipse at center top, rgba(168,85,247,.1), transparent 70%);
    pointer-events: none;
    animation: ctaOrb 5s ease-in-out infinite alternate;
}
@keyframes ctaOrb {
    from { opacity: .5; transform: translateX(-50%) scale(1); }
    to   { opacity: 1; transform: translateX(-50%) scale(1.2); }
}
.cta-badge {
    display: inline-block; padding: 7px 18px;
    border-radius: 50px; font-family: var(--font-mono); font-size: .62rem;
    letter-spacing: .16em; text-transform: uppercase;
    background: rgba(232,121,249,.08); border: 1px solid rgba(232,121,249,.28);
    color: var(--mag-bright); margin-bottom: 28px;
    position: relative; z-index: 1;
    box-shadow: 0 0 20px rgba(232,121,249,.08);
}
.cta-title {
    font-family: var(--font-display);
    font-size: clamp(2.2rem, 4.5vw, 3.5rem);
    font-weight: 800; letter-spacing: -.04em;
    color: var(--text-1); line-height: 1.08; margin-bottom: 18px;
    position: relative; z-index: 1;
}
.cta-title .g {
    background: linear-gradient(135deg, var(--cyan), var(--violet), var(--mag-bright));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 0 16px rgba(0,212,255,.2));
}
.cta-desc {
    font-size: .92rem; color: var(--text-2);
    line-height: 1.78; margin-bottom: 44px;
    position: relative; z-index: 1;
}
.cta-micro {
    font-family: var(--font-mono); font-size: .62rem;
    color: var(--text-3); letter-spacing: .08em;
    margin-top: 18px; display: block;
    position: relative; z-index: 1;
}
.cta-actions {
    display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;
    position: relative; z-index: 1;
}

/* ══════════════════════════════════════
   FOOTER
══════════════════════════════════════ */
.footer-sec {
    border-top: 1px solid rgba(255,255,255,.04);
    padding: 64px 0 30px;
    background: linear-gradient(180deg, #02020a 0%, #01010707 100%);
    position: relative;
}
.footer-sec::before {
    content: '';
    position: absolute; top: 0; left: 10%; right: 10%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,255,.15), rgba(168,85,247,.2), transparent);
}
.footer-grid {
    display: grid; grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 48px; margin-bottom: 48px;
}
.footer-brand-name {
    font-family: var(--font-display); font-size: .85rem;
    font-weight: 800; letter-spacing: .15em;
    text-transform: uppercase; color: var(--text-1);
    display: flex; align-items: center; gap: 10px; margin-bottom: 12px;
}
.footer-brand-name .brand-wordmark {
    font-size: 1.1rem;
    letter-spacing: .17em;
}
.brand-subline {
    font-family: var(--font-mono);
    font-size: .56rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--text-3: white;);
    margin-top: 4px;
}
.footer-tagline {
    font-size: .8rem; color: var(--text-3); line-height: 1.7;
    max-width: 240px;
}
.footer-col-head {
    font-family: var(--font-mono); font-size: .6rem;
    letter-spacing: .24em; text-transform: uppercase;
    color: var(--cyan-dim); margin-bottom: 18px;
}
.footer-lnk {
    display: block; font-size: .8rem;
    color: var(--text-3); text-decoration: none;
    margin-bottom: 11px; transition: color .2s, transform .2s;
    position: relative; padding-left: 0;
}
.footer-lnk::before {
    content: '›';
    position: absolute; left: -14px; opacity: 0; color: var(--cyan);
    transition: opacity .2s, left .2s;
}
.footer-lnk:hover { color: var(--text-2); transform: translateX(6px); }
.footer-lnk:hover::before { opacity: 1; left: -10px; }
.footer-bottom {
    border-top: 1px solid rgba(255,255,255,.04);
    padding-top: 24px;
    display: flex; align-items: center; justify-content: space-between;
    font-family: var(--font-mono); font-size: .62rem;
    color: var(--text-3); letter-spacing: .06em;
}
.footer-copy-sig {
    background: linear-gradient(90deg, var(--cyan-dim), var(--violet));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.footer-copy-brand {
    display: flex;
    align-items: center;
    gap: 10px;
}
.brand-mini {
    width: 22px;
    height: 22px;
}
.brand-mini .nav-logo-bg {
    border-radius: 8px;
}
.brand-mini .nav-logo-spin {
    inset: -2px;
    border-radius: 10px;
}
.brand-mini .nav-logo-icon {
    font-size: .72rem;
}

/* ══════════════════════════════════════
   ANIMATIONS
══════════════════════════════════════ */
@keyframes slideUp {
    from { opacity:0; transform:translateY(32px); }
    to   { opacity:1; transform:translateY(0); }
}

/* ══════════════════════════════════════
   GLITCH TEXT EFFECT (on hover)
══════════════════════════════════════ */
.glitch {
    position: relative;
}
.glitch:hover::before,
.glitch:hover::after {
    content: attr(data-text);
    position: absolute; top: 0; left: 0;
    width: 100%; height: 100%;
    background: transparent;
    -webkit-background-clip: text; background-clip: text;
}
.glitch:hover::before {
    color: var(--cyan); opacity: .7;
    animation: glitchTop .4s steps(2) infinite;
    clip-path: polygon(0 0, 100% 0, 100% 40%, 0 40%);
}
.glitch:hover::after {
    color: var(--mag-bright); opacity: .7;
    animation: glitchBot .4s steps(2) infinite;
    clip-path: polygon(0 60%, 100% 60%, 100% 100%, 0 100%);
}
@keyframes glitchTop {
    0%   { transform: translate(-2px, -1px); }
    50%  { transform: translate(2px, 1px); }
    100% { transform: translate(-1px, 2px); }
}
@keyframes glitchBot {
    0%   { transform: translate(2px, 1px); }
    50%  { transform: translate(-2px, -1px); }
    100% { transform: translate(1px, -2px); }
}

/* ══════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════ */
@media (max-width: 1100px) {
    .hero-section  { grid-template-columns: 1fr; gap:48px; padding:64px 32px 48px; }
    .feats-grid    { grid-template-columns: repeat(2,1fr); }
    .steps-row     { grid-template-columns: 1fr; gap:16px; }
    .step-connector{ display:none; }
    .trust-grid    { grid-template-columns: repeat(2,1fr); }
    .footer-grid   { grid-template-columns: 1fr 1fr; gap:36px; }
    .nav-center-links { display:none; }
}
@media (max-width: 768px) {
    .block-container { padding: 0 !important; }
    .navbar { padding: 0 20px; }
    .nav-inner { height: 62px; }
    .hero-section { padding: 48px 20px 36px; }
    .hero-stats { gap:24px; }
    .feats-grid { grid-template-columns: 1fr; padding: 0 20px; gap:12px; }
    .sec-wrap, .footer-inner { padding: 0 20px; }
    .cta-box { padding: 52px 24px; border-radius: 18px; }
    .footer-grid { grid-template-columns: 1fr; gap:28px; }
    .footer-bottom { flex-direction: column; gap:10px; text-align:center; }
    div[data-testid="stButton"] > button { height: 48px !important; font-size:.75rem !important; }
    .hero-actions, .cta-actions { flex-direction: column; }
    div[data-testid="stButton"].btn-primary > button,
    div[data-testid="stButton"].btn-ghost > button { width: 100% !important; }
    .trust-item { border-right: none; border-bottom: 1px solid rgba(255,255,255,.05); }
}
@media (max-width: 480px) {
    .trust-grid { grid-template-columns: 1fr 1fr; }
    .hero-stats { flex-wrap: wrap; gap: 20px; }
    .feats-sec, .how-sec, .cta-sec { padding: 72px 0; }
}
</style>
"""

PARTICLE_JS = """
<script>
(function() {
    // Wait for canvas to be in DOM
    function initParticles() {
        const canvas = document.getElementById('particle-canvas');
        if (!canvas) { setTimeout(initParticles, 200); return; }
        const ctx = canvas.getContext('2d');
        let W, H, particles = [], mouse = { x: -9999, y: -9999 };
        const COLORS = ['rgba(0,212,255,', 'rgba(168,85,247,', 'rgba(52,211,153,', 'rgba(232,121,249,'];
        
        function resize() {
            W = canvas.width  = window.innerWidth;
            H = canvas.height = window.innerHeight;
        }
        
        function Particle() {
            this.reset = function() {
                this.x  = Math.random() * W;
                this.y  = Math.random() * H;
                this.vx = (Math.random() - .5) * .4;
                this.vy = (Math.random() - .5) * .4;
                this.r  = Math.random() * 1.5 + .3;
                this.a  = Math.random() * .5 + .05;
                this.c  = COLORS[Math.floor(Math.random() * COLORS.length)];
                this.life = 0;
                this.maxLife = 200 + Math.random() * 400;
            };
            this.reset();
            this.life = Math.random() * this.maxLife; // stagger start
        }
        
        // Create particles
        for (let i = 0; i < 90; i++) particles.push(new Particle());
        
        // Mouse parallax
        document.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });
        
        function draw() {
            ctx.clearRect(0, 0, W, H);
            
            particles.forEach(p => {
                p.life++;
                if (p.life > p.maxLife) p.reset();
                
                // Mouse repulsion (subtle)
                const dx = mouse.x - p.x, dy = mouse.y - p.y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 120) {
                    p.vx -= (dx / dist) * .015;
                    p.vy -= (dy / dist) * .015;
                }
                // Damping
                p.vx *= .998; p.vy *= .998;
                p.x += p.vx; p.y += p.vy;
                
                // Fade in/out
                const fadeLen = 60;
                let alpha = p.a;
                if (p.life < fadeLen) alpha = p.a * (p.life / fadeLen);
                if (p.life > p.maxLife - fadeLen) alpha = p.a * ((p.maxLife - p.life) / fadeLen);
                
                // Draw
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = p.c + alpha + ')';
                ctx.fill();
                if (p.r > 1) {
                    ctx.shadowBlur = 8;
                    ctx.shadowColor = p.c + alpha + ')';
                    ctx.fill();
                    ctx.shadowBlur = 0;
                }
            });
            
            // Draw connection lines
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const a = particles[i], b = particles[j];
                    const dx = a.x - b.x, dy = a.y - b.y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    if (dist < 110) {
                        const alpha = (1 - dist/110) * 0.04;
                        ctx.beginPath();
                        ctx.moveTo(a.x, a.y);
                        ctx.lineTo(b.x, b.y);
                        ctx.strokeStyle = `rgba(0,212,255,${alpha})`;
                        ctx.lineWidth = .6;
                        ctx.stroke();
                    }
                }
            }
            
            requestAnimationFrame(draw);
        }
        
        resize();
        window.addEventListener('resize', resize);
        draw();
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initParticles);
    } else {
        initParticles();
    }
})();
</script>
"""


def show_landing_page():
    """
    Renders the ultra-premium landing page.
    Returns True when any CTA button is clicked.
    """
    st.markdown(LANDING_CSS, unsafe_allow_html=True)

    # Particle canvas + background layers
    st.markdown(f"""
    <canvas id="particle-canvas"></canvas>
    <div class="bg-canvas"></div>
    <div class="scan-beam"></div>
    <div class="scan-beam-2"></div>
    <!-- Floating hex shapes -->
    <div class="hex-float">⬡</div>
    <div class="hex-float">◈</div>
    <div class="hex-float">⬡</div>
    <div class="hex-float">◇</div>
    <div class="hex-float">⬡</div>
    <div class="hex-float">◈</div>
    <div class="hex-float">◇</div>
    <div class="lp">
    {PARTICLE_JS}
    """, unsafe_allow_html=True)

    # ─── NAVBAR ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="navbar">
        <div class="nav-inner">
            <div class="nav-brand">
                <div class="nav-logo-ring">
                    <div class="nav-logo-bg"></div>
                    <div class="nav-logo-spin"></div>
                    <span class="nav-logo-icon">🛡</span>
                </div>
                <div class="nav-brand-stack">
                    <span class="nav-wordmark"><em>VULN</em>SAGE</span>
                    <span class="nav-brand-sub">AI-Powered Web Vulnerability Scanner</span>
                </div>
            </div>
            <div class="nav-center-links">
                <a href="#" class="nav-link">Features</a>
                <a href="#" class="nav-link">How It Works</a>
                <a href="#" class="nav-link">Docs</a>
                <a href="#" class="nav-link">Pricing</a>
            </div>
            <div class="nav-status-chip">
                <div class="status-dot"></div>
                ALL SYSTEMS ONLINE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, nav_btn_col = st.columns([5, 1])
    with nav_btn_col:
        st.markdown('<div class="btn-primary" style="margin-top:-54px;margin-right:10px">',
                    unsafe_allow_html=True)
        nav_launch = st.button("Login/Signup", key="nav_launch", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ─── HERO ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="hero-outer">', unsafe_allow_html=True)
    h_left, h_right = st.columns([1.15, 0.85], gap="large")

    with h_left:
        st.markdown("""
        <div class="hero-section" style="display:block;padding:88px 48px 0;">
            <div class="hero-badge">
                <div class="hero-badge-dot"></div>
                ⬡ &nbsp;Agentic AI Security Platform · v4.0 · OWASP-Ready
            </div>
            <h1 class="hero-h1">
                Detect Threats<br>
                <span class="grad" data-text="Before Attackers">Before Attackers</span><br>
                Strike.
            </h1>
            <p class="hero-h1-sub">Precision vulnerability scanning, operationally ready.</p>
            <p class="hero-desc">
                The platform combines deep crawling, ML-powered detection, and AI orchestration
                to surface XSS, SQLi, header misconfigurations, and critical risks — with
                evidence-first output, CVSS scoring, and auto-generated fix code.
            </p>
        </div>
        """, unsafe_allow_html=True)

        bc1, bc2 = st.columns([1.1, 0.9])
        with bc1:
            st.markdown('<div class="btn-primary" style="padding-left:48px">', unsafe_allow_html=True)
            hero_launch = st.button("🚀 Launch Scanner", key="hero_launch", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with bc2:
            st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with h_right:
        st.markdown("""
        <div class="term-wrap" style="padding:88px 48px 0 0;">
            <div class="term-frame">
                <div class="term-topbar">
                    <div class="term-circs">
                        <span class="tc tc-r"></span>
                        <span class="tc tc-y"></span>
                        <span class="tc tc-g"></span>
                    </div>
                    <span class="term-title">secure-scan.log · target: example.com</span>
                    <span class="ping-dot"></span>
                </div>
                <div class="term-body">
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-mute">Initializing security scanner neural engine...</span></div>
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-ok">✓  Neural model loaded — 2.4 GB weights</span></div>
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-ok">✓  Threat DB synced — 847,312 signatures</span></div>
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-info">⬡  Subdomain enumeration: 14 targets found</span></div>
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-mute">Crawling &amp; fingerprinting target surface...</span></div>
                    <div class="t-line">
                        <span class="t-prompt">›</span>
                        <span class="t-mute">Deep scan progress: <span class="t-ok">87%</span></span>
                    </div>
                    <div class="t-progress-bar"><div class="t-progress-fill"></div></div>
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-warn">⚠&nbsp; XSS found <span class="t-badge t-badge-med">MEDIUM</span><span class="t-mute"> · conf: 94% · /search?q=</span></span></div>
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-err">✗&nbsp; SQLi risk <span class="t-badge t-badge-crit">CRITICAL</span><span class="t-mute"> · conf: 99% · /api/users</span></span></div>
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-ok">✓&nbsp; Misconfig <span class="t-badge t-badge-low">LOW</span><span class="t-mute"> · HSTS header missing</span></span></div>
                    <div class="t-line"><span class="t-prompt">›</span><span class="t-info">⬡  Generating remediation report… <span class="t-cursor"></span></span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # /hero-outer

    # ─── LIVE THREAT TICKER ────────────────────────────────────────────────────
    ticker_items = (
        '<span class="t-err">✗</span> SQLi Blocked · api.target.io/v2/users',
        '<span class="t-warn">⚠</span> XSS Detected · shop.example.com/search',
        '<span class="t-ok">✓</span> Scan Complete · secure.fintech.co · 0 critical',
        '<span class="t-err">✗</span> SSRF Attempt · internal.api/metadata',
        '<span class="t-warn">⚠</span> Open Redirect · auth.portal.net',
        '<span class="t-ok">✓</span> Headers Fixed · payments.app · HSTS enforced',
        '<span class="t-err">✗</span> IDOR Risk · /api/invoice/4821',
        '<span class="t-warn">⚠</span> RCE Pattern · upload.legacy.com/file',
        '<span class="t-ok">✓</span> Report Exported · enterprise-audit-2026.pdf',
    )
    ticker_html = ''.join(
        f'<span class="ticker-item">{item}</span>'
        for item in ticker_items
    ) * 2  # duplicate for seamless loop

    st.markdown(f"""
    <div class="ticker-sec">
        <div class="ticker-inner">
            {ticker_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── FEATURE CARDS ─────────────────────────────────────────────────────────
    st.markdown("""
    <div class="feats-sec">
        <div class="sec-wrap">
            <div class="sec-head">
                <span class="sec-eyebrow">Capabilities</span>
                <h2 class="sec-title">A Full <span class="g">Arsenal</span> of Detection</h2>
                <p class="sec-sub">Military-grade vulnerability analysis powered by AI, ML, and deep threat intelligence</p>
            </div>
            <div class="feats-grid">
                <div class="feat-card">
                    <div class="card-left-border"></div>
                    <span class="feat-idx">01 — XSS Detection</span>
                    <div class="feat-icon-wrap">🎯</div>
                    <div class="feat-title">Cross-Site Scripting</div>
                    <p class="feat-desc">Identify reflected, stored, and DOM-based XSS with deep pattern recognition and contextual AI validation to eliminate false positives.</p>
                    <span class="feat-tag tag-cyan">AI-Powered</span>
                </div>
                <div class="feat-card">
                    <div class="card-left-border"></div>
                    <span class="feat-idx">02 — Injection Attacks</span>
                    <div class="feat-icon-wrap">💉</div>
                    <div class="feat-title">SQL & NoSQL Injection</div>
                    <p class="feat-desc">Advanced detection of SQL, NoSQL, and command injection vectors before they compromise your data layer — with exact proof-of-concept output.</p>
                    <span class="feat-tag tag-red">Critical Risk</span>
                </div>
                <div class="feat-card">
                    <div class="card-left-border"></div>
                    <span class="feat-idx">03 — Header Audit</span>
                    <div class="feat-icon-wrap">🛡️</div>
                    <div class="feat-title">Security Header Analysis</div>
                    <p class="feat-desc">Comprehensive audit of CSP, X-Frame-Options, HSTS, CORS, Permissions-Policy — with severity scoring and ready-to-deploy fix snippets.</p>
                    <span class="feat-tag tag-violet">Deep Audit</span>
                </div>
                <div class="feat-card">
                    <div class="card-left-border"></div>
                    <span class="feat-idx">04 — Real-time</span>
                    <div class="feat-icon-wrap">⚡</div>
                    <div class="feat-title">Live Scanning Engine</div>
                    <p class="feat-desc">Instant multi-subdomain assessment with real-time status updates, granular progress logs, and parallel execution across all targets.</p>
                    <span class="feat-tag tag-amber">&lt; 60 Seconds</span>
                </div>
                <div class="feat-card">
                    <div class="card-left-border"></div>
                    <span class="feat-idx">05 — AI Orchestration</span>
                    <div class="feat-icon-wrap">🤖</div>
                    <div class="feat-title">Agentic AI Engine</div>
                    <p class="feat-desc">LLM-powered threat assessment for intelligent risk prioritization, automated remediation planning, and adaptive attack-surface reasoning.</p>
                    <span class="feat-tag tag-green">LLM Powered</span>
                </div>
                <div class="feat-card">
                    <div class="card-left-border"></div>
                    <span class="feat-idx">06 — Reporting</span>
                    <div class="feat-icon-wrap">📋</div>
                    <div class="feat-title">Executive & Technical Reports</div>
                    <p class="feat-desc">Auto-generated security reports with CVSS scores, risk prioritization, evidence chains, code-level fixes, and exportable formats for all stakeholders.</p>
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
                <span class="sec-eyebrow">Process</span>
                <h2 class="sec-title">How <span class="g">It Works</span></h2>
                <p class="sec-sub">Three precise steps from target to comprehensive security intelligence</p>
            </div>
            <div class="steps-row">
                <div class="step-card">
                    <span class="step-number">01</span>
                    <span class="step-icon">🔗</span>
                    <div class="step-title">Submit Target URL</div>
                    <p class="step-desc">Enter any domain or URL — the AI engine automatically maps the full attack surface, enumerates subdomains, and profiles the tech stack.</p>
                </div>
                <div class="step-connector">
                    <div class="conn-arrow"></div>
                </div>
                <div class="step-card">
                    <span class="step-number">02</span>
                    <span class="step-icon">🧠</span>
                    <div class="step-title">AI Deep Analysis</div>
                    <p class="step-desc">Multi-layer checks — ML threat modeling, rule-based OWASP scanning, and agentic AI inspection — all run in parallel for maximum coverage.</p>
                </div>
                <div class="step-connector">
                    <div class="conn-arrow"></div>
                </div>
                <div class="step-card">
                    <span class="step-number">03</span>
                    <span class="step-icon">📊</span>
                    <div class="step-title">Get Actionable Report</div>
                    <p class="step-desc">A detailed vulnerability report with CVSS scores, risk prioritization, proof-of-concept evidence, and step-by-step remediation code.</p>
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
                <span class="cta-badge">✦ No Credit Card · No Setup · Free to Start</span>
                <h2 class="cta-title">
                    Ready to Secure<br><span class="g">Your Applications?</span>
                </h2>
                <p class="cta-desc">
                    Start scanning in seconds and shield your systems from critical vulnerabilities.<br>
                    Production-ready results in under a minute with full remediation guidance.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, cta_col, _ = st.columns([1, 2, 1])
    with cta_col:
        st.markdown('<div class="btn-primary" style="margin-top:-48px">', unsafe_allow_html=True)
        cta_launch = st.button("🚀 Start Free Scan", key="cta_launch", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin-top: -16px; padding-bottom: 80px;">
        <span class="cta-micro">✓ Free tier ·  ✓ Auto-generated fix code</span>
    </div>
    """, unsafe_allow_html=True)

    # ─── FOOTER ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="footer-sec">
        <div class="sec-wrap footer-inner">
            <div class="footer-grid">
                <div>
                    <div class="footer-brand-name">
                        <div class="brand-logo-ring">
                            <div class="brand-logo-bg"></div>
                            <div class="brand-logo-spin"></div>
                            <span class="brand-logo-icon">🛡</span>
                        </div>
                        <div>
                            <span class="brand-wordmark"><em>VULN</em>SAGE</span>
                            <div class="brand-subline">AI-Powered Web Vulnerability Scanner</div>
                        </div>
                    </div>
                    <p class="footer-tagline">Agentic AI web security scanning with ML-powered detection, threat intelligence enrichment, and remediation guidance. Built for defenders.</p>
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
                    <a href="#" class="footer-lnk">OWASP Guide</a>
                    <a href="#" class="footer-lnk">Security Blog</a>
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
                <span class="footer-copy-brand">
                    <span class="nav-logo-ring brand-mini">
                        <span class="nav-logo-bg"></span>
                        <span class="nav-logo-spin"></span>
                        <span class="nav-logo-icon">🛡</span>
                    </span>
                    <span>© 2026 VULNSAGE. All rights reserved.</span>
                </span>
                <span class="footer-copy-sig">Built for defenders. Powered by AI.</span>
            </div>
        </div>
    </div>
    </div><!-- /lp -->
    """, unsafe_allow_html=True)

    return nav_launch or hero_launch or cta_launch
