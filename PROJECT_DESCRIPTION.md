# 🛡️ VulnSage — AI-Powered Web Vulnerability Scanner

## Project Overview

**VulnSage** is an advanced, AI-powered web vulnerability scanner that combines the power of **Groq Cloud AI (LLaMA 3.3 70B)** with a **trained Machine Learning model** to discover subdomains, detect vulnerabilities, and generate professional security reports. The scanner features a modern **Streamlit-based dark-mode interface** and provides comprehensive, multi-layered security analysis with autonomous remediation capabilities.

---

## 🎯 Core Mission

To democratize enterprise-grade web security testing by combining cutting-edge AI and machine learning technologies, making sophisticated vulnerability detection accessible through an intuitive, automated platform.

---

## 🚀 Key Features

### 🤖 AI-Powered Analysis
- **Groq Cloud AI (LLaMA 3.3 70B)** for intelligent domain recognition, vulnerability validation, and executive report generation
- Natural language executive summaries written in business-friendly language
- AI-computed risk scores (0–100) per vulnerability, factoring in severity, exploitability, and business impact
- AI validation layer to filter out false positives before reporting
- Autonomous security agent for vulnerability prioritization and remediation planning

### 🧠 Machine Learning Detection
- Pre-trained **scikit-learn** model (`vulnerability_model.pkl`) predicts vulnerability classes from page features
- Detects three vulnerability categories: **SQL Injection**, **XSS**, and **Misconfiguration**
- Feature extraction based on form count, script count, and Content Security Policy presence
- Self-trained threat-intel model (`bug_intel_model.pkl`) built from latest CVE/KEV intelligence
- ML confidence scores shown alongside AI scores for full transparency

### 🌐 Subdomain Discovery
- **crt.sh** (Certificate Transparency Logs) — passive enumeration
- **HackerTarget API** — additional passive source
- Common subdomain wordlist probing
- Concurrent DNS resolution and HTTP validation (up to 30 parallel threads)
- IP address resolution for each discovered subdomain

### 🔍 Vulnerability Detection (Multi-Layer Architecture)
| Layer | Method | Detects |
|-------|--------|---------|
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

### 🤖 Autonomous Security Agent
- **Vulnerability Prioritization**: AI-driven risk-based prioritization
- **Deep Analysis**: Root cause analysis, attack vectors, business impact assessment
- **Remediation Planning**: Immediate, short-term, and long-term action plans
- **Fix Code Generation**: Production-ready code fixes for common vulnerabilities
- **Fix Validation**: Verify proposed fixes address the root cause

### 🔧 Remediation Engine
- Comprehensive fix templates for common vulnerabilities
- Multi-language code examples (Python, JavaScript, PHP, Node.js)
- Security configuration templates (Nginx, Apache, Express.js, Django, Flask)
- Testing and verification procedures
- Deployment and rollback strategies

### 📡 Threat Intelligence Integration
- **NVD (National Vulnerability Database)** integration
- **CISA KEV (Known Exploited Vulnerabilities)** catalog sync
- Self-training ML model from latest threat intelligence
- Real-time vulnerability intelligence updates

### 📄 Reporting
- AI-generated executive summary (via Groq)
- Full Markdown report with severity grouping, CWE IDs, proof-of-concept, and remediation guidance
- JSON export for integration with other tools
- CSV export for spreadsheet analysis
- Severity breakdown: Critical / High / Medium / Low / Info

### 🖥️ Web UI
- Streamlit-based dark-mode interface
- Secure login/registration system with hashed passwords
- Scan history per user session
- Real-time progress bar during scanning
- Configurable scan options in sidebar
- Admin panel with user management and activity logs

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web UI (app_ai.py)             │
│             login_page.py · landing_page.py                 │
└────────────────────────┬────────────────────────────────────┘
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
 │   vulnerability│ └──────────────┘ └──────────────────────┘
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

### Additional Agent Components
```
┌─────────────────────────────────────────────────────────────┐
│              Security Agent (security_agent.py)            │
│                                                               │
│  • analyze_scan_results()  • prioritized_vulnerabilities   │
│  • _tool_analyze_vulnerability()                           │
│  • _tool_generate_fix_code()                               │
│  • _tool_create_remediation_plan()                         │
│  • _tool_validate_fix()                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│           Remediation Engine (remediation_engine.py)        │
│                                                               │
│  • generate_fix()        • generate_remediation_checklist() │
│  • _get_sql_injection_fix()                                │
│  • _get_xss_fix()       • _get_csrf_fix()                  │
│  • _get_security_headers_fix()                            │
│  • generate_configuration_template()                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│        Threat Intel Agent (threat_intel_agent.py)          │
│                                                               │
│  • collect_latest_bugs()  • _fetch_nvd_recent()           │
│  • load_cached_bugs()     • _fetch_cisa_kev()              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
VulnSage/
│
├── app_ai.py                     # Main Streamlit application
├── groq_orchestrator.py          # Groq AI wrapper (LLaMA 3.3 70B)
├── vulnerability_detector.py    # Multi-layer vulnerability detection
├── subdomain_scanner.py          # Subdomain discovery & validation
├── report_generator.py           # Report builder (Markdown / JSON / CSV)
├── security_agent.py             # Autonomous security agent
├── remediation_engine.py         # Fix code generation
├── threat_intel_agent.py         # Threat intelligence integration
├── self_training_agent.py        # Self-training ML model
├── login_page.py                 # Auth system (login / register / logout)
├── landing_page.py               # Streamlit landing page UI
├── chatbot_component.py          # AI chatbot assistant
├── admin_logger.py               # Admin logging system
│
├── crawler.py                    # Standalone site crawler utility
├── cicd_gate.py                  # CI/CD security gate
├── attack_path_agent.py          # Attack path analysis
├── scan_baseline.py              # Continuous scan baselines
├── soc_copilot.py                # SOC copilot interface
│
├── vulnerability_model.pkl       # Pre-trained ML classifier
├── bug_intel_model.pkl          # Self-trained threat-intel model
│
├── data/
│   └── latest_bugs.json          # Cached threat intelligence
│
├── users.json                   # User credential store
├── requirements.txt              # Python dependencies
├── .env                         # Environment variables (API keys)
└── __init__.py                   # Package init
```

