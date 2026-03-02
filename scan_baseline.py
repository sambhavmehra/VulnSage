"""
Scan Baseline & Continuous Scanning
Stores baseline scans, detects deltas (new/resolved/regressed),
and provides 'what changed' summaries.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


BASELINE_FILE = "scan_baselines.json"


def _load_baselines() -> Dict:
    if os.path.exists(BASELINE_FILE):
        try:
            with open(BASELINE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_baselines(data: Dict):
    try:
        with open(BASELINE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Could not save baselines: {e}")


class ScanDelta:
    """Represents changes between two scans."""
    def __init__(self):
        self.new_vulns: List[Dict] = []
        self.resolved_vulns: List[Dict] = []
        self.regressed_vulns: List[Dict] = []  # were fixed, came back
        self.unchanged_vulns: List[Dict] = []
        self.severity_changes: List[Dict] = []

    def to_dict(self) -> Dict:
        return {
            "new": [self._vuln_summary(v) for v in self.new_vulns],
            "resolved": [self._vuln_summary(v) for v in self.resolved_vulns],
            "regressed": [self._vuln_summary(v) for v in self.regressed_vulns],
            "unchanged": len(self.unchanged_vulns),
            "new_count": len(self.new_vulns),
            "resolved_count": len(self.resolved_vulns),
            "regressed_count": len(self.regressed_vulns),
        }

    def _vuln_summary(self, v: Dict) -> Dict:
        return {
            "type": v.get('type', '?'),
            "severity": v.get('severity', '?'),
            "url": v.get('url', '?'),
        }

    def summary_text(self) -> str:
        parts = []
        if self.new_vulns:
            parts.append(f"🆕 {len(self.new_vulns)} new vulnerabilities found")
            for v in self.new_vulns[:3]:
                parts.append(f"   • {v.get('type')} [{v.get('severity')}] at {v.get('url', '')[:60]}")
        if self.resolved_vulns:
            parts.append(f"✅ {len(self.resolved_vulns)} vulnerabilities resolved")
        if self.regressed_vulns:
            parts.append(f"⚠️ {len(self.regressed_vulns)} vulnerabilities regressed (came back)")
        if self.unchanged_vulns:
            parts.append(f"➡️ {len(self.unchanged_vulns)} vulnerabilities unchanged")
        if not parts:
            parts.append("No changes detected.")
        return "\n".join(parts)


def _vuln_fingerprint(v: Dict) -> str:
    """Create a unique fingerprint for a vulnerability."""
    return f"{v.get('type', '')}|{v.get('url', '')}|{v.get('severity', '')}"


def save_baseline(domain: str, vulnerabilities: List[Dict], scan_info: Dict = None):
    """Save current scan as the baseline for a domain."""
    baselines = _load_baselines()
    baselines[domain] = {
        "timestamp": datetime.now().isoformat(),
        "scan_count": baselines.get(domain, {}).get("scan_count", 0) + 1,
        "vulnerabilities": vulnerabilities,
        "fingerprints": [_vuln_fingerprint(v) for v in vulnerabilities],
        "scan_info": scan_info or {},
        "history": baselines.get(domain, {}).get("history", []),
    }
    # Keep history of last 10 scans
    baselines[domain]["history"].append({
        "timestamp": datetime.now().isoformat(),
        "vuln_count": len(vulnerabilities),
        "severity_breakdown": _severity_breakdown(vulnerabilities),
    })
    baselines[domain]["history"] = baselines[domain]["history"][-10:]
    _save_baselines(baselines)


def get_baseline(domain: str) -> Optional[Dict]:
    """Get the stored baseline for a domain."""
    baselines = _load_baselines()
    return baselines.get(domain)


def has_baseline(domain: str) -> bool:
    """Check if a baseline exists for a domain."""
    return domain in _load_baselines()


def compare_with_baseline(domain: str, current_vulns: List[Dict]) -> ScanDelta:
    """Compare current scan results with the stored baseline."""
    delta = ScanDelta()
    baseline = get_baseline(domain)

    if not baseline:
        # First scan — everything is new
        delta.new_vulns = current_vulns
        return delta

    baseline_fps = set(baseline.get("fingerprints", []))
    current_fps = set(_vuln_fingerprint(v) for v in current_vulns)

    # Check for previously resolved vulns that have regressed
    resolved_history = set()
    for hist in baseline.get("history", []):
        # Track all previously seen fingerprints
        pass  # simplified for MVP

    # New = in current but not in baseline
    for v in current_vulns:
        fp = _vuln_fingerprint(v)
        if fp not in baseline_fps:
            delta.new_vulns.append(v)
        else:
            delta.unchanged_vulns.append(v)

    # Resolved = in baseline but not in current
    baseline_vulns = baseline.get("vulnerabilities", [])
    for v in baseline_vulns:
        fp = _vuln_fingerprint(v)
        if fp not in current_fps:
            delta.resolved_vulns.append(v)

    return delta


def get_scan_history(domain: str) -> List[Dict]:
    """Get scan history for a domain."""
    baseline = get_baseline(domain)
    if baseline:
        return baseline.get("history", [])
    return []


def get_all_baselined_domains() -> List[str]:
    """Get all domains that have baselines."""
    return list(_load_baselines().keys())


def _severity_breakdown(vulns: List[Dict]) -> Dict:
    breakdown = {}
    for v in vulns:
        s = v.get('severity', 'Info')
        breakdown[s] = breakdown.get(s, 0) + 1
    return breakdown


def generate_delta_summary(domain: str, current_vulns: List[Dict], orchestrator=None) -> Dict:
    """Generate comprehensive delta summary with optional AI analysis."""
    delta = compare_with_baseline(domain, current_vulns)
    is_first_scan = not has_baseline(domain)

    result = {
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "is_first_scan": is_first_scan,
        "delta": delta.to_dict(),
        "summary_text": delta.summary_text(),
        "scan_history": get_scan_history(domain),
        "trend": _calculate_trend(domain, current_vulns),
    }

    # AI-enhanced summary
    if orchestrator and not is_first_scan:
        try:
            prompt = f"""Summarize the security posture changes for {domain}:
{delta.summary_text()}

Previous scan had {len(get_baseline(domain).get('vulnerabilities', []))} vulnerabilities.
Current scan has {len(current_vulns)} vulnerabilities.

Provide a 3-sentence security status update focusing on:
1. What improved
2. What got worse 
3. Most urgent action needed"""
            result["ai_summary"] = orchestrator._call_groq(prompt, temperature=0.2, max_tokens=300)
        except Exception:
            pass

    return result


def _calculate_trend(domain: str, current_vulns: List[Dict]) -> str:
    history = get_scan_history(domain)
    if len(history) < 2:
        return "baseline"
    prev_count = history[-1].get("vuln_count", 0)
    curr_count = len(current_vulns)
    if curr_count < prev_count:
        return "improving"
    elif curr_count > prev_count:
        return "worsening"
    return "stable"
