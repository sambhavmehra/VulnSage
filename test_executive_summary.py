#!/usr/bin/env python3
"""
Test Executive Summary Generation
Helps debug issues with Groq AI executive summary
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Check API key
if not os.getenv("GROQ_API_KEY"):
    print("❌ ERROR: GROQ_API_KEY not found")
    print("Add it to your .env file")
    sys.exit(1)

print("=" * 70)
print("🧪 Testing Executive Summary Generation")
print("=" * 70)

try:
    from ai_scanner.groq_orchestrator import GroqOrchestrator

    print("✅ Modules imported successfully\n")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Create test scan results
test_scan_results = {
    'domain_info': {
        'domain': 'example.com',
        'protocol': 'https',
        'confidence': 95
    },
    'subdomains': ['example.com', 'www.example.com', 'api.example.com'],
    'scan_summary': {
        'scan_date': '2024-02-14',
        'target_domain': 'example.com',
        'subdomains_scanned': 3,
        'total_vulnerabilities': 5,
        'severity_breakdown': {
            'Critical': 1,
            'High': 2,
            'Medium': 2,
            'Low': 0,
            'Info': 0
        },
        'vulnerability_types': {
            'SQL Injection': 1,
            'XSS': 2,
            'CSRF': 1,
            'Missing Security Header': 1
        }
    },
    'vulnerabilities': [
        {
            'type': 'SQL Injection',
            'severity': 'Critical',
            'confidence': 90,
            'risk_score': 95,
            'description': 'Login form vulnerable to SQL injection',
            'url': 'https://example.com/login'
        },
        {
            'type': 'Cross-Site Scripting (XSS)',
            'severity': 'High',
            'confidence': 85,
            'risk_score': 75,
            'description': 'Reflected XSS in search parameter',
            'url': 'https://example.com/search'
        },
        {
            'type': 'Cross-Site Scripting (XSS)',
            'severity': 'High',
            'confidence': 80,
            'risk_score': 72,
            'description': 'Stored XSS in comment form',
            'url': 'https://example.com/comments'
        },
        {
            'type': 'Missing CSRF Protection',
            'severity': 'Medium',
            'confidence': 75,
            'risk_score': 55,
            'description': 'Profile update form lacks CSRF token',
            'url': 'https://example.com/profile'
        },
        {
            'type': 'Missing Security Header',
            'severity': 'Medium',
            'confidence': 95,
            'risk_score': 50,
            'description': 'Content-Security-Policy header not set',
            'url': 'https://example.com'
        }
    ]
}

print("\n📊 Test Scan Data:")
print(f"Domain: {test_scan_results['domain_info']['domain']}")
print(f"Subdomains: {len(test_scan_results['subdomains'])}")
print(f"Total Vulnerabilities: {test_scan_results['scan_summary']['total_vulnerabilities']}")
print(f"Critical: {test_scan_results['scan_summary']['severity_breakdown']['Critical']}")
print(f"High: {test_scan_results['scan_summary']['severity_breakdown']['High']}")
print(f"Medium: {test_scan_results['scan_summary']['severity_breakdown']['Medium']}")

print("\n" + "=" * 70)
print("🤖 Generating Executive Summary with Groq AI...")
print("=" * 70)

try:
    orchestrator = GroqOrchestrator()
    print("✅ Groq Orchestrator initialized")
    print("⏳ Calling Groq API (this may take 5-10 seconds)...\n")

    summary = orchestrator.generate_executive_summary(test_scan_results)

    print("=" * 70)
    print("📄 EXECUTIVE SUMMARY")
    print("=" * 70)
    print()
    print(summary)
    print()
    print("=" * 70)

    # Check if it's the fallback
    if "OVERALL SECURITY POSTURE" in summary and "fallback" in summary.lower():
        print("\n⚠️  NOTE: This appears to be the fallback summary")
        print("The AI generation may have failed or timed out")
    elif "OVERALL SECURITY POSTURE" in summary:
        print("\n✅ Summary generated (appears to be fallback format)")
    elif len(summary) > 100:
        print("\n✅ Summary generated successfully by Groq AI!")
    else:
        print("\n⚠️  Summary seems short - may indicate an issue")

    print(f"\nSummary length: {len(summary)} characters")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    print("\nFull traceback:")
    traceback.print_exc()

print("\n" + "=" * 70)
print("💡 Troubleshooting Tips")
print("=" * 70)
print("""
If the summary failed or used fallback:

1. Check your Groq API key is valid
2. Check your internet connection
3. Verify Groq API status at https://console.groq.com
4. Check if you have API rate limits remaining
5. Try again in a few minutes (API may be temporarily busy)

If summary is working:
✓ Your setup is correct!
✓ The scanner should generate proper executive summaries
✓ Run the full scanner with: streamlit run app_ai.py
""")

print("=" * 70)