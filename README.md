# 🛡️ AI-Powered Web Vulnerability Scanner

<div align="center">

![Version](https://img.shields.io/badge/version-2.1--AI--ML-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9%2B-yellow?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red?style=for-the-badge&logo=streamlit)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**An automated web security scanner combining Groq Cloud AI (LLaMA 3.3 70B) with a trained Machine Learning model to discover subdomains, detect vulnerabilities, and generate professional security reports.**

[Features](#-features) · [Architecture](#-architecture) · [Installation](#-installation) · [Usage](#-usage) · [Configuration](#-configuration) · [Reports](#-reports)

</div>

---

## ✨ Features

### 🤖 AI-Powered Analysis
- **Groq Cloud AI (LLaMA 3.3 70B)** for intelligent domain recognition, vulnerability validation, and executive report generation
- Natural language executive summaries written in business-friendly language
- AI-computed risk scores (0–100) per vulnerability, factoring in severity, exploitability, and business impact
- AI validation layer to filter out false positives before reporting

### 🧠 Machine Learning Detection
- Pre-trained **scikit-learn** model (`vulnerability_model.pkl`) predicts vulnerability classes from page features
- Detects three vulnerability categories: **SQL Injection**, **XSS**, and **Misconfiguration**
- Feature extraction based on form count, script count, and Content Security Policy presence
- ML confidence scores shown alongside AI scores for full transparency

### 🌐 Subdomain Discovery
- **crt.sh** (Certificate Transparency Logs) — passive enumeration
- **HackerTarget API** — additional passive source
- Common subdomain wordlist probing
- Concurrent DNS resolution and HTTP validation (up to 30 parallel threads)
- IP address resolution for each discovered subdomain

### 🔍 Vulnerability Detection (Multi-Layer)
| Layer | Method | Detects |
|---|---|---|
| 1 | ML Model | SQLi, XSS, Misconfiguration |
| 2 | Pattern Matching | SQLi, XSS, CSRF, Sensitive Data |
| 3 | Groq AI | All OWASP Top 10 categories |
| 4 | Header Analysis | 5 missing security headers |
| 5 | Protocol Check | HTTP vs HTTPS |

### 📊 Vulnerability Types Covered
- SQL Injection (CWE-89)
- Cross-Site Scripting / XSS (CWE-79)
- Cross-Site Request Forgery / CSRF (CWE-352)
- Sensitive Data Exposure (CWE-200)
- Insecure Protocol / HTTP (CWE-319)
- Security Misconfiguration (CWE-16)
- Missing Security Headers: `X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security`, `Content-Security-Policy`, `X-XSS-Protection`

### 📄 Reporting
- AI-generated executive summary (via Groq)
- Full Markdown report with severity grouping, CWE IDs, proof-of-concept, and remediation guidance
- JSON export for integration with other tools
- CSV export for spreadsheet analysis
- Severity breakdown: Critical / High / Medium / Low / Info

### 🖥️ Web UI
- Streamlit-based dark-mode interface
- Secure login/registration system with hashed passwords (`users.json`)
- Scan history per user session
- Real-time progress bar during scanning
- Configurable scan options in sidebar

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                     │
│             app_ai.py · login_page.py · landing_page.py │
└────────────────────────┬────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
 ┌───────────────┐ ┌──────────────┐ ┌──────────────────┐
 │GroqOrchestrator│ │SubdomainScanner│ │VulnerabilityDetector│
 │               │ │              │ │                  │
 │ • recognize_  │ │ • crt.sh     │ │ • ML model       │
 │   domain      │ │ • HackerTarget│ │ • Pattern rules  │
 │ • analyze_    │ │ • Wordlist   │ │ • Groq AI        │
 │   page_content│ │ • DNS + HTTP │ │ • Header checks  │
 │ • validate_   │ │   validation │ │ • URL checks     │
 │   vulnerability│ └──────────────┘ └──────────────────┘
 │ • generate_   │                          │
 │   executive_  │                          ▼
 │   summary     │                  vulnerability_model.pkl
 └───────┬───────┘                  (scikit-learn classifier)
         │
         ▼
 ┌───────────────┐
 │ReportGenerator│
 │               │
 │ • Markdown    │
 │ • JSON        │
 │ • CSV         │
 └───────────────┘
```

---

## 📂 Project Structure

```
ai-vulnerability-scanner/
│
├── app_ai.py                  # Main Streamlit application
├── groq_orchestrator.py       # Groq AI wrapper (LLaMA 3.3 70B)
├── vulnerability_detector.py  # Multi-layer vulnerability detection
├── subdomain_scanner.py       # Subdomain discovery & validation
├── report_generator.py        # Report builder (Markdown / JSON / CSV)
├── crawler.py                 # Standalone site crawler utility
├── landing_page.py            # Streamlit landing page UI
├── login_page.py              # Auth system (login / register / logout)
│
├── vulnerability_model.pkl    # Pre-trained ML classifier
│
├── users.json                 # User credential store (MD5 hashed)
├── requirements.txt           # Python dependencies
├── __init__.py                # Package init
│
├── test_executive_summary.py  # Test Groq executive summary generation
└── test_ml_integration.py     # Test ML model pipeline end-to-end
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.9 or higher
- A [Groq Cloud API key](https://console.groq.com) (free tier available)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-vulnerability-scanner.git
cd ai-vulnerability-scanner
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> **Get your free API key at:** https://console.groq.com

---

## 🚀 Usage

### Run the web application

```bash
streamlit run app_ai.py
```

Open your browser and navigate to `http://localhost:8501`.

**Default credentials:**
| Username | Password | Role |
|---|---|---|
| `admin` | `admin` | Administrator |
| `demo` | `demo` | User |

> ⚠️ **Change default passwords immediately in production.**

### Run integration tests

```bash
# Test ML model pipeline
python test_ml_integration.py

# Test Groq executive summary generation
python test_executive_summary.py
```

---

## 🎛️ Configuration

Scan options are available in the sidebar:

| Option | Default | Description |
|---|---|---|
| Max Subdomains | 20 | Maximum subdomains to scan |
| Max Pages / Domain | 10 | Pages crawled per subdomain |
| Smart Crawl | Enabled | Prioritize login, admin, API pages |
| AI Validation | Enabled | Use Groq to validate findings |
| ML Model | Enabled | Use trained ML model for detection |
| Detailed Report | Enabled | Include PoC payloads in report |

---

## 📊 Reports

Each scan produces three export formats:

### Markdown Report (`.md`)
Full narrative report including:
- Executive summary (AI-generated)
- Scan statistics and risk metrics
- Discovered subdomains with IP addresses
- Vulnerabilities grouped by severity with CWE IDs, risk scores, and remediation steps
- Recommended actions (immediate, high-priority, and general)

### JSON Report (`.json`)
Machine-readable output including all raw scan data, vulnerability objects, and the executive summary — suitable for integration with SIEM tools, ticketing systems, or CI/CD pipelines.

### CSV Export (`.csv`)
Flat vulnerability list with URL, type, severity, confidence, and description — ready for spreadsheet analysis or import into vulnerability tracking tools.

---

## 🧪 ML Model Details

The pre-trained `vulnerability_model.pkl` is a scikit-learn classifier trained on web page features:

| Feature | Description |
|---|---|
| `forms` | Number of HTML forms on the page |
| `scripts` | Number of `<script>` tags |
| `missing_csp` | 1 if `Content-Security-Policy` header absent, else 0 |

**Predicted classes:** `SQL Injection` · `XSS` · `Misconfiguration`

The ML model runs alongside (not instead of) the AI and pattern-based detectors, with all findings merged and deduplicated in the final report.

---

## ⚠️ Legal Disclaimer

> **This tool is for authorized security testing only.**
>
> Only scan systems you own or have explicit written permission to test. Unauthorized scanning may violate computer fraud and abuse laws. The authors assume no liability for misuse of this software.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

*Built with ❤️ by the AI Security Team · Powered by Groq Cloud AI + Machine Learning*

</div>
#   V u l n S a g e  
 