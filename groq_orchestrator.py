"""
Groq AI Orchestrator - The Brain of the Scanner
Handles all AI operations: domain recognition, vulnerability detection, and report generation
"""

import os
import json
import requests
import time
import random
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

class GroqOrchestrator:
    """
    Central AI orchestrator using Groq Cloud for all intelligence operations
    """

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        self.max_retries = int(os.getenv("GROQ_MAX_RETRIES", "5"))
        self.timeout = int(os.getenv("GROQ_TIMEOUT_SEC", "45"))
        self.rate_limit_per_min = int(os.getenv("GROQ_RATE_LIMIT_PER_MIN", "20"))
        self.min_call_interval = 60.0 / max(1, self.rate_limit_per_min)
        self.last_call_ts = 0.0
        self.session = requests.Session()
        self.response_cache = {}

    def _call_groq(self, prompt, temperature=0.1, max_tokens=2000):
        """Make a call to Groq API"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert cybersecurity AI specializing in web vulnerability analysis. Provide precise, actionable security insights."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        cache_key = f"{temperature}|{max_tokens}|{prompt}"
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]

        for attempt in range(self.max_retries):
            try:
                # Client-side throttling to reduce 429 bursts.
                now = time.time()
                elapsed = now - self.last_call_ts
                if elapsed < self.min_call_interval:
                    time.sleep(self.min_call_interval - elapsed)

                response = self.session.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                self.last_call_ts = time.time()

                # Handle rate-limit responses with retry/backoff.
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    if retry_after and str(retry_after).isdigit():
                        wait_sec = max(1.0, float(retry_after))
                    else:
                        wait_sec = min(30.0, (2 ** attempt) + random.uniform(0.1, 1.0))
                    print(f"[WARN] Groq rate limited (429). Retrying in {wait_sec:.1f}s "
                          f"(attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_sec)
                    continue

                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                self.response_cache[cache_key] = content
                return content

            except requests.exceptions.RequestException as e:
                wait_sec = min(20.0, (2 ** attempt) + random.uniform(0.1, 1.0))
                print(f"[WARN] Groq request failed: {e}. Retrying in {wait_sec:.1f}s "
                      f"(attempt {attempt + 1}/{self.max_retries})")
                time.sleep(wait_sec)
                continue
            except Exception as e:
                print(f"[ERROR] Groq API call failed: {e}")
                return None

        print("[ERROR] Groq API call failed after retries due to rate limiting or request errors.")
        return None

    def recognize_domain(self, user_input):
        """
        Use Groq AI to intelligently recognize and extract domain information
        """

        prompt = f"""
Analyze this user input and extract domain information: "{user_input}"

Return ONLY a JSON object with these fields:
{{
    "domain": "clean_domain.com",
    "protocol": "https" or "http",
    "is_subdomain": true/false,
    "parent_domain": "parent.com" if subdomain,
    "path": "/path/to/page" if any,
    "confidence": 0-100,
    "analysis": "brief explanation"
}}

Rules:
- Extract the base domain without protocol
- Identify if it's a subdomain
- Determine if input has path/query params
- Provide confidence score

Input: {user_input}
"""

        response = self._call_groq(prompt, temperature=0.1)

        if response:
            try:
                # Extract JSON from response
                json_str = response
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0]

                domain_info = json.loads(json_str.strip())
                return domain_info

            except json.JSONDecodeError:
                print("[WARN] AI response not valid JSON, using fallback")

        # Fallback to basic parsing
        parsed = urlparse(user_input if '://' in user_input else f'http://{user_input}')
        domain = parsed.netloc or parsed.path.split('/')[0]

        return {
            "domain": domain,
            "protocol": "https",
            "is_subdomain": domain.count('.') > 1,
            "parent_domain": '.'.join(domain.split('.')[-2:]) if domain.count('.') > 1 else domain,
            "path": parsed.path if parsed.path != '/' else None,
            "confidence": 75,
            "analysis": "Fallback domain extraction"
        }

    def analyze_page_content(self, url, html_content, forms_data, scripts_data):
        """
        Use Groq AI to analyze page content for vulnerabilities with risk scoring
        """

        # Truncate content if too long
        html_snippet = html_content[:2000] if len(html_content) > 2000 else html_content

        prompt = f"""
Analyze this web page for security vulnerabilities:

URL: {url}

HTML Snippet:
{html_snippet}

Forms Found: {len(forms_data)}
Form Details:
{json.dumps(forms_data[:3], indent=2)}

Scripts: {len(scripts_data)}
External Scripts: {sum(1 for s in scripts_data if s.get('external'))}

Analyze for these vulnerability types:
1. SQL Injection (forms, URL parameters)
2. XSS (Cross-Site Scripting)
3. CSRF (Missing tokens)
4. Insecure Direct Object References
5. Security Misconfiguration
6. Sensitive Data Exposure
7. Missing Security Headers

