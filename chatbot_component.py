"""
Agentic AI Chatbot Component
Clean chat interface using Streamlit native components.
Internally tracks user activity logs to give smart, context-aware replies via Groq.
"""

import streamlit as st
import json
import re
import base64
import io
import os
from datetime import datetime


CHATBOT_CSS = """
<style>
/* ── Chat section styling ── */
div[data-testid="stChatMessage"] {
    background: rgba(255,255,255,.02) !important;
    border: 1px solid rgba(255,255,255,.04) !important;
    border-radius: 14px !important;
    padding: 12px 16px !important;
    margin-bottom: 8px !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stChatMessage"] p {
    font-size: .88rem !important;
    line-height: 1.65 !important;
    color: #cbd5e1 !important;
}

/* Chat input bar */
div[data-testid="stChatInput"] {
    border-color: rgba(99,102,241,.2) !important;
}
div[data-testid="stChatInput"] textarea {
    font-family: 'Inter', sans-serif !important;
    font-size: .88rem !important;
    color: #e2e8f0 !important;
    caret-color: #818cf8 !important;
}

/* Chat header card */
.chat-header-card {
    background: linear-gradient(135deg, rgba(99,102,241,.08), rgba(52,211,153,.05));
    border: 1px solid rgba(99,102,241,.12);
    border-radius: 16px; padding: 16px 20px;
    margin-bottom: 16px;
    display: flex; align-items: center; gap: 14px;
}
.chat-hdr-dot {
    width: 10px; height: 10px; border-radius: 50%;
    background: #34d399; box-shadow: 0 0 10px #34d399;
    flex-shrink: 0;
}
.chat-hdr-info {
    flex: 1;
}
.chat-hdr-title {
    font-family: 'Outfit', sans-serif; font-weight: 700;
    font-size: 1.05rem; color: #e2e8f0; margin: 0;
}
.chat-hdr-sub {
    font-family: 'JetBrains Mono', monospace; font-size: .68rem;
    color: #64748b; margin-top: 2px;
}
</style>
"""


def _log_activity(action: str):
    """Silently log user activity for AI context."""
    if 'activity_log' not in st.session_state:
        st.session_state.activity_log = []
    st.session_state.activity_log.append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'action': action
    })
    # Keep last 30 entries
    st.session_state.activity_log = st.session_state.activity_log[-30:]


def _build_context():
    """Build internal context string from activity logs + scan data."""
    parts = []

    # Activity log
    logs = st.session_state.get('activity_log', [])
    if logs:
        parts.append("USER ACTIVITY LOG (recent):")
        for log in logs[-15:]:
            parts.append(f"  [{log['time']}] {log['action']}")

    # Session info
    if st.session_state.get('authenticated'):
        parts.append(f"\nUser: {st.session_state.get('username', 'unknown')}")

    # Scan data
    if st.session_state.get('scan_completed'):
        di = st.session_state.get('domain_info', {})
        vulns = st.session_state.get('vulnerabilities', [])
        subs = st.session_state.get('subdomains', [])
        parts.append(f"\nScan completed: {di.get('domain', 'N/A')}")
        parts.append(f"Subdomains: {len(subs)}, Vulnerabilities: {len(vulns)}")

        sev = {}
        for v in vulns:
            s = v.get('severity', 'Info')
            sev[s] = sev.get(s, 0) + 1
        if sev:
            parts.append(f"Severity: {json.dumps(sev)}")
        for v in vulns[:5]:
            parts.append(f"  - {v.get('type','?')} [{v.get('severity','?')}] at {v.get('url','?')}")

    if st.session_state.get('agent_analysis'):
        parts.append("\nAI Agent analysis completed.")
        plan = st.session_state.get('remediation_plan')
        if plan:
            parts.append(f"Remediation: {len(plan.get('immediate_actions',[]))} immediate, "
                         f"{len(plan.get('short_term_actions',[]))} short-term")

    history = st.session_state.get('scan_history', [])
    if history:
        parts.append(f"Total scans this session: {len(history)}")

    return "\n".join(parts) if parts else "No scan activity yet."


def _format_history():
    """Format last few chat messages for context."""
    msgs = st.session_state.get('chat_messages', [])
    recent = msgs[-8:] if len(msgs) > 8 else msgs
    lines = []
    for m in recent:
        role = "User" if m['role'] == 'user' else "Assistant"
        lines.append(f"{role}: {m['content']}")
    return "\n".join(lines) if lines else "(no prior messages)"


