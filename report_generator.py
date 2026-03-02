"""
AI-Powered Report Generator
Uses Groq AI to generate comprehensive security reports
"""

import json
from datetime import datetime

class ReportGenerator:
    """
    Generates comprehensive security reports using AI
    """

    def generate_report(self, domain_info, subdomains, vulnerabilities, orchestrator, detailed=True):
        """
        Generate a comprehensive security report
        """

        # Prepare scan summary
        scan_summary = {
            'scan_date': datetime.now().isoformat(),
            'target_domain': domain_info['domain'],
            'subdomains_scanned': len(subdomains),
            'total_vulnerabilities': len(vulnerabilities),
            'severity_breakdown': self._get_severity_breakdown(vulnerabilities),
            'verification_breakdown': self._get_verification_breakdown(vulnerabilities),
            'vulnerability_types': self._get_vulnerability_types(vulnerabilities),
            'risk_metrics': self._get_risk_metrics(vulnerabilities)
        }

        # Generate AI executive summary
        executive_summary = orchestrator.generate_executive_summary({
            'domain_info': domain_info,
            'subdomains': [s.get('subdomain') or s.get('url', '') for s in subdomains],
            'vulnerabilities': vulnerabilities,
            'scan_summary': scan_summary
        })

        # Build markdown report
        markdown_report = self._build_markdown_report(
            domain_info,
            subdomains,
            vulnerabilities,
            executive_summary,
            scan_summary,
            detailed
        )

        # Build JSON report
        json_report = {
            'metadata': {
                'scan_date': scan_summary['scan_date'],
                'scanner_version': '2.0-AI',
                'target': domain_info['domain']
            },
            'domain_analysis': domain_info,
            'subdomains': subdomains,
            'vulnerabilities': vulnerabilities,
            'summary': scan_summary,
            'executive_summary': executive_summary
        }

        return {
            'markdown_report': markdown_report,
            'json_report': json_report,
            'executive_summary': executive_summary
        }

    def _get_severity_breakdown(self, vulnerabilities):
        """Count vulnerabilities by severity"""
        breakdown = {
            'Critical': 0,
            'High': 0,
            'Medium': 0,
            'Low': 0,
            'Info': 0
        }

        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'Info')
            if severity in breakdown:
                breakdown[severity] += 1

        return breakdown

    def _get_vulnerability_types(self, vulnerabilities):
        """Count vulnerabilities by type"""
        types = {}
        for vuln in vulnerabilities:
            vuln_type = vuln.get('type', 'Unknown')
            types[vuln_type] = types.get(vuln_type, 0) + 1

        return types

    def _get_verification_breakdown(self, vulnerabilities):
        """Count vulnerabilities by verification confidence band."""
        breakdown = {
            'confirmed': 0,
            'probable': 0,
            'suspected': 0,
            'info': 0
        }

        for vuln in vulnerabilities:
            status = str(vuln.get('verification_status', 'suspected')).lower()
            if status in breakdown:
                breakdown[status] += 1
            else:
                breakdown['suspected'] += 1

        return breakdown

    def _get_risk_metrics(self, vulnerabilities):
        """Calculate risk score statistics"""
        if not vulnerabilities:
            return {
                'average_risk_score': 0,
                'max_risk_score': 0,
                'min_risk_score': 0,
                'high_risk_count': 0,
                'overall_risk_level': 'Low'
            }

        risk_scores = [v.get('risk_score', 50) for v in vulnerabilities]
        avg_risk = sum(risk_scores) / len(risk_scores)

        # Determine overall risk level
        if avg_risk >= 70:
            risk_level = 'Critical'
        elif avg_risk >= 50:
            risk_level = 'High'
        elif avg_risk >= 30:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'

        return {
            'average_risk_score': round(avg_risk, 1),
            'max_risk_score': max(risk_scores),
            'min_risk_score': min(risk_scores),
            'high_risk_count': sum(1 for s in risk_scores if s >= 70),
            'overall_risk_level': risk_level
        }

    def _build_markdown_report(self, domain_info, subdomains, vulnerabilities, executive_summary, scan_summary, detailed):
        """Build a markdown-formatted report"""

        report = f"""# 🛡️ AI Security Scan Report

## Target Information
- **Domain:** {domain_info['domain']}
- **Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Scanner:** AI-Powered Vulnerability Scanner v2.1 (AI + ML)
- **Powered by:** Groq Cloud AI + Machine Learning Model

---

## 📊 Executive Summary

{executive_summary}

---

## 📈 Scan Statistics

- **Subdomains Scanned:** {scan_summary['subdomains_scanned']}
- **Total Vulnerabilities Found:** {scan_summary['total_vulnerabilities']}

### 🎯 Groq AI Risk Assessment

- **Overall Risk Level:** {scan_summary['risk_metrics']['overall_risk_level']}
- **Average Risk Score:** {scan_summary['risk_metrics']['average_risk_score']}/100
- **Highest Risk Score:** {scan_summary['risk_metrics']['max_risk_score']}/100
- **High Risk Findings:** {scan_summary['risk_metrics']['high_risk_count']}

### Severity Breakdown
"""

        # Add severity breakdown
        for severity, count in scan_summary['severity_breakdown'].items():
            if count > 0:
                emoji = {
                    'Critical': '🔴',
                    'High': '🟠',
                    'Medium': '🟡',
                    'Low': '🟢',
                    'Info': '🔵'
                }.get(severity, '⚪')
                report += f"\n- {emoji} **{severity}:** {count}"

        report += "\n\n### Vulnerability Types\n"
        for vuln_type, count in scan_summary['vulnerability_types'].items():
            report += f"\n- **{vuln_type}:** {count}"

        report += "\n\n### Verification Confidence\n"
        report += f"\n- **Confirmed:** {scan_summary['verification_breakdown']['confirmed']}"
        report += f"\n- **Probable:** {scan_summary['verification_breakdown']['probable']}"
        report += f"\n- **Suspected:** {scan_summary['verification_breakdown']['suspected']}"
        report += f"\n- **Informational:** {scan_summary['verification_breakdown']['info']}"

        # Add subdomain list
        report += "\n\n---\n\n## 🌐 Discovered Subdomains\n"
        for i, sub in enumerate(subdomains, 1):
            report += f"\n{i}. **{sub['subdomain']}**"
            report += f"\n   - URL: `{sub['url']}`"
            report += f"\n   - IP Address: `{sub.get('ip_address', 'N/A')}`"
            report += f"\n   - Status: {sub['status']}"
            if sub.get('title'):
                report += f"\n   - Title: {sub['title']}"

        # Add detailed vulnerability information
        if vulnerabilities:
            report += "\n\n---\n\n## 🔍 Detailed Vulnerability Findings\n"

            # Group by severity
            severity_order = ['Critical', 'High', 'Medium', 'Low', 'Info']

            for severity in severity_order:
                severity_vulns = [v for v in vulnerabilities if v.get('severity') == severity]

                if severity_vulns:
                    emoji = {
                        'Critical': '🔴',
                        'High': '🟠',
                        'Medium': '🟡',
                        'Low': '🟢',
                        'Info': '🔵'
                    }.get(severity, '⚪')

                    report += f"\n### {emoji} {severity} Severity ({len(severity_vulns)})\n"

                    for i, vuln in enumerate(severity_vulns, 1):
                        report += f"\n#### {i}. {vuln['type']}\n"
                        report += f"\n- **URL:** `{vuln['url']}`"

                        # Add Groq AI Risk Score prominently
                        risk_score = vuln.get('risk_score', 50)
                        if risk_score >= 80:
                            risk_emoji = "🔴"
                            risk_level = "CRITICAL RISK"
                        elif risk_score >= 60:
                            risk_emoji = "🟠"
                            risk_level = "HIGH RISK"
                        elif risk_score >= 40:
                            risk_emoji = "🟡"
                            risk_level = "MEDIUM RISK"
                        elif risk_score >= 20:
                            risk_emoji = "🟢"
                            risk_level = "LOW RISK"
                        else:
                            risk_emoji = "🔵"
                            risk_level = "INFORMATIONAL"

                        report += f"\n- {risk_emoji} **Groq AI Risk Score: {risk_score}/100** ({risk_level})"
                        report += f"\n- **Confidence:** {vuln.get('confidence', 'N/A')}%"
                        report += f"\n- **Verification Status:** {vuln.get('confidence_band', 'Suspected')}"
                        report += f"\n- **Verification Signals:** {vuln.get('verification_signal_count', 0)}"
                        
                        # Show detection method if available
                        if vuln.get('detection_method'):
                            report += f"\n- **Detection Method:** {vuln['detection_method']}"
                        
                        # Show ML prediction details if available
                        if vuln.get('ml_prediction'):
                            report += f"\n- **🤖 ML Prediction:** {vuln['ml_prediction']}"
                        
                        if vuln.get('ml_confidence_scores'):
                            report += f"\n- **🤖 ML Confidence Breakdown:**"
                            for cls, score in vuln['ml_confidence_scores'].items():
                                report += f"\n  - {cls}: {score}"
                        
                        report += f"\n- **Description:** {vuln['description']}"

                        if vuln.get('location'):
                            report += f"\n- **Location:** {vuln['location']}"

                        if vuln.get('cwe_id'):
                            report += f"\n- **CWE:** {vuln['cwe_id']}"

                        if vuln.get('exploitation_difficulty'):
                            report += f"\n- **Exploitation Difficulty:** {vuln['exploitation_difficulty']}"

                        if vuln.get('business_impact'):
                            report += f"\n- **Business Impact:** {vuln['business_impact']}"

                        if vuln.get('verification_evidence'):
                            report += "\n- **Evidence:**"
                            for item in vuln['verification_evidence'][:3]:
                                report += f"\n  - {item}"

                        report += f"\n\n**💡 Recommendation:**\n{vuln.get('recommendation', 'Manual review required')}\n"

                        if detailed and vuln.get('proof'):
                            report += f"\n**🔬 Proof of Concept:**\n```\n{vuln['proof']}\n```\n"

                        report += "\n---\n"
        else:
            report += "\n\n---\n\n## ✅ No Vulnerabilities Detected\n"
            report += "\nNo significant vulnerabilities were detected during this scan. However, this does not guarantee complete security. Regular security assessments are recommended.\n"

        # Add recommendations
        report += "\n\n---\n\n## 🎯 Recommended Actions\n"

        if scan_summary['severity_breakdown']['Critical'] > 0:
            report += "\n### 🚨 Immediate Actions Required\n"
            report += "\n1. **Address all Critical vulnerabilities immediately**"
            report += "\n2. Implement emergency security patches"
            report += "\n3. Consider taking affected systems offline until patched\n"

        if scan_summary['severity_breakdown']['High'] > 0:
            report += "\n### ⚠️ High Priority Actions\n"
            report += "\n1. Schedule remediation for High severity issues within 7 days"
            report += "\n2. Review and update security policies"
            report += "\n3. Implement additional monitoring\n"

        report += "\n### 📋 General Recommendations\n"
        report += "\n1. Conduct regular security assessments"
        report += "\n2. Implement Web Application Firewall (WAF)"
        report += "\n3. Enable security logging and monitoring"
        report += "\n4. Keep all software and dependencies updated"
        report += "\n5. Provide security awareness training to development team"
        report += "\n6. Implement secure coding practices"
        report += "\n7. Regular penetration testing"

        # Footer
        report += "\n\n---\n\n## 📝 Disclaimer\n"
        report += "\nThis report is generated by an AI-powered automated security scanner with machine learning capabilities. "
        report += "While we strive for accuracy, automated scans may produce false positives or miss certain vulnerabilities. "
        report += "This report should be used as part of a comprehensive security assessment program and reviewed by qualified security professionals.\n"

        report += "\n---\n\n*Report generated by AI Security Scanner v2.1 - Powered by Groq Cloud AI + ML Model*\n"
        report += f"*Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return report
