"""
Remediation Engine
Generates specific fix code and remediation solutions for common vulnerabilities
"""

import json
from typing import Dict, List, Any, Optional
from groq_orchestrator import GroqOrchestrator


class RemediationEngine:
    """
    Generates production-ready fix code and remediation solutions
    """
    
    def __init__(self, groq_orchestrator: GroqOrchestrator):
        self.orchestrator = groq_orchestrator
        
        # Pre-defined fix templates for common vulnerabilities
        self.fix_templates = {
            "sql_injection": self._get_sql_injection_fix,
            "xss": self._get_xss_fix,
            "csrf": self._get_csrf_fix,
            "security_headers": self._get_security_headers_fix,
            "insecure_protocol": self._get_https_fix,
            "information_disclosure": self._get_info_disclosure_fix
        }
        
    def generate_fix(self, vulnerability: Dict) -> Dict:
        """
        Generate comprehensive fix for a vulnerability
        """
        vuln_type = vulnerability.get("type", "").lower()
        
        # Determine vulnerability category
        category = self._classify_vulnerability(vuln_type)
        
        # Try to get template-based fix first
        if category in self.fix_templates:
            template_fix = self.fix_templates[category](vulnerability)
            # Enhance with AI-generated specifics
            ai_enhancement = self._ai_enhance_fix(vulnerability, template_fix)
            return {**template_fix, **ai_enhancement}
        else:
            # Fully AI-generated fix
            return self._ai_generate_fix(vulnerability)
    
    def generate_remediation_checklist(self, vulnerabilities: List[Dict]) -> Dict:
        """
        Generate a checklist-based remediation plan
        """
        checklist = {
            "title": "Security Remediation Checklist",
            "total_items": 0,
            "completed_items": 0,
            "categories": {}
        }
        
        for vuln in vulnerabilities:
            category = self._classify_vulnerability(vuln.get("type", ""))
            
            if category not in checklist["categories"]:
                checklist["categories"][category] = {
                    "title": category.replace("_", " ").title(),
                    "items": []
                }
            
            item = {
                "id": f"{category}_{len(checklist['categories'][category]['items']) + 1}",
                "vulnerability": vuln.get("type"),
                "severity": vuln.get("severity"),
                "description": vuln.get("description"),
                "status": "pending",
                "steps": self._generate_checklist_steps(vuln),
                "estimated_time": self._estimate_fix_time(vuln),
                "resources_needed": self._get_required_resources(vuln)
            }
            
            checklist["categories"][category]["items"].append(item)
            checklist["total_items"] += 1
        
        return checklist
    
    def generate_configuration_template(self, config_type: str) -> Dict:
        """
        Generate security configuration templates
        """
        templates = {
            "nginx_security": self._get_nginx_security_config(),
            "apache_security": self._get_apache_security_config(),
            "csp_policy": self._get_csp_template(),
            "security_headers": self._get_security_headers_config(),
            "docker_security": self._get_docker_security_config(),
            "aws_security": self._get_aws_security_config()
        }
        
        return templates.get(config_type, {
            "error": f"Template {config_type} not found",
            "available_templates": list(templates.keys())
        })
    
    def _classify_vulnerability(self, vuln_type: str) -> str:
        """Classify vulnerability into category"""
        vuln_lower = vuln_type.lower()
        
        if any(x in vuln_lower for x in ["sql", "injection", "sqli"]):
            return "sql_injection"
        elif any(x in vuln_lower for x in ["xss", "cross-site", "scripting"]):
            return "xss"
        elif any(x in vuln_lower for x in ["csrf", "cross-site request"]):
            return "csrf"
        elif any(x in vuln_lower for x in ["header", "csp", "hsts", "x-frame"]):
            return "security_headers"
        elif any(x in vuln_lower for x in ["http", "https", "ssl", "tls", "insecure protocol"]):
            return "insecure_protocol"
        elif any(x in vuln_lower for x in ["information", "disclosure", "sensitive data"]):
            return "information_disclosure"
        else:
            return "general"
    
    def _get_sql_injection_fix(self, vulnerability: Dict) -> Dict:
        """Get SQL injection fix template"""
        return {
            "vulnerability_type": "SQL Injection",
            "severity": vulnerability.get("severity", "High"),
            "fix_approach": "Parameterized Queries / Prepared Statements",
            "code_examples": {
                "python_sqlalchemy": {
                    "language": "python",
                    "description": "Using SQLAlchemy ORM (Recommended)",
                    "vulnerable_code": """# VULNERABLE - DO NOT USE
query = f"SELECT * FROM users WHERE username = '{username}'"
result = db.execute(query)""",
                    "secure_code": """# SECURE - Use parameterized queries
from sqlalchemy import text

# Method 1: Using SQLAlchemy ORM
user = db.session.query(User).filter_by(username=username).first()

# Method 2: Using parameterized queries
query = text("SELECT * FROM users WHERE username = :username")
result = db.execute(query, {"username": username})""",
                    "explanation": "SQLAlchemy ORM automatically escapes parameters. When using raw SQL, always use parameterized queries with named placeholders."
                },
                "python_psycopg2": {
                    "language": "python",
                    "description": "Using psycopg2 (PostgreSQL)",
                    "vulnerable_code": """# VULNERABLE
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")""",
                    "secure_code": """# SECURE
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))""",
                    "explanation": "Use %s placeholders and pass parameters as a tuple or list"
                },
                "php_pdo": {
                    "language": "php",
                    "description": "Using PHP PDO",
                    "vulnerable_code": """// VULNERABLE
$query = "SELECT * FROM users WHERE id = " . $_GET['id'];
$result = $db->query($query);""",
                    "secure_code": """// SECURE
$stmt = $db->prepare("SELECT * FROM users WHERE id = :id");
$stmt->execute(['id' => $_GET['id']]);
$result = $stmt->fetch();""",
                    "explanation": "Always use prepared statements with bound parameters"
                },
                "nodejs_mysql2": {
                    "language": "javascript",
                    "description": "Using mysql2/promise (Node.js)",
                    "vulnerable_code": """// VULNERABLE
const query = `SELECT * FROM users WHERE id = ${req.query.id}`;
const [rows] = await connection.execute(query);""",
                    "secure_code": """// SECURE
const [rows] = await connection.execute(
  'SELECT * FROM users WHERE id = ?',
  [req.query.id]
);""",
                    "explanation": "Use ? placeholders and pass values as an array"
                }
            },
            "additional_measures": [
                "Use ORM frameworks (SQLAlchemy, Django ORM, Hibernate) when possible",
                "Implement input validation and sanitization",
                "Apply principle of least privilege to database accounts",
                "Use stored procedures for complex queries",
                "Enable database query logging for monitoring",
                "Implement Web Application Firewall (WAF) rules"
            ],
            "testing_code": {
                "description": "Test to verify SQL injection is patched",
                "python_test": """import requests

def test_sql_injection_protection():
    # Test with SQL injection payload
    malicious_input = "' OR '1'='1"
    response = requests.post(
        'http://your-app.com/login',
        data={'username': malicious_input, 'password': 'test'}
    )
    
    # Should not grant access
    assert "Welcome" not in response.text
    assert response.status_code == 401  # Unauthorized
    
    # Test with normal input
    normal_response = requests.post(
        'http://your-app.com/login',
        data={'username': 'validuser', 'password': 'validpass'}
    )
    
    # Should work normally for valid users
    assert normal_response.status_code == 200""",
                "sqlmap_test": """# Use sqlmap to verify fix
sqlmap -u "http://your-app.com/login" \
  --data="username=test&password=test" \
  --level=5 --risk=3 \
  --batch""",
                "explanation": "sqlmap should not find any injectable parameters after the fix"
            },
            "deployment_steps": [
                "1. Identify all database query locations in the codebase",
                "2. Replace string concatenation with parameterized queries",
                "3. Update ORM models if using an ORM",
                "4. Run unit tests to ensure functionality is preserved",
                "5. Run security tests (sqlmap) to verify fix",
                "6. Deploy to staging environment",
                "7. Monitor for any database errors",
                "8. Deploy to production"
            ],
            "rollback_plan": "Keep previous code version tagged. If issues occur, rollback to previous version and investigate.",
            "verification_commands": [
                "grep -r \"execute.*f\\\"\" --include=\"*.py\" .  # Check for vulnerable patterns",
                "sqlmap -u <target> --batch  # Verify no SQL injection",
                "python -m pytest tests/security/  # Run security tests"
            ]
        }
    
    def _get_xss_fix(self, vulnerability: Dict) -> Dict:
        """Get XSS fix template"""
        return {
            "vulnerability_type": "Cross-Site Scripting (XSS)",
            "severity": vulnerability.get("severity", "High"),
            "fix_approach": "Output Encoding + Content Security Policy",
            "code_examples": {
                "python_jinja2": {
                    "language": "python",
                    "description": "Using Jinja2 auto-escaping (Flask/Django)",
                    "vulnerable_code": """# VULNERABLE - Raw HTML output
@app.route('/search')
def search():
    query = request.args.get('q', '')
    return f"<h1>Results for: {query}</h1>"  # XSS vulnerability!""",
                    "secure_code": """# SECURE - Use template with auto-escaping
from flask import render_template_string

@app.route('/search')
def search():
    query = request.args.get('q', '')
    # Jinja2 auto-escapes by default
    return render_template_string(
        '<h1>Results for: {{ query }}</h1>',
        query=query
    )

# For HTML content that must be rendered, use |safe filter carefully
@app.route('/display')
def display():
    content = get_user_content()
    # Only use |safe if content is from trusted source and sanitized
    return render_template_string(
        '<div>{{ content }}</div>',
        content=content
    )""",
                    "explanation": "Jinja2 auto-escapes variables by default. Never use the |safe filter with user input."
                },
                "javascript_react": {
                    "language": "javascript",
                    "description": "React JSX (auto-escapes by default)",
                    "vulnerable_code": """// VULNERABLE - dangerouslySetInnerHTML
function UserProfile({ userBio }) {
  return <div dangerouslySetInnerHTML={{__html: userBio}} />;
}""",
                    "secure_code": """// SECURE - JSX auto-escaping
function UserProfile({ userBio }) {
  // React JSX automatically escapes content
  return <div>{userBio}</div>;
}

// If HTML is absolutely necessary, sanitize first
import DOMPurify from 'dompurify';

function UserProfile({ userBio }) {
  const sanitizedBio = DOMPurify.sanitize(userBio);
  return <div dangerouslySetInnerHTML={{__html: sanitizedBio}} />;
}""",
                    "explanation": "React JSX auto-escapes by default. Use dangerouslySetInnerHTML only with sanitized content."
                },
                "php_htmlspecialchars": {
                    "language": "php",
                    "description": "PHP output encoding",
                    "vulnerable_code": """// VULNERABLE
echo "Hello, " . $_GET['name'];""",
                    "secure_code": """// SECURE
echo "Hello, " . htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8');

// Or use a template engine like Twig (auto-escapes)
// {{ user.name }}  // Auto-escaped""",
                    "explanation": "Always use htmlspecialchars() when outputting user data in HTML context"
                }
            },
            "configuration_fix": {
                "description": "Content Security Policy (CSP) Header",
                "config_code": """# Add to your web server config or application

# Strict CSP (Recommended)
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self';

# For Nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;

# For Apache
Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self';"

# For Express.js (Node.js)
app.use((req, res, next) => {
  res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self';");
  next();
});""",
                "explanation": "CSP prevents execution of inline scripts and restricts resource loading, significantly reducing XSS impact"
            },
            "additional_measures": [
                "Implement strict Content Security Policy (CSP)",
                "Use X-XSS-Protection header (though modern browsers rely on CSP)",
                "Validate and sanitize all user inputs on server-side",
                "Use HttpOnly flag for session cookies",
                "Implement Subresource Integrity (SRI) for external scripts",
                "Use modern frameworks that auto-escape by default"
            ],
            "testing_code": {
                "description": "Test XSS protection",
                "manual_test_payloads": [
                    "<script>alert('XSS')</script>",
                    "<img src=x onerror=alert('XSS')>",
                    "javascript:alert('XSS')",
                    "\"><script>alert(String.fromCharCode(88,83,83))</script>",
                    "'-alert(1)-'"
                ],
                "automated_test": """# Using OWASP ZAP
zap-cli quick-scan --self-contained \
  --start-options '-config api.disablekey=true' \
  --spider \
  --scan \
  --recursive \
  -r report.html \
  http://your-app.com

# Or using XSStrike
python xsstrike.py -u "http://your-app.com/search?q=test" --crawl""",
                "explanation": "Test with various XSS payloads to ensure they're properly escaped or blocked by CSP"
            },
            "deployment_steps": [
                "1. Audit all locations where user input is displayed",
                "2. Replace direct output with template engine rendering",
                "3. Add CSP headers to web server configuration",
                "4. Test with XSS payloads to verify protection",
                "5. Monitor CSP violation reports",
                "6. Gradually tighten CSP policy",
                "7. Deploy to production"
            ],
            "rollback_plan": "If CSP breaks functionality, use report-only mode first: Content-Security-Policy-Report-Only",
            "verification_commands": [
                "curl -I http://your-app.com | grep -i content-security-policy",
                "python xsstrike.py -u 'http://your-app.com/search?q=test'",
                "npm audit --audit-level=moderate  # Check for XSS vulnerabilities in dependencies"
            ]
        }
    
    def _get_csrf_fix(self, vulnerability: Dict) -> Dict:
        """Get CSRF fix template"""
        return {
            "vulnerability_type": "Cross-Site Request Forgery (CSRF)",
            "severity": vulnerability.get("severity", "Medium"),
            "fix_approach": "CSRF Tokens + SameSite Cookies",
            "code_examples": {
                "python_flask": {
                    "language": "python",
                    "description": "Flask-WTF CSRF protection",
                    "vulnerable_code": """# VULNERABLE - No CSRF protection
@app.route('/transfer', methods=['POST'])
def transfer():
    amount = request.form.get('amount')
    # Process transfer without CSRF check
    return "Transfer completed" """,
                    "secure_code": """# SECURE - Using Flask-WTF
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import FloatField

csrf = CSRFProtect(app)

class TransferForm(FlaskForm):
    amount = FloatField('Amount')

@app.route('/transfer', methods=['POST'])
def transfer():
    form = TransferForm()
    if form.validate_on_submit():  # Includes CSRF check
        amount = form.amount.data
        # Process transfer
        return "Transfer completed"
    return "Invalid request", 400

# In template:
# <form method="POST">
#     {{ form.hidden_tag() }}  <!-- Includes CSRF token -->
#     {{ form.amount.label }} {{ form.amount() }}
#     <button type="submit">Transfer</button>
# </form>""",
                    "explanation": "Flask-WTF automatically generates and validates CSRF tokens"
                },
                "python_django": {
                    "language": "python",
                    "description": "Django CSRF protection (built-in)",
                    "vulnerable_code": """# VULNERABLE - CSRF exempt
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def transfer_view(request):
    # Process without CSRF check
    pass""",
                    "secure_code": """# SECURE - Default CSRF protection
from django.shortcuts import render
from django.middleware.csrf import get_token

# Django automatically protects POST requests with CSRF
def transfer_view(request):
    if request.method == 'POST':
        # CSRF token is automatically validated
        amount = request.POST.get('amount')
        # Process transfer
        return JsonResponse({'status': 'success'})
    return render(request, 'transfer.html')

# In template (transfer.html):
# {% csrf_token %}
# <form method="POST">
#     <input type="number" name="amount">
#     <button type="submit">Transfer</button>
# </form>""",
                    "explanation": "Django has built-in CSRF protection. Never use @csrf_exempt without good reason."
                },
                "javascript_fetch": {
                    "language": "javascript",
                    "description": "Including CSRF token in AJAX requests",
                    "vulnerable_code": """// VULNERABLE - No CSRF token
fetch('/api/transfer', {
  method: 'POST',
  body: JSON.stringify({amount: 100})
});""",
                    "secure_code": """// SECURE - Include CSRF token
// Get CSRF token from meta tag or cookie
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

fetch('/api/transfer', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken  // Or 'X-CSRFToken' for Django
  },
  body: JSON.stringify({amount: 100})
});

// Or for Django:
fetch('/api/transfer', {
  method: 'POST',
  headers: {
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({amount: 100})
});""",
                    "explanation": "Always include CSRF token in state-changing AJAX requests"
                }
            },
            "configuration_fix": {
                "description": "SameSite Cookie Attribute",
                "config_code": """# Set SameSite attribute for session cookies

# Flask
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'  # or 'Strict'
)

# Django
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Express.js (Node.js)
app.use(session({
  secret: 'your-secret',
  cookie: {
    secure: true,
    httpOnly: true,
    sameSite: 'strict'
  }
}));

# PHP
session_set_cookie_params([
    'secure' => true,
    'httponly' => true,
    'samesite' => 'Lax'
]);
session_start();""",
                "explanation": "SameSite=Lax prevents CSRF from cross-site POST requests. SameSite=Strict is stronger but may break some legitimate flows."
            },
            "additional_measures": [
                "Use SameSite cookie attribute (Lax or Strict)",
                "Implement double-submit cookie pattern for APIs",
                "Verify Referer/Origin headers for sensitive actions",
                "Use custom request headers for AJAX (simple requests can't set them)",
                "Implement CAPTCHA for sensitive operations",
                "Require re-authentication for high-risk actions"
            ],
            "testing_code": {
                "description": "Test CSRF protection",
                "test_script": """# Test CSRF protection with curl

# Should FAIL (no CSRF token)
curl -X POST http://your-app.com/transfer \
  -d "amount=1000&to_account=attacker" \
  -b "sessionid=valid_session"

# Should SUCCEED (with CSRF token)
curl -X POST http://your-app.com/transfer \
  -d "amount=1000&to_account=attacker&csrf_token=VALID_TOKEN" \
  -b "sessionid=valid_session"

# Test SameSite cookies
# Try CSRF from different origin - should be blocked by browser""",
                "explanation": "Verify that requests without valid CSRF tokens are rejected"
            },
            "deployment_steps": [
                "1. Enable CSRF protection in your framework",
                "2. Add CSRF tokens to all forms",
                "3. Update AJAX requests to include CSRF tokens",
                "4. Configure SameSite cookie attributes",
                "5. Test that CSRF attacks are blocked",
                "6. Monitor for any legitimate requests being blocked",
                "7. Deploy to production"
            ],
            "rollback_plan": "If issues occur, temporarily disable CSRF for specific endpoints while investigating, but fix immediately.",
            "verification_commands": [
                "curl -X POST http://your-app.com/api/action -d 'test=data'  # Should fail without token",
                "grep -r 'csrf_exempt' --include='*.py' .  # Find any disabled CSRF",
                "python -c \"import requests; r = requests.post('http://your-app.com/action', data={'x':1}); print('CSRF Protection:', 'blocked' if r.status_code == 403 else 'VULNERABLE')\""
            ]
        }
    
    def _get_security_headers_fix(self, vulnerability: Dict) -> Dict:
        """Get security headers fix template"""
        header_name = vulnerability.get("type", "").replace("Missing Security Header: ", "")
        
        header_configs = {
            "X-Frame-Options": {
                "description": "Prevents clickjacking attacks",
                "value": "DENY or SAMEORIGIN",
                "nginx": "add_header X-Frame-Options 'SAMEORIGIN' always;",
                "apache": "Header always set X-Frame-Options 'SAMEORIGIN'",
                "express": "res.setHeader('X-Frame-Options', 'SAMEORIGIN');"
            },
            "X-Content-Type-Options": {
                "description": "Prevents MIME type sniffing",
                "value": "nosniff",
                "nginx": "add_header X-Content-Type-Options 'nosniff' always;",
                "apache": "Header always set X-Content-Type-Options 'nosniff'",
                "express": "res.setHeader('X-Content-Type-Options', 'nosniff');"
            },
            "Strict-Transport-Security": {
                "description": "Enforces HTTPS connections",
                "value": "max-age=31536000; includeSubDomains",
                "nginx": "add_header Strict-Transport-Security 'max-age=31536000; includeSubDomains' always;",
                "apache": "Header always set Strict-Transport-Security 'max-age=31536000; includeSubDomains'",
                "express": "res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');"
            },
            "Content-Security-Policy": {
                "description": "Controls resource loading",
                "value": "default-src 'self'",
                "nginx": "add_header Content-Security-Policy \"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';\" always;",
                "apache": "Header always set Content-Security-Policy \"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';\"",
                "express": "res.setHeader('Content-Security-Policy', \"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';\");"
            },
            "X-XSS-Protection": {
                "description": "Legacy XSS filter (modern browsers use CSP)",
                "value": "1; mode=block",
                "nginx": "add_header X-XSS-Protection '1; mode=block' always;",
                "apache": "Header always set X-XSS-Protection '1; mode=block'",
                "express": "res.setHeader('X-XSS-Protection', '1; mode=block');"
            }
        }
        
        config = header_configs.get(header_name, {
            "description": "Security header",
            "value": "recommended-value",
            "nginx": f"add_header {header_name} 'value' always;",
            "apache": f"Header always set {header_name} 'value'",
            "express": f"res.setHeader('{header_name}', 'value');"
        })
        
        return {
            "vulnerability_type": f"Missing Security Header: {header_name}",
            "severity": vulnerability.get("severity", "Low"),
            "fix_approach": "Add Security Header",
            "header_info": config,
            "configuration_fix": {
                "description": f"Add {header_name} header",
                "nginx_config": f"""
# Add to nginx.conf or site configuration
server {{
    ...
    {config['nginx']}
}}""",
                "apache_config": f"""
# Add to .htaccess or httpd.conf
{config['apache']}

# Or in VirtualHost:
<VirtualHost *:443>
    ...
    {config['apache']}
</VirtualHost>""",
                "express_config": f"""
// Add to Express.js middleware
app.use((req, res, next) => {{
    {config['express']}
    next();
}});

// Or use helmet middleware (recommended)
const helmet = require('helmet');
app.use(helmet());  // Sets multiple security headers automatically""",
                "python_flask": f"""
# Add to Flask app
@app.after_request
def add_security_headers(response):
    response.headers['{header_name}'] = '{config['value']}'
    return response

# Or use Flask-Talisman (recommended)
from flask_talisman import Talisman
Talisman(app)  # Sets multiple security headers""",
                "python_django": f"""
# Add to settings.py or middleware
# Django Security Middleware sets many headers automatically
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    ...
]

# In settings.py:
SECURE_CONTENT_TYPE_NOSNIFF = True  # X-Content-Type-Options
SECURE_BROWSER_XSS_FILTER = True    # X-XSS-Protection
X_FRAME_OPTIONS = 'DENY'          # X-Frame-Options
SECURE_HSTS_SECONDS = 31536000     # HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True"""
            },
            "additional_measures": [
                "Use helmet.js (Node.js) or Flask-Talisman/Django Security Middleware",
                "Test headers with securityheaders.com or Mozilla Observatory",
                "Consider using Report-Only mode for CSP initially",
                "Monitor for any functionality issues after adding headers"
            ],
            "testing_code": {
                "description": "Verify security headers",
                "curl_test": f"""# Check header is present
curl -I https://your-app.com | grep -i "{header_name}"

# Test all security headers
curl -I https://your-app.com | grep -iE '(X-Frame-Options|X-Content-Type-Options|Strict-Transport-Security|Content-Security-Policy|X-XSS-Protection)'""",
                "online_tools": [
                    "https://securityheaders.com",
                    "https://observatory.mozilla.org",
                    "https://www.ssllabs.com/ssltest"
                ]
            },
            "deployment_steps": [
                "1. Add header configuration to your web server or application",
                "2. Test locally to ensure no functionality issues",
                "3. For CSP, start with Report-Only mode",
                "4. Deploy to staging and verify",
                "5. Use online tools to verify headers are set correctly",
                "6. Deploy to production",
                "7. Monitor CSP violation reports if applicable"
            ],
            "rollback_plan": "Headers can be removed immediately by reverting configuration. For CSP, use Report-Only mode first.",
            "verification_commands": [
                f"curl -I https://your-app.com | grep -i '{header_name}'",
                "nmap --script http-security-headers -p 443 your-app.com",
                "python -c \"import requests; h = requests.head('https://your-app.com').headers; print('Security Headers:', [k for k in h.keys() if 'X-' in k or 'Content-Security' in k or 'Strict-Transport' in k])\""
            ]
        }
    
    def _get_https_fix(self, vulnerability: Dict) -> Dict:
        """Get HTTPS/fix for insecure protocol"""
        return {
            "vulnerability_type": "Insecure Protocol (HTTP)",
            "severity": vulnerability.get("severity", "Medium"),
            "fix_approach": "Enforce HTTPS with SSL/TLS",
            "configuration_fix": {
                "description": "Redirect HTTP to HTTPS and configure SSL",
                "nginx_config": """# Force HTTPS redirect
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS (optional but recommended)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}""",
                "apache_config": """# Force HTTPS
<VirtualHost *:80>
    ServerName your-domain.com
    Redirect permanent / https://your-domain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName your-domain.com
    
    SSLEngine on
    SSLCertificateFile /path/to/cert.pem
    SSLCertificateKeyFile /path/to/key.pem
    
    # Modern SSL configuration
    SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
    SSLHonorCipherOrder off
    
    # HSTS
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
</VirtualHost>""",
                "express_config": """// Force HTTPS in Express.js
const express = require('express');
const helmet = require('helmet');

const app = express();

// Trust proxy (if behind load balancer)
app.set('trust proxy', true);

// Redirect HTTP to HTTPS
app.use((req, res, next) => {
  if (req.secure || req.headers['x-forwarded-proto'] === 'https') {
    return next();
  }
  res.redirect(301, `https://${req.headers.host}${req.url}`);
});

// Use helmet for security headers
app.use(helmet.hsts({
  maxAge: 31536000,
  includeSubDomains: true,
  preload: true
}));""",
                "python_flask": """# Force HTTPS in Flask
from flask import Flask, request, redirect
from flask_talisman import Talisman

app = Flask(__name__)

# Force HTTPS
@app.before_request
def force_https():
    if not request.is_secure:
        return redirect(request.url.replace('http://', 'https://', 1), code=301)

# Or use Talisman (recommended)
Talisman(app, force_https=True)""",
                "certbot_ssl": """# Get free SSL certificate with Certbot (Let's Encrypt)

# Install Certbot
sudo apt-get install certbot python3-certbot-nginx  # For Nginx
# OR
sudo apt-get install certbot python3-certbot-apache  # For Apache

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
# OR
sudo certbot --apache -d your-domain.com -d www.your-domain.com

# Auto-renewal (usually set up automatically)
sudo certbot renew --dry-run"""
            },
            "additional_measures": [
                "Use Let's Encrypt for free SSL certificates",
                "Enable HTTP/2 for better performance",
                "Configure HSTS (HTTP Strict Transport Security)",
                "Use modern TLS versions (1.2 or 1.3 only)",
                "Implement OCSP Stapling",
                "Monitor SSL configuration with SSL Labs test"
            ],
            "testing_code": {
                "description": "Verify HTTPS configuration",
                "tests": [
                    "curl -I http://your-domain.com  # Should redirect to HTTPS",
                    "curl -I https://your-domain.com  # Should return 200 with HTTPS",
                    "nmap --script ssl-enum-ciphers -p 443 your-domain.com  # Check cipher suites",
                    "openssl s_client -connect your-domain.com:443 -tls1_2  # Test TLS 1.2"
                ],
                "online_test": "https://www.ssllabs.com/ssltest/analyze.html?d=your-domain.com"
            },
            "deployment_steps": [
                "1. Obtain SSL certificate (Let's Encrypt or commercial)",
                "2. Configure web server with SSL",
                "3. Set up HTTP to HTTPS redirect",
                "4. Test SSL configuration with SSL Labs",
                "5. Update any hardcoded HTTP URLs in your application",
                "6. Set up auto-renewal for certificates",
                "7. Monitor certificate expiration"
            ],
            "rollback_plan": "Can temporarily disable HTTPS redirect if critical issues occur, but fix immediately.",
            "verification_commands": [
                "curl -I http://your-app.com  # Should show 301 redirect",
                "curl -I https://your-app.com  # Should show 200 OK",
                "echo | openssl s_client -servername your-app.com -connect your-app.com:443 2>/dev/null | openssl x509 -noout -dates  # Check cert validity",
                "nmap --script ssl-cert,ssl-enum-ciphers -p 443 your-app.com"
            ]
        }
    
    def _get_info_disclosure_fix(self, vulnerability: Dict) -> Dict:
        """Get information disclosure fix template"""
        return {
            "vulnerability_type": "Information Disclosure",
            "severity": vulnerability.get("severity", "Medium"),
            "fix_approach": "Remove sensitive data from client-side and error messages",
            "code_examples": {
                "error_handling": {
                    "language": "python",
                    "description": "Secure error handling",
                    "vulnerable_code": """# VULNERABLE - Detailed error messages
@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({
        'error': str(error),
        'traceback': traceback.format_exc(),
        'sql_query': current_query  # NEVER expose this!
    }), 500""",
                    "secure_code": """# SECURE - Generic error messages
import logging

logger = logging.getLogger(__name__)

@app.errorhandler(Exception)
def handle_error(error):
    # Log full details internally
    logger.error(f"Error occurred: {error}", exc_info=True)
    
    # Return generic message to user
    return jsonify({
        'error': 'An internal error occurred',
        'error_id': generate_error_id()  # For support reference
    }), 500""",
                    "explanation": "Never expose stack traces, SQL queries, or internal details to users"
                }
            },
            "additional_measures": [
                "Remove comments containing sensitive info from HTML/JS",
                "Disable detailed error messages in production",
                "Remove debug endpoints and console logs",
                "Check for API keys in client-side code",
                "Review all HTML comments for sensitive data",
                "Disable server version banners"
            ],
            "deployment_steps": [
                "1. Audit all error handling code",
                "2. Replace detailed errors with generic messages",
                "3. Implement proper logging to internal systems",
                "4. Remove debug information from production builds",
                "5. Scan for API keys and secrets in codebase",
                "6. Test error scenarios to verify no info leakage"
            ],
            "rollback_plan": "Revert to previous error handling if critical debugging needed, but fix info leak immediately.",
            "verification_commands": [
                "grep -r 'password\\|secret\\|key' --include='*.html' --include='*.js' .",
                "curl http://your-app.com/nonexistent  # Check error message",
                "grep -r 'traceback\\|stacktrace' --include='*.py' ."
            ]
        }
    
    def _ai_enhance_fix(self, vulnerability: Dict, template_fix: Dict) -> Dict:
        """Enhance template fix with AI-generated specifics"""
        # Use AI to customize the fix based on specific vulnerability details
        prompt = f"""
Customize this security fix for the specific vulnerability:

Vulnerability: {json.dumps(vulnerability, indent=2)}
Base Fix: {json.dumps(template_fix, indent=2)}

Provide specific enhancements:
1. Custom code modifications based on the vulnerability location
2. Framework-specific recommendations
3. Additional context-aware fixes

Return JSON with:
{{
    "customizations": {{
        "specific_recommendations": ["rec1", "rec2"],
        "framework_specific_notes": "notes",
        "location_specific_fix": "custom fix for this location"
    }}
}}
"""
        
        try:
            response = self.orchestrator._call_groq(prompt, temperature=0.2)
            if response and "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif response and "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            if response:
                enhancements = json.loads(response.strip())
                return enhancements
        except:
            pass
        
        return {
            "customizations": {
                "specific_recommendations": ["Review vulnerability location manually"],
                "framework_specific_notes": "Apply framework best practices",
                "location_specific_fix": "See base fix template"
            }
        }
    
    def _ai_generate_fix(self, vulnerability: Dict) -> Dict:
        """Generate fix entirely using AI for unknown vulnerability types"""
        prompt = f"""
Generate a complete security fix for this vulnerability:

{json.dumps(vulnerability, indent=2)}

Provide:
1. Root cause explanation
2. Step-by-step fix instructions
3. Code examples in multiple languages
4. Testing approach
5. Deployment guidance

Return comprehensive fix guide in markdown format.
"""
        
        try:
            ai_fix = self.orchestrator._call_groq(prompt, temperature=0.2, max_tokens=2500)
            return {
                "vulnerability_type": vulnerability.get("type", "Unknown"),
                "severity": vulnerability.get("severity", "Medium"),
                "fix_approach": "AI-Generated Custom Fix",
                "ai_generated_guide": ai_fix or "AI fix generation failed. Manual review required.",
                "note": "This is a custom fix generated by AI. Please review carefully before implementation."
            }
        except:
            return {
                "vulnerability_type": vulnerability.get("type", "Unknown"),
                "severity": vulnerability.get("severity", "Medium"),
                "fix_approach": "Manual Fix Required",
                "error": "AI fix generation failed",
                "recommendation": "Consult security documentation for this vulnerability type."
            }
    
    def _generate_checklist_steps(self, vulnerability: Dict) -> List[str]:
        """Generate checklist steps for a vulnerability"""
        vuln_type = vulnerability.get("type", "").lower()
        severity = vulnerability.get("severity", "Medium")
        
        base_steps = [
            f"☐ Identify all occurrences of {vulnerability.get('type')}",
            "☐ Review affected code locations",
            "☐ Implement security fix",
            "☐ Test the fix thoroughly",
            "☐ Deploy to staging environment",
            "☐ Monitor for issues",
            "☐ Deploy to production"
        ]
        
        if severity in ["Critical", "High"]:
            base_steps.insert(0, "☐ [URGENT] Prioritize immediate fix")
            base_steps.insert(1, "☐ [URGENT] Consider temporary mitigation")
        
        return base_steps
    
    def _estimate_fix_time(self, vulnerability: Dict) -> str:
        """Estimate time to fix a vulnerability"""
        severity = vulnerability.get("severity", "Medium")
        vuln_type = vulnerability.get("type", "").lower()
        
        # Base estimates by severity
        estimates = {
            "Critical": "2-4 hours",
            "High": "4-8 hours",
            "Medium": "1-2 days",
            "Low": "2-5 days"
        }
        
        # Adjust for specific types
        if "header" in vuln_type:
            return "30 minutes - 1 hour"
        elif "http" in vuln_type or "ssl" in vuln_type:
            return "1-2 hours"
        
        return estimates.get(severity, "1-3 days")
    
    def _get_required_resources(self, vulnerability: Dict) -> List[str]:
        """Get required resources to fix a vulnerability"""
        severity = vulnerability.get("severity", "Medium")
        
        resources = ["Security Engineer"]
        
        if severity in ["Critical", "High"]:
            resources.extend(["Senior Developer", "DevOps Engineer"])
        
        if "sql" in vulnerability.get("type", "").lower():
            resources.append("Database Administrator")
        
        if "infrastructure" in vulnerability.get("type", "").lower():
            resources.append("System Administrator")
        
        return resources
    
    def _get_nginx_security_config(self) -> Dict:
        """Get Nginx security configuration template"""
        return {
            "description": "Nginx security hardening configuration",
            "config": """
# Security Headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';" always;

# SSL Configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;

# Rate Limiting
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;
limit_req zone=one burst=20 nodelay;

# Hide Nginx version
server_tokens off;
"""
        }
    
    def _get_apache_security_config(self) -> Dict:
        """Get Apache security configuration template"""
        return {
            "description": "Apache security hardening configuration",
            "config": """
# Security Headers
Header always set X-Frame-Options "SAMEORIGIN"
Header always set X-Content-Type-Options "nosniff"
Header always set X-XSS-Protection "1; mode=block"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';"

# SSL Configuration
SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
SSLCipherSuite ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384
SSLHonorCipherOrder off

# Hide Apache version
ServerTokens Prod
ServerSignature Off
"""
        }
    
    def _get_csp_template(self) -> Dict:
        """Get Content Security Policy template"""
        return {
            "description": "Content Security Policy templates",
            "strict_policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self';",
            "moderate_policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none';",
            "report_only": "default-src 'self'; report-uri /csp-report;",
            "notes": "Start with report-only mode to test, then enforce strict policy"
        }
    
    def _get_security_headers_config(self) -> Dict:
        """Get comprehensive security headers configuration"""
        return {
            "description": "Complete security headers setup",
            "headers": {
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
                "X-Frame-Options": "DENY",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
                "X-XSS-Protection": "1; mode=block"
            }
        }
    
    def _get_docker_security_config(self) -> Dict:
        """Get Docker security configuration"""
        return {
            "description": "Docker security best practices",
            "dockerfile_best_practices": [
                "Use official base images",
                "Run as non-root user",
                "Use multi-stage builds",
                "Scan images for vulnerabilities",
                "Keep images small"
            ],
            "dockerfile_example": """
# Use specific version, not 'latest'
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Change to non-root user
USER appuser

# Run application
CMD ["python", "app.py"]
"""
        }
    
    def _get_aws_security_config(self) -> Dict:
        """Get AWS security configuration"""
        return {
            "description": "AWS security best practices",
            "s3_security": [
                "Enable bucket versioning",
                "Use bucket policies to restrict access",
                "Enable server-side encryption",
                "Block public access unless required",
                "Enable access logging"
            ],
            "iam_best_practices": [
                "Use least privilege principle",
                "Enable MFA for root account",
                "Rotate access keys regularly",
                "Use IAM roles instead of access keys",
                "Enable CloudTrail for auditing"
            ]
        }