def _get_ai_reply(user_msg):
    """Get AI reply via Groq, with full internal context."""
    context = _build_context()
    history = _format_history()

    prompt = f"""You are VulnSage AI — a friendly, expert cybersecurity chatbot inside a vulnerability scanner dashboard.

INTERNAL CONTEXT (user activity & scan data — do NOT reveal this raw data, just use it to answer smartly):
{context}

CHAT HISTORY:
{history}

USER: {user_msg}

Rules:
- Be concise (2-4 sentences) unless detail is needed.
- Reference scan results naturally if the user asks about them.
- If no scan done yet, guide them to use the scanner.
- Be warm, helpful, professional. Use correct security terminology.
- You can explain vulnerabilities, suggest fixes, recommend next steps.
- When giving commands or code, ALWAYS wrap them in triple-backtick code blocks with a language tag (e.g. ```bash, ```python, ```sql etc).
- Never say you are "monitoring" the user. You are just a helpful assistant."""

    try:
        from groq_orchestrator import GroqOrchestrator
        orch = GroqOrchestrator()
        response = orch._call_groq(prompt, temperature=0.35, max_tokens=500)
        return response or "I'm having trouble connecting right now. Please try again."
    except Exception as e:
        return f"Sorry, I couldn't process that. ({e})"


def _extract_pdf_text(uploaded_file):
    """Extract text from an uploaded PDF file."""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(uploaded_file.read()))
        text_parts = []
        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"--- Page {page_num} ---\n{page_text}")
        uploaded_file.seek(0)  # reset for potential re-read
        full_text = "\n".join(text_parts)
        # Limit to ~3000 chars to fit in prompt
        if len(full_text) > 3000:
            full_text = full_text[:3000] + "\n... [truncated]"
        return full_text if full_text.strip() else "(No readable text found in PDF)"
    except Exception as e:
        return f"(Error reading PDF: {e})"


def _analyze_image(uploaded_file):
    """Analyze an uploaded image using Groq's vision model."""
    try:
        from PIL import Image
        img_bytes = uploaded_file.read()
        uploaded_file.seek(0)

        # Encode to base64
        b64 = base64.b64encode(img_bytes).decode('utf-8')
        mime = uploaded_file.type or 'image/png'

        # Use Groq vision model
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "(GROQ_API_KEY not set — cannot analyze image)"

        import requests
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.2-90b-vision-preview",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in detail. If it contains code, text, network diagrams, security configurations, error messages, or logs — extract and explain all of that content."},
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
                    ]
                }],
                "temperature": 0.2,
                "max_tokens": 800
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        # Fallback: describe file metadata only
        return f"(Image analysis unavailable: {e}. You uploaded an image file: {uploaded_file.name}, size: {uploaded_file.size} bytes)"


def _render_message(content):
    """Render a message, splitting code blocks into st.code() with copy buttons."""
    # Split on fenced code blocks: ```lang\ncode\n```
    parts = re.split(r'```(\w+)?\n(.*?)```', content, flags=re.DOTALL)
    # parts alternates: [text, lang, code, text, lang, code, ...]
    i = 0
    while i < len(parts):
        if i % 3 == 0:
            # Regular text
            text = parts[i].strip()
            if text:
                st.markdown(text)
        elif i % 3 == 1:
            # Language tag (next part is the code)
            lang = parts[i] or 'text'
            code = parts[i + 1].strip() if (i + 1) < len(parts) else ''
            if code:
                st.code(code, language=lang)
            i += 1  # skip the code part since we consumed it
        i += 1


