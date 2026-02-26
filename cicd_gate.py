"""
CI/CD Security Gate
Enforces policy rules, exports JSON + SARIF reports,
and returns machine-readable pass/fail for pipeline integration.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


# Default policy — can be overridden
DEFAULT_POLICY = {
    "name": "VulnSage Default Policy",
    "max_critical": 0,
    "max_high": 2,
    "max_medium": 10,
    "min_confidence": 50,
    "block_on_critical": True,
    "block_on_high_count": True,
    "allowed_severity_exceptions": [],  # e.g., ["Info"]
}


class PolicyResult:
    """Result of a policy evaluation."""
    def __init__(self):
        self.passed = True
        self.violations: List[Dict] = []
        self.warnings: List[Dict] = []
        self.summary = ""
        self.exit_code = 0
        self.timestamp = datetime.now().isoformat()

    def add_violation(self, rule: str, detail: str, severity: str = "error"):
        self.violations.append({
            "rule": rule,
            "detail": detail,
            "severity": severity,
            "timestamp": self.timestamp,
        })
        self.passed = False
        self.exit_code = 1

    def add_warning(self, rule: str, detail: str):
        self.warnings.append({"rule": rule, "detail": detail})

    def to_dict(self) -> Dict:
        return {
            "passed": self.passed,
            "exit_code": self.exit_code,
            "timestamp": self.timestamp,
            "violations": self.violations,
            "violations_count": len(self.violations),
            "warnings": self.warnings,
            "warnings_count": len(self.warnings),
            "summary": self.summary,
        }


class CICDGate:
    """
    Security gate for CI/CD pipelines.
    Evaluates scan results against policy, produces pass/fail + SARIF output.
    """

    def __init__(self, policy: Dict = None):
        self.policy = policy or DEFAULT_POLICY.copy()

    def evaluate(self, vulnerabilities: List[Dict], domain_info: Dict = None) -> PolicyResult:
        """Evaluate vulnerabilities against policy. Returns pass/fail result."""
        result = PolicyResult()

        if not vulnerabilities:
            result.summary = "✅ PASSED — No vulnerabilities found."
            return result

        # Count by severity
        counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "Info": 0}
        for v in vulnerabilities:
            sev = v.get('severity', 'Info')
            if sev in counts:
                counts[sev] += 1

        # Rule: Critical count
        if self.policy.get("block_on_critical") and counts["Critical"] > self.policy.get("max_critical", 0):
            result.add_violation(
                "MAX_CRITICAL_EXCEEDED",
                f"Found {counts['Critical']} Critical vulnerabilities (max allowed: {self.policy['max_critical']})",
                "critical"
            )

        # Rule: High count
        if self.policy.get("block_on_high_count") and counts["High"] > self.policy.get("max_high", 2):
            result.add_violation(
                "MAX_HIGH_EXCEEDED",
                f"Found {counts['High']} High vulnerabilities (max allowed: {self.policy['max_high']})",
                "error"
            )

        # Rule: Medium count
        if counts["Medium"] > self.policy.get("max_medium", 10):
            result.add_warning(
                "HIGH_MEDIUM_COUNT",
                f"Found {counts['Medium']} Medium vulnerabilities (threshold: {self.policy['max_medium']})"
            )

        # Rule: Low confidence findings
        low_conf = [v for v in vulnerabilities if v.get('confidence', 100) < self.policy.get("min_confidence", 50)]
        if low_conf:
            result.add_warning(
                "LOW_CONFIDENCE_FINDINGS",
                f"{len(low_conf)} findings below {self.policy['min_confidence']}% confidence threshold"
            )

        # Build summary
        if result.passed:
            result.summary = f"✅ PASSED — {len(vulnerabilities)} findings within policy limits. (C:{counts['Critical']} H:{counts['High']} M:{counts['Medium']} L:{counts['Low']})"
        else:
            result.summary = f"❌ BLOCKED — {len(result.violations)} policy violation(s). (C:{counts['Critical']} H:{counts['High']} M:{counts['Medium']} L:{counts['Low']})"

        return result

    def export_json(self, vulnerabilities: List[Dict], domain_info: Dict = None) -> str:
        """Export scan results as pipeline-friendly JSON."""
        result = self.evaluate(vulnerabilities, domain_info)
        export = {
            "vulnsage_cicd_report": {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "domain": domain_info.get('domain', 'unknown') if domain_info else 'unknown',
                "policy": self.policy,
                "gate_result": result.to_dict(),
                "findings_count": len(vulnerabilities),
                "findings": [
                    {
                        "type": v.get('type'),
                        "severity": v.get('severity'),
                        "confidence": v.get('confidence'),
                        "url": v.get('url'),
                        "description": v.get('description', ''),
                    }
                    for v in vulnerabilities
                ],
            }
        }
        return json.dumps(export, indent=2)

    def export_sarif(self, vulnerabilities: List[Dict], domain_info: Dict = None) -> str:
        """Export scan results in SARIF 2.1.0 format for GitHub/Azure DevOps."""
        rules = []
        results = []
        seen_types = {}

        for i, v in enumerate(vulnerabilities):
            vtype = v.get('type', 'Unknown')
            sev = v.get('severity', 'Info')

            # Create rule if not seen
            if vtype not in seen_types:
                rule_idx = len(rules)
                seen_types[vtype] = rule_idx
                rules.append({
                    "id": f"VULNSAGE-{rule_idx + 1:03d}",
                    "name": vtype.replace(' ', ''),
                    "shortDescription": {"text": vtype},
                    "fullDescription": {"text": v.get('description', vtype)},
                    "defaultConfiguration": {
                        "level": self._sarif_level(sev)
                    },
                    "properties": {"severity": sev},
                })

            rule_idx = seen_types[vtype]

            results.append({
                "ruleId": f"VULNSAGE-{rule_idx + 1:03d}",
                "ruleIndex": rule_idx,
                "level": self._sarif_level(sev),
                "message": {"text": v.get('description', 'Vulnerability detected')},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": v.get('url', 'unknown')},
                    }
                }],
                "properties": {
                    "confidence": v.get('confidence', 0),
                    "recommendation": v.get('recommendation', ''),
                },
            })

        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "VulnSage",
                        "version": "2.0.0",
                        "informationUri": "https://github.com/vulnsage",
                        "rules": rules,
                    }
                },
                "results": results,
                "invocations": [{
                    "executionSuccessful": True,
                    "endTimeUtc": datetime.utcnow().isoformat() + "Z",
                }],
            }],
        }
        return json.dumps(sarif, indent=2)

    def _sarif_level(self, severity: str) -> str:
        mapping = {
            "Critical": "error",
            "High": "error",
            "Medium": "warning",
            "Low": "note",
            "Info": "note",
        }
        return mapping.get(severity, "note")
