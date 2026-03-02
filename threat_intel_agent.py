"""
Threat Intelligence Agent
Collects latest public vulnerability intelligence from trusted feeds.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import requests


class ThreatIntelAgent:
    """Fetch and normalize recent vulnerability intelligence."""

    NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

    def __init__(self, cache_path: str = "data/latest_bugs.json", timeout: int = 20):
        self.cache_path = cache_path
        self.timeout = timeout
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    def collect_latest_bugs(self, max_items: int = 200, days: int = 30) -> Dict[str, Any]:
        nvd_items = self._fetch_nvd_recent(max_items=max_items, days=days)
        kev_items = self._fetch_cisa_kev(max_items=max_items)

        merged = {}
        for item in nvd_items + kev_items:
            key = item.get("id") or f"{item.get('source')}::{item.get('title', '')[:60]}"
            if key not in merged:
                merged[key] = item

        items = sorted(
            merged.values(),
            key=lambda x: x.get("published", ""),
            reverse=True,
        )[:max_items]

        payload = {
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "total_items": len(items),
            "sources": {
                "nvd": len(nvd_items),
                "cisa_kev": len(kev_items),
            },
            "items": items,
        }
        self._save_cache(payload)
        return payload

    def load_cached_bugs(self) -> Dict[str, Any]:
        if not os.path.exists(self.cache_path):
            return {"collected_at": None, "total_items": 0, "sources": {}, "items": []}
        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"collected_at": None, "total_items": 0, "sources": {}, "items": []}

    def _fetch_nvd_recent(self, max_items: int, days: int) -> List[Dict[str, Any]]:
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)
        results_per_page = min(200, max_items)
        start_index = 0
        all_items: List[Dict[str, Any]] = []

        while len(all_items) < max_items:
            params = {
                "pubStartDate": start.isoformat().replace("+00:00", "Z"),
                "pubEndDate": end.isoformat().replace("+00:00", "Z"),
                "resultsPerPage": results_per_page,
                "startIndex": start_index,
            }
            try:
                res = requests.get(self.NVD_API_URL, params=params, timeout=self.timeout)
                res.raise_for_status()
                data = res.json()
            except Exception:
                break

            vulns = data.get("vulnerabilities", [])
            if not vulns:
                break

            for entry in vulns:
                cve = entry.get("cve", {})
                cve_id = cve.get("id", "N/A")
                descriptions = cve.get("descriptions", [])
                desc = self._pick_english_text(descriptions, "value")
                metrics = cve.get("metrics", {})
                severity = self._extract_cvss_severity(metrics)
                score = self._extract_cvss_score(metrics)
                weaknesses = cve.get("weaknesses", [])
                cwe_id = self._extract_cwe_id(weaknesses)

                all_items.append(
                    {
                        "id": cve_id,
                        "source": "NVD",
                        "title": cve_id,
                        "description": desc,
                        "severity": severity,
                        "cvss_score": score,
                        "cwe_id": cwe_id,
                        "published": cve.get("published", ""),
                        "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                        "known_exploited": False,
                    }
                )
                if len(all_items) >= max_items:
                    break

            if len(vulns) < results_per_page:
                break
            start_index += results_per_page

        return all_items

    def _fetch_cisa_kev(self, max_items: int) -> List[Dict[str, Any]]:
        try:
            res = requests.get(self.CISA_KEV_URL, timeout=self.timeout)
            res.raise_for_status()
            data = res.json()
        except Exception:
            return []

        vulns = data.get("vulnerabilities", [])[:max_items]
        items: List[Dict[str, Any]] = []
        for v in vulns:
            cve_id = v.get("cveID", "N/A")
            title = v.get("vulnerabilityName", cve_id)
            desc = v.get("shortDescription", "")
            vendor = v.get("vendorProject", "")
            product = v.get("product", "")
            due_date = v.get("dueDate", "")
            known_ransomware = v.get("knownRansomwareCampaignUse", "")

            items.append(
                {
                    "id": cve_id,
                    "source": "CISA_KEV",
                    "title": title,
                    "description": f"{desc} Vendor: {vendor}. Product: {product}.",
                    "severity": "High",
                    "cvss_score": None,
                    "cwe_id": None,
                    "published": v.get("dateAdded", ""),
                    "url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
                    "known_exploited": True,
                    "kev_due_date": due_date,
                    "known_ransomware_campaign_use": known_ransomware,
                }
            )
        return items

    def _pick_english_text(self, items: List[Dict[str, Any]], value_key: str) -> str:
        for item in items:
            if item.get("lang") == "en":
                return item.get(value_key, "")
        return items[0].get(value_key, "") if items else ""

    def _extract_cvss_severity(self, metrics: Dict[str, Any]) -> str:
        for version_key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
            records = metrics.get(version_key, [])
            if records:
                severity = records[0].get("cvssData", {}).get("baseSeverity")
                if severity:
                    return str(severity).title()
        return "Medium"

    def _extract_cvss_score(self, metrics: Dict[str, Any]) -> Any:
        for version_key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
            records = metrics.get(version_key, [])
            if records:
                score = records[0].get("cvssData", {}).get("baseScore")
                if score is not None:
                    return score
        return None

    def _extract_cwe_id(self, weaknesses: List[Dict[str, Any]]) -> str | None:
        for weakness in weaknesses:
            for desc in weakness.get("description", []):
                val = desc.get("value", "")
                if val.startswith("CWE-"):
                    return val
        return None

    def _save_cache(self, payload: Dict[str, Any]) -> None:
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
