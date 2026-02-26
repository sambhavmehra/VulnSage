"""
SOC Copilot for Triage and Response
Generates plain-language incident summaries, priority rankings,
containment steps, and remediation task objects with owner/due/SLA.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional


SLA_MAP = {
    "Critical": {"response_hours": 4, "fix_hours": 24, "label": "P1 — Immediate"},
    "High": {"response_hours": 8, "fix_hours": 72, "label": "P2 — Urgent"},
    "Medium": {"response_hours": 24, "fix_hours": 168, "label": "P3 — Standard"},
    "Low": {"response_hours": 72, "fix_hours": 720, "label": "P4 — Low"},
    "Info": {"response_hours": 168, "fix_hours": 2160, "label": "P5 — Informational"},
}


class RemediationTask:
    """A structured remediation task with owner, due date, and SLA."""
    _counter = 0

    def __init__(self, vuln: Dict, owner: str = "Unassigned"):
        RemediationTask._counter += 1
        self.task_id = f"TASK-{RemediationTask._counter:04d}"
        self.vuln_type = vuln.get('type', 'Unknown')
        self.severity = vuln.get('severity', 'Info')
        self.url = vuln.get('url', '')
        self.description = vuln.get('description', '')
        self.recommendation = vuln.get('recommendation', '')
        self.confidence = vuln.get('confidence', 0)
        self.owner = owner
        self.status = "open"
        self.created = datetime.now()

        sla = SLA_MAP.get(self.severity, SLA_MAP["Info"])
        self.priority = sla["label"]
        self.response_due = self.created + timedelta(hours=sla["response_hours"])
        self.fix_due = self.created + timedelta(hours=sla["fix_hours"])
        self.sla_hours = sla["fix_hours"]

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "vuln_type": self.vuln_type,
            "severity": self.severity,
            "priority": self.priority,
            "url": self.url,
            "description": self.description,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "owner": self.owner,
            "status": self.status,
            "created": self.created.isoformat(),
            "response_due": self.response_due.isoformat(),
            "fix_due": self.fix_due.isoformat(),
            "sla_hours": self.sla_hours,
        }


class SOCCopilot:
    """
    SOC Copilot that provides triage, incident summaries,
    containment steps, and structured remediation tasks.
    """

    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        self.tasks: List[RemediationTask] = []

    def triage(self, vulnerabilities: List[Dict], domain_info: Dict = None) -> Dict:
        """
        Main entry: Triage all findings and produce SOC-ready output.
        """
        if not vulnerabilities:
            return self._empty_result()

        # 1. Create prioritized task list
        self.tasks = self._create_tasks(vulnerabilities)

        # 2. Generate incident summary
        summary = self._generate_summary(vulnerabilities, domain_info)

        # 3. Generate containment steps
        containment = self._generate_containment(vulnerabilities)

        # 4. AI-enhanced triage if available
        ai_triage = None
        if self.orchestrator:
            ai_triage = self._ai_triage(vulnerabilities, domain_info)

        return {
            "timestamp": datetime.now().isoformat(),
            "domain": domain_info.get('domain', 'Unknown') if domain_info else 'Unknown',
            "incident_summary": summary,
            "containment_steps": containment,
            "tasks": [t.to_dict() for t in self.tasks],
            "task_count": len(self.tasks),
            "priority_breakdown": self._priority_breakdown(),
            "ai_triage": ai_triage,
            "sla_status": self._sla_status(),
        }

    def _empty_result(self) -> Dict:
        return {
            "timestamp": datetime.now().isoformat(),
            "incident_summary": "No vulnerabilities detected. System appears secure.",
            "containment_steps": [],
            "tasks": [],
            "task_count": 0,
            "priority_breakdown": {},
        }

    def _create_tasks(self, vulns: List[Dict]) -> List[RemediationTask]:
        tasks = []
        # Sort by severity priority
        sev_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3, 'Info': 4}
        sorted_vulns = sorted(vulns, key=lambda v: sev_order.get(v.get('severity', 'Info'), 5))

        for v in sorted_vulns:
            task = RemediationTask(v)
            tasks.append(task)
        return tasks

    def _generate_summary(self, vulns: List[Dict], domain_info: Dict) -> str:
        counts = {}
        for v in vulns:
            s = v.get('severity', 'Info')
            counts[s] = counts.get(s, 0) + 1

        domain = domain_info.get('domain', 'target') if domain_info else 'target'
        parts = [f"Security scan of {domain} identified {len(vulns)} findings."]

        if counts.get('Critical', 0):
            parts.append(f"🔴 {counts['Critical']} CRITICAL findings require immediate response (SLA: 4h).")
        if counts.get('High', 0):
            parts.append(f"🟠 {counts['High']} HIGH findings need urgent attention (SLA: 72h).")
        if counts.get('Medium', 0):
            parts.append(f"🟡 {counts['Medium']} MEDIUM findings for standard remediation.")
        if counts.get('Low', 0):
            parts.append(f"🟢 {counts['Low']} LOW findings for backlog.")

        return " ".join(parts)

    def _generate_containment(self, vulns: List[Dict]) -> List[Dict]:
        steps = []
        seen_types = set()

        for v in vulns:
            sev = v.get('severity', 'Info')
            vtype = v.get('type', 'Unknown')

            if sev in ('Critical', 'High') and vtype not in seen_types:
                seen_types.add(vtype)
                steps.append({
                    "priority": "IMMEDIATE" if sev == "Critical" else "URGENT",
                    "action": f"Contain {vtype} at {v.get('url', 'N/A')}",
                    "detail": v.get('recommendation', 'Apply vendor patch or WAF rule'),
                    "sla": SLA_MAP[sev]["label"],
                })

        if not steps:
            steps.append({
                "priority": "ROUTINE",
                "action": "No immediate containment needed",
                "detail": "All findings are Medium/Low severity — schedule for next sprint",
                "sla": "P3 — Standard",
            })

        return steps

    def _ai_triage(self, vulns: List[Dict], domain_info: Dict) -> Optional[str]:
        vuln_summary = "\n".join([
            f"- {v.get('type')} [{v.get('severity')}] at {v.get('url', '')[:50]}"
            for v in vulns[:8]
        ])

        prompt = f"""You are a SOC analyst. Provide a plain-language incident triage for:

Domain: {domain_info.get('domain', 'unknown') if domain_info else 'unknown'}
Findings:
{vuln_summary}

Output:
1. Executive summary (2 sentences)
2. Top 3 containment priorities
3. Recommended response team assignments

Be concise and actionable."""

        try:
            return self.orchestrator._call_groq(prompt, temperature=0.2, max_tokens=500)
        except Exception:
            return None

    def _priority_breakdown(self) -> Dict:
        breakdown = {}
        for t in self.tasks:
            p = t.priority
            breakdown[p] = breakdown.get(p, 0) + 1
        return breakdown

    def _sla_status(self) -> Dict:
        now = datetime.now()
        overdue = sum(1 for t in self.tasks if t.status == "open" and t.response_due < now)
        return {
            "total_tasks": len(self.tasks),
            "overdue": overdue,
            "on_track": len(self.tasks) - overdue,
        }