def render_chatbot():
    """Render the chatbot using Streamlit native chat components."""

    # Inject styling
    st.markdown(CHATBOT_CSS, unsafe_allow_html=True)

    # Init
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'chat_visible' not in st.session_state:
        st.session_state.chat_visible = False

    # Log that dashboard is being viewed
    _log_activity("Viewing dashboard")

    # ── Toggle button ─────────────────────────────────────────────────────
    st.markdown("---")
    toggle_col1, toggle_col2 = st.columns([4, 1])
    with toggle_col2:
        label = "✕ Close Chat" if st.session_state.chat_visible else "💬 AI Chat"
        if st.button(label, key="chat_toggle", use_container_width=True):
            st.session_state.chat_visible = not st.session_state.chat_visible
            _log_activity("Opened chatbot" if st.session_state.chat_visible else "Closed chatbot")
            st.rerun()

    if not st.session_state.chat_visible:
        return

    # ── Chat header ───────────────────────────────────────────────────────
    st.markdown("""
    <div class="chat-header-card">
        <div class="chat-hdr-dot"></div>
        <div class="chat-hdr-info">
            <div class="chat-hdr-title">VulnSage AI</div>
            <div class="chat-hdr-sub">Ask anything · Upload PDFs & images for analysis</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── File uploader ─────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Upload a PDF or image for AI analysis",
        type=["pdf", "png", "jpg", "jpeg", "webp", "gif", "bmp"],
        key="chat_file_upload",
        label_visibility="collapsed"
    )

    if uploaded_file and not st.session_state.get('_last_uploaded_file') == uploaded_file.name + str(uploaded_file.size):
        # Mark as processed to avoid re-processing on rerun
        st.session_state._last_uploaded_file = uploaded_file.name + str(uploaded_file.size)
        _log_activity(f"Uploaded file: {uploaded_file.name}")

        file_ext = uploaded_file.name.rsplit('.', 1)[-1].lower()

        with st.spinner(f"📎 Analyzing {uploaded_file.name}..."):
            if file_ext == 'pdf':
                extracted = _extract_pdf_text(uploaded_file)
                file_context = f"[User uploaded PDF: {uploaded_file.name}]\n\nExtracted text:\n{extracted}"
                user_msg = f"📎 Uploaded **{uploaded_file.name}** — please analyze this PDF."
            else:
                # Image file
                extracted = _analyze_image(uploaded_file)
                file_context = f"[User uploaded image: {uploaded_file.name}]\n\nImage analysis:\n{extracted}"
                user_msg = f"📎 Uploaded **{uploaded_file.name}** — please analyze this image."

        # Add user message
        st.session_state.chat_messages.append({'role': 'user', 'content': user_msg})

        # Get AI reply with file context
        context = _build_context()
        history = _format_history()
        prompt = f"""You are VulnSage AI — a cybersecurity assistant.

INTERNAL CONTEXT:
{context}

CHAT HISTORY:
{history}

FILE CONTENT:
{file_context}

The user uploaded a file. Analyze its contents from a cybersecurity perspective. If it's a security report, summarize findings. If it's code, identify vulnerabilities. If it's a config, check for misconfigurations. If it's a screenshot, describe what you see.
When giving commands or code, ALWAYS use triple-backtick code blocks."""

        try:
            from groq_orchestrator import GroqOrchestrator
            orch = GroqOrchestrator()
            reply = orch._call_groq(prompt, temperature=0.3, max_tokens=800)
            reply = reply or "I couldn't analyze the file. Please try again."
        except Exception as e:
            reply = f"Error analyzing file: {e}"

        st.session_state.chat_messages.append({'role': 'assistant', 'content': reply})
        _log_activity(f"Chat: AI analyzed file {uploaded_file.name}")
        st.rerun()

    # ── Chat messages ─────────────────────────────────────────────────────
    if not st.session_state.chat_messages:
        with st.chat_message("assistant", avatar="🛡️"):
            st.markdown("👋 Hey! I'm **VulnSage AI** — your security assistant. Ask me anything about vulnerabilities, scans, or cybersecurity!")

    for msg in st.session_state.chat_messages:
        avatar = "🛡️" if msg['role'] == 'assistant' else "👤"
        with st.chat_message(msg['role'], avatar=avatar):
            if msg['role'] == 'assistant':
                _render_message(msg['content'])
            else:
                st.markdown(msg['content'])

    # ── Chat input ────────────────────────────────────────────────────────
    if user_input := st.chat_input("Ask VulnSage AI anything...", key="chatbot_input"):
        _log_activity(f"Chat: asked '{user_input[:50]}...'")

        # Show user message
        st.session_state.chat_messages.append({'role': 'user', 'content': user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Get & show AI reply
        with st.chat_message("assistant", avatar="🛡️"):
            with st.spinner("Thinking..."):
                reply = _get_ai_reply(user_input)
            _render_message(reply)

        st.session_state.chat_messages.append({'role': 'assistant', 'content': reply})
        _log_activity(f"Chat: AI replied")
        st.rerun()