---

## 💻 Technology Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.9+ |
| **UI Framework** | Streamlit |
| **AI Engine** | Groq Cloud (LLaMA 3.3 70B) |
| **ML Framework** | scikit-learn |
| **Web Scraping** | BeautifulSoup, requests |
| **Threat Intel** | NVD API, CISA KEV |
| **Authentication** | Custom (MD5 hashed) |

---

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:
```
env
GROQ_API_KEY=your_groq_api_key_here
```

### Scan Options (Sidebar)
| Option | Default | Description |
|--------|---------|-------------|
| Scan Depth | Standard | Quick/Standard/Deep/Comprehensive |
| Max Subdomains | 20 | Maximum subdomains to scan |
| Pages per Domain | 10 | Pages crawled per subdomain |
| AI Domain Recognition | Enabled | Use AI to extract domain |
| Smart Crawling | Enabled | Prioritize login, admin, API pages |
| ML Vuln Detection | Enabled | Random Forest model |
| AI Vuln Validation | Enabled | Use Groq to validate findings |
| Detailed Report | Enabled | Include PoC payloads |
| Threat-Intel Model | Enabled | Self-trained model |

---

## 📊 Detection Capabilities

### Multi-Layer Vulnerability Detection
1. **Machine Learning Layer**: Pre-trained scikit-learn classifier
   - Features: form count, script count, missing CSP
   - Classes: SQL Injection, XSS, Misconfiguration

2. **Pattern Matching Layer**: Rule-based detection
   - SQL injection patterns
   - XSS patterns
   - CSRF token checks
   - Sensitive data exposure

3. **AI Analysis Layer**: Groq LLaMA 3.3 70B
   - Deep semantic analysis
   - Context-aware vulnerability identification
   - OWASP Top 10 2021 coverage

4. **Header Analysis Layer**: Security header checks
   - X-Frame-Options
   - X-Content-Type-Options
   - Strict-Transport-Security
   - Content-Security-Policy
   - X-XSS-Protection

5. **Protocol Layer**: URL-based checks
   - HTTP vs HTTPS detection
   - Sensitive parameters in URLs

### Verification Pipeline
- **Deterministic Checks**: Header presence, protocol schemes
- **ML Confidence**: ≥80% confidence indicators
- **AI Validation**: Groq-powered triage
- **Heuristic Signals**: Category-specific indicators
- **Confidence Bands**: Confirmed / Probable / Suspected / Informational

---

## 📈 Reporting Features

### Report Formats
- **Markdown (.md)**: Full narrative report with executive summary
- **JSON (.json)**: Machine-readable for SIEM/ticketing integration
- **CSV (.csv)**: Flat vulnerability list for spreadsheet analysis

### Report Sections
1. Executive Summary (AI-generated)
2. Scan Statistics
3. Domain Analysis
4. Subdomain Inventory
5. Vulnerability Findings (by severity)
6. Remediation Recommendations
7. Risk Metrics

---

## 🔐 Security Features

### Authentication
- Login/Registration system
- MD5 hashed passwords
- Session management
- Admin role separation

### Agentic AI Security
- Autonomous vulnerability analysis
- Risk-based prioritization
- Business impact assessment
- Compliance mapping (GDPR, PCI-DSS)
- Remediation planning and tracking

### Robustness
- Circuit breaker pattern for API failures
- Exponential backoff with jitter
- Rate limiting
- Response caching
- Timeout handling

---

## 🎨 User Interface

### Dashboard Features
- Dark mode theme with custom styling
- Real-time scan progress
- Interactive vulnerability cards
- Severity-based color coding
- Risk score visualization
- Export functionality

### Admin Panel
- User management
- Scan history tracking
- Activity logging
- Registration logs
- Login history

---

## 🚦 Getting Started

### Installation
```
bash
# Clone repository
git clone https://github.com/your-username/VulnSage.git
cd VulnSage

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure API key
echo "GROQ_API_KEY=your_key" > .env
```

### Running
```
bash
streamlit run app_ai.py
```

### Default Credentials
| Username | Password | Role |
|----------|----------|------|
| admin | admin | Administrator |
| demo | demo | User |

---

## 📝 Legal Disclaimer

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

## 🔗 Links

- **Documentation**: [docs.vulnsage.io]
- **GitHub**: [github.com/vulnsage]
- **Groq Cloud**: [console.groq.com]
- **NVD**: [nvd.nist.gov]
- **CISA KEV**: [cisa.gov/known-exploited-vulnerabilities-catalog]

---

*Built with ❤️ by the AI Security Team · Powered by Groq Cloud AI + Machine Learning*