Return ONLY a JSON array of vulnerabilities found:
[
    {{
        "type": "SQL Injection",
        "severity": "Critical|High|Medium|Low|Info",
        "confidence": 0-100,
        "risk_score": 0-100,
        "description": "detailed description",
        "location": "where found",
        "proof": "proof of concept if applicable",
        "recommendation": "how to fix",
        "cwe_id": "CWE-XXX"
    }}
]

IMPORTANT: Calculate risk_score (0-100) based on:
- Severity level (Critical=80-100, High=60-79, Medium=40-59, Low=20-39, Info=0-19)
- Exploitability (Easy exploit = +20, Medium = +10, Hard = +0)
- Impact on business (Data breach = +15, Service disruption = +10, Info disclosure = +5)
- Confidence level (High confidence = +5, Medium = +3, Low = +0)

Example risk_score calculations:
- Critical SQL Injection, Easy exploit, High confidence = 95
- Medium XSS, Medium exploit, Medium confidence = 53
- Low Missing Header, Hard exploit, Low confidence = 25

If no vulnerabilities found, return empty array: []
Be precise and only report real vulnerabilities, not theoretical ones.
"""

        response = self._call_groq(prompt, temperature=0.2, max_tokens=2500)

        if response:
            try:
                # Extract JSON array
                json_str = response
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0]

                vulnerabilities = json.loads(json_str.strip())

                # Ensure it's a list
                if isinstance(vulnerabilities, dict):
                    vulnerabilities = [vulnerabilities]
                elif not isinstance(vulnerabilities, list):
                    vulnerabilities = []

                return vulnerabilities

            except json.JSONDecodeError as e:
                print(f"[WARN] AI vulnerability analysis failed to parse JSON: {e}")
                return []

        return []

    def validate_vulnerability(self, vulnerability_data):
        """
        Use AI to validate and refine detected vulnerabilities with risk scoring
        """

        prompt = f"""
Validate this potential security vulnerability:

{json.dumps(vulnerability_data, indent=2)}

Tasks:
1. Verify if this is a real vulnerability or false positive
2. Assess the actual severity (could be overestimated)
3. Provide exploitation difficulty (Easy/Medium/Hard)
4. Add business impact assessment
5. Prioritize remediation (Critical/High/Medium/Low)
6. Calculate overall risk score (0-100)

Return JSON:
{{
    "is_valid": true/false,
    "refined_severity": "Critical|High|Medium|Low|Info",
    "exploitation_difficulty": "Easy|Medium|Hard",
    "business_impact": "description",
    "remediation_priority": "Critical|High|Medium|Low",
    "risk_score": 0-100,
    "false_positive_reason": "if is_valid=false, explain why",
    "additional_notes": "any other insights"
}}

Calculate risk_score (0-100) based on:
- Severity: Critical=25, High=20, Medium=15, Low=10, Info=5
- Exploitability: Easy=+30, Medium=+20, Hard=+10
- Business Impact: High=+25, Medium=+15, Low=+5
- Remediation Urgency: Critical=+20, High=+15, Medium=+10, Low=+5

Example:
- Critical severity (25) + Easy exploit (30) + High impact (25) + Critical urgency (20) = 100
- Medium severity (15) + Medium exploit (20) + Medium impact (15) + Medium urgency (10) = 60
- Low severity (10) + Hard exploit (10) + Low impact (5) + Low urgency (5) = 30
"""

        response = self._call_groq(prompt, temperature=0.1)

        if response:
            try:
                json_str = response
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0]

                validation = json.loads(json_str.strip())
                return validation

            except:
                pass

        return {
            "is_valid": True,
            "refined_severity": vulnerability_data.get('severity', 'Medium'),
            "exploitation_difficulty": "Medium",
            "business_impact": "Requires manual review",
            "remediation_priority": "Medium",
            "risk_score": 50,
            "additional_notes": "Auto-validated"
        }

    def generate_executive_summary(self, scan_results):
        """
        Generate executive summary of the entire scan
        """

        # Extract key information safely
        domain = scan_results.get('domain_info', {}).get('domain', 'Unknown')
        total_vulns = len(scan_results.get('vulnerabilities', []))
        subdomains_count = len(scan_results.get('subdomains', []))

        # Get severity counts
        severity_breakdown = scan_results.get('scan_summary', {}).get('severity_breakdown', {})
        critical_count = severity_breakdown.get('Critical', 0)
        high_count = severity_breakdown.get('High', 0)
        medium_count = severity_breakdown.get('Medium', 0)
        low_count = severity_breakdown.get('Low', 0)

        # Get top vulnerabilities
        top_vulns = scan_results.get('vulnerabilities', [])[:3]
        top_vulns_summary = []
        for v in top_vulns:
            top_vulns_summary.append(f"- {v.get('type', 'Unknown')} ({v.get('severity', 'Unknown')})")

        prompt = f"""
