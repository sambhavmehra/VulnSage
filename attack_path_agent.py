"""
Attack Path Agent
Correlates findings across subdomains/pages, identifies exploit chains,
outputs attack graphs with chain confidence and business impact.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional


class AttackNode:
    """Represents a single step in an attack path."""
    def __init__(self, vuln: Dict, step_number: int):
        self.id = f"node_{step_number}"
        self.step = step_number
        self.vuln_type = vuln.get('type', 'Unknown')
        self.severity = vuln.get('severity', 'Info')
        self.url = vuln.get('url', '')
        self.description = vuln.get('description', '')
        self.confidence = vuln.get('confidence', 0)
        self.subdomain = self._extract_subdomain(self.url)

    def _extract_subdomain(self, url: str) -> str:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.hostname or url
        except Exception:
            return url

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "step": self.step,
            "type": self.vuln_type,
            "severity": self.severity,
            "url": self.url,
            "subdomain": self.subdomain,
            "confidence": self.confidence,
            "description": self.description,
        }


class AttackChain:
    """Represents a complete exploit chain."""
    def __init__(self, chain_id: str):
        self.id = chain_id
        self.nodes: List[AttackNode] = []
        self.chain_confidence = 0.0
        self.business_impact = "Unknown"
        self.impact_score = 0
        self.attack_vector = ""
        self.prerequisites = []
        self.mitigations = []

    def add_node(self, node: AttackNode):
        self.nodes.append(node)

    def calculate_confidence(self):
        if not self.nodes:
            self.chain_confidence = 0
            return
        confidences = [n.confidence for n in self.nodes]
        # Chain confidence = product of individual confidences (weakest link)
        product = 1.0
        for c in confidences:
            product *= (c / 100.0)
        self.chain_confidence = round(product * 100, 1)

    def to_dict(self) -> Dict:
        return {
            "chain_id": self.id,
            "nodes": [n.to_dict() for n in self.nodes],
            "chain_confidence": self.chain_confidence,
            "business_impact": self.business_impact,
            "impact_score": self.impact_score,
            "attack_vector": self.attack_vector,
            "prerequisites": self.prerequisites,
            "mitigations": self.mitigations,
            "chain_length": len(self.nodes),
        }


# Common exploit chain patterns
CHAIN_PATTERNS = [
    {
        "name": "Info Disclosure → SQLi → Data Breach",
        "pattern": ["Information Disclosure", "SQL Injection"],
        "impact": "Critical — Full database compromise via info leak + SQLi",
        "score": 95,
        "vector": "Network",
    },
    {
        "name": "XSS → Session Hijack → Account Takeover",
        "pattern": ["XSS", "Missing Security Headers"],
        "impact": "High — User session theft via XSS + weak headers",
        "score": 85,
        "vector": "Client-side",
    },
    {
        "name": "CSRF → State Mutation → Privilege Escalation",
        "pattern": ["CSRF", "Missing Security Headers"],
        "impact": "High — Unauthorized actions via CSRF exploitation",
        "score": 80,
        "vector": "Client-side",
    },
    {
        "name": "Open Redirect → Phishing → Credential Theft",
        "pattern": ["Open Redirect"],
        "impact": "Medium — Credential phishing via trusted domain",
        "score": 65,
        "vector": "Social Engineering",
    },
    {
        "name": "Insecure Transport → MitM → Data Interception",
        "pattern": ["Insecure", "HTTP"],
        "impact": "High — Data interception via unencrypted transport",
        "score": 75,
        "vector": "Network",
    },
    {
        "name": "Server Info Leak → Targeted Exploit",
        "pattern": ["Server", "Version"],
        "impact": "Medium — Targeted attacks using disclosed server info",
        "score": 60,
        "vector": "Network",
    },
]


class AttackPathAgent:
    """
    Correlates findings across subdomains/pages and identifies exploit chains.
    Uses rule-based pattern matching + AI for attack graph generation.
    """

    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        self.chains: List[AttackChain] = []
        self.attack_graph = {}

    def analyze(self, vulnerabilities: List[Dict], domain_info: Dict = None) -> Dict:
        """
        Main entry: Analyze all vulnerabilities and produce attack paths.
        Returns attack graph with chains, impact, and recommendations.
        """
        if not vulnerabilities:
            return self._empty_result()

        # 1. Group vulnerabilities by subdomain
        subdomain_groups = self._group_by_subdomain(vulnerabilities)

        # 2. Identify exploit chains using pattern matching
        self.chains = self._find_chains(vulnerabilities)

        # 3. Build attack graph
        self.attack_graph = self._build_graph(vulnerabilities, subdomain_groups)

        # 4. AI-enhanced analysis if orchestrator available
        ai_analysis = None
        if self.orchestrator:
            ai_analysis = self._ai_correlate(vulnerabilities, domain_info)

        # 5. Compile results
        result = {
            "timestamp": datetime.now().isoformat(),
            "domain": domain_info.get('domain', 'Unknown') if domain_info else 'Unknown',
            "total_vulnerabilities": len(vulnerabilities),
            "attack_chains": [c.to_dict() for c in self.chains],
            "attack_chains_count": len(self.chains),
            "attack_graph": self.attack_graph,
            "critical_paths": [c.to_dict() for c in self.chains if c.impact_score >= 80],
            "risk_summary": self._risk_summary(vulnerabilities),
            "ai_analysis": ai_analysis,
            "recommendations": self._generate_recommendations(),
        }
        return result

    def _empty_result(self) -> Dict:
        return {
            "timestamp": datetime.now().isoformat(),
            "total_vulnerabilities": 0,
            "attack_chains": [],
            "attack_chains_count": 0,
            "attack_graph": {},
            "critical_paths": [],
            "risk_summary": {"overall_risk": "None", "score": 0},
            "recommendations": [],
        }

    def _group_by_subdomain(self, vulns: List[Dict]) -> Dict[str, List[Dict]]:
        groups = {}
        for v in vulns:
            url = v.get('url', '')
            try:
                from urllib.parse import urlparse
                host = urlparse(url).hostname or 'unknown'
            except Exception:
                host = 'unknown'
            groups.setdefault(host, []).append(v)
        return groups

    def _find_chains(self, vulns: List[Dict]) -> List[AttackChain]:
        chains = []
        vuln_types = [v.get('type', '').lower() for v in vulns]
        vuln_type_str = ' '.join(vuln_types)

        for idx, pattern in enumerate(CHAIN_PATTERNS):
            # Check if all pattern keywords exist in findings
            matched = all(
                any(kw.lower() in vt for vt in vuln_types)
                for kw in pattern["pattern"]
            )
            if matched:
                chain = AttackChain(f"chain_{idx + 1}")
                chain.attack_vector = pattern["vector"]
                chain.business_impact = pattern["impact"]
                chain.impact_score = pattern["score"]

                # Find matching vulns for each pattern keyword
                step = 1
                for kw in pattern["pattern"]:
                    for v in vulns:
                        if kw.lower() in v.get('type', '').lower():
                            chain.add_node(AttackNode(v, step))
                            step += 1
                            break

                chain.calculate_confidence()
                chain.mitigations = [
                    f"Fix: {n.vuln_type} at {n.url}" for n in chain.nodes
                ]
                chains.append(chain)

        # Sort by impact score
        chains.sort(key=lambda c: c.impact_score, reverse=True)
        return chains

    def _build_graph(self, vulns: List[Dict], groups: Dict) -> Dict:
        nodes = []
        edges = []

        # Create nodes for each vulnerability
        for i, v in enumerate(vulns):
            nodes.append({
                "id": f"v{i}",
                "label": v.get('type', 'Unknown'),
                "severity": v.get('severity', 'Info'),
                "url": v.get('url', ''),
            })

        # Create edges between related vulns (same subdomain or chained)
        for i, v1 in enumerate(vulns):
            for j, v2 in enumerate(vulns):
                if i >= j:
                    continue
                # Same subdomain = potential lateral movement
                try:
                    from urllib.parse import urlparse
                    h1 = urlparse(v1.get('url', '')).hostname
                    h2 = urlparse(v2.get('url', '')).hostname
                    if h1 and h2 and h1 == h2:
                        edges.append({
                            "from": f"v{i}", "to": f"v{j}",
                            "type": "same_host", "label": "lateral"
                        })
                except Exception:
                    pass

        return {
            "nodes": nodes[:50],  # cap for performance
            "edges": edges[:100],
            "subdomains_affected": list(groups.keys()),
            "subdomains_count": len(groups),
        }

    def _ai_correlate(self, vulns: List[Dict], domain_info: Dict) -> Optional[str]:
        vuln_summary = json.dumps([
            {"type": v.get('type'), "severity": v.get('severity'),
             "url": v.get('url'), "confidence": v.get('confidence')}
            for v in vulns[:10]
        ], indent=2)

        prompt = f"""Analyze these vulnerability findings and identify non-obvious attack paths and exploit chains:

DOMAIN: {domain_info.get('domain', 'Unknown') if domain_info else 'Unknown'}
FINDINGS:
{vuln_summary}

Provide:
1. Correlated attack paths an attacker would likely follow
2. Business impact of each path
3. Priority order for remediation
4. Any chained exploits that combine multiple findings

Be concise and actionable (5-8 sentences)."""

        try:
            return self.orchestrator._call_groq(prompt, temperature=0.2, max_tokens=600)
        except Exception:
            return None

    def _risk_summary(self, vulns: List[Dict]) -> Dict:
        sev_weights = {'Critical': 10, 'High': 7, 'Medium': 4, 'Low': 1, 'Info': 0}
        total_score = sum(sev_weights.get(v.get('severity', 'Info'), 0) for v in vulns)
        max_possible = len(vulns) * 10 if vulns else 1

        risk_pct = min(100, round((total_score / max_possible) * 100))
        if risk_pct >= 70:
            level = "Critical"
        elif risk_pct >= 50:
            level = "High"
        elif risk_pct >= 25:
            level = "Medium"
        else:
            level = "Low"

        return {"overall_risk": level, "score": risk_pct, "raw_score": total_score}

    def _generate_recommendations(self) -> List[str]:
        recs = []
        for chain in self.chains:
            if chain.impact_score >= 80:
                recs.append(f"🔴 CRITICAL: Break chain '{chain.id}' — fix {chain.nodes[0].vuln_type} first")
            elif chain.impact_score >= 60:
                recs.append(f"🟠 HIGH: Address chain '{chain.id}' — {chain.business_impact}")
        if not recs:
            recs.append("✅ No critical attack chains detected.")
        return recs