You are a cybersecurity expert writing an executive summary for a security scan.

SCAN RESULTS:
- Domain: {domain}
- Subdomains Scanned: {subdomains_count}
- Total Vulnerabilities Found: {total_vulns}
- Critical Severity: {critical_count}
- High Severity: {high_count}
- Medium Severity: {medium_count}
- Low Severity: {low_count}

TOP FINDINGS:
{chr(10).join(top_vulns_summary) if top_vulns_summary else "No major vulnerabilities"}

Write a concise executive summary (200-250 words) with these sections:

**OVERALL SECURITY POSTURE**
Rate as: Excellent / Good / Fair / Poor / Critical
(1-2 sentences explaining the rating)

**KEY FINDINGS**
(2-3 sentences about most important discoveries)

**BUSINESS RISK**
(2-3 sentences about real-world impact)

**IMMEDIATE ACTIONS REQUIRED**
(3-5 specific action items, if critical/high issues exist)

**RECOMMENDATIONS**
(2-3 strategic improvements)

RULES:
- Use clear, business-friendly language
- Be specific and actionable
- Focus on impact, not just technical details
- Use markdown formatting (headers, bold, bullets)
- NO code blocks or JSON
- Maximum 250 words total
"""

        try:
            response = self._call_groq(prompt, temperature=0.3, max_tokens=1500)

            if response and len(response.strip()) > 50:
                return response
            else:
                print("[WARN] AI executive summary too short, using fallback")
                return self._generate_fallback_summary(scan_results)

        except Exception as e:
            print(f"[ERROR] Executive summary generation failed: {e}")
            return self._generate_fallback_summary(scan_results)

    def _generate_fallback_summary(self, scan_results):
        """Generate a fallback executive summary when AI fails"""

        domain = scan_results.get('domain_info', {}).get('domain', 'Unknown')
        total_vulns = len(scan_results.get('vulnerabilities', []))
        severity_breakdown = scan_results.get('scan_summary', {}).get('severity_breakdown', {})

        critical_count = severity_breakdown.get('Critical', 0)
        high_count = severity_breakdown.get('High', 0)
        medium_count = severity_breakdown.get('Medium', 0)

        # Determine security posture
        if critical_count > 0:
            posture = "**CRITICAL**"
            rating = "The security posture requires immediate attention due to critical vulnerabilities."
        elif high_count > 2:
            posture = "**POOR**"
            rating = "Multiple high-severity vulnerabilities pose significant security risks."
        elif high_count > 0 or medium_count > 3:
            posture = "**FAIR**"
            rating = "Some security issues were identified that should be addressed."
        elif medium_count > 0:
            posture = "**GOOD**"
            rating = "Overall security is good with minor issues to address."
        else:
            posture = "**EXCELLENT**"
            rating = "No significant security vulnerabilities detected."

        summary = f"""## OVERALL SECURITY POSTURE: {posture}

{rating}

### KEY FINDINGS

The security scan of **{domain}** identified **{total_vulns} total vulnerabilities** across the scanned infrastructure:
- {critical_count} Critical severity issues
- {high_count} High severity issues  
- {medium_count} Medium severity issues

### BUSINESS RISK

"""

        if critical_count > 0 or high_count > 0:
            summary += f"""The identified vulnerabilities pose a significant risk to business operations. Critical and high-severity issues could lead to data breaches, service disruption, or unauthorized access to sensitive systems."""
        else:
            summary += f"""The current security posture presents minimal immediate risk. However, addressing the identified medium-severity issues will further strengthen the security position."""

        if critical_count > 0 or high_count > 0:
            summary += """

### IMMEDIATE ACTIONS REQUIRED

1. **Patch all critical vulnerabilities within 24 hours**
2. **Address high-severity issues within 7 days**
3. **Implement additional monitoring on affected systems**
4. **Review access controls and authentication mechanisms**
"""

        summary += """

### RECOMMENDATIONS

1. Implement regular security scanning as part of the development lifecycle
2. Establish a vulnerability management program with clear SLAs
3. Provide security training for development and operations teams
4. Consider implementing a Web Application Firewall (WAF) for additional protection
"""

        return summary

    def suggest_remediation(self, vulnerability):
        """
        Get detailed remediation steps for a specific vulnerability
        """

        prompt = f"""
Provide detailed remediation guidance for this vulnerability:

Type: {vulnerability.get('type')}
Severity: {vulnerability.get('severity')}
Description: {vulnerability.get('description')}
Location: {vulnerability.get('location')}

Provide:
1. Step-by-step remediation instructions
2. Code examples (if applicable)
3. Security best practices
4. Testing/validation steps
5. Prevention for future

Format as clear markdown.
"""

        response = self._call_groq(prompt, temperature=0.2, max_tokens=2000)
        return response or "Remediation guidance unavailable."
