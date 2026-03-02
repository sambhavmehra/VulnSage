"""
Reports Database Module
Handles persistent storage and retrieval of scan reports
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class ReportsDB:
    """
    Manages persistent storage of scan reports
    """
    
    REPORTS_DIR = "data/reports"
    
    def __init__(self, reports_dir: str = REPORTS_DIR):
        self.reports_dir = reports_dir
        self._ensure_directory()
        self._init_index()
    
    def _ensure_directory(self):
        """Create reports directory if it doesn't exist"""
        Path(self.reports_dir).mkdir(parents=True, exist_ok=True)
    
    def _init_index(self):
        """Initialize or load the reports index"""
        self.index_path = os.path.join(self.reports_dir, "index.json")
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.index = {"reports": [], "last_updated": None}
        else:
            self.index = {"reports": [], "last_updated": None}
    
    def _save_index(self):
        """Save the reports index"""
        self.index["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(self.index, f, indent=2, default=str)
            return True
        except IOError as e:
            print(f"[ERROR] Failed to save reports index: {e}")
            return False
    
    def save_report(self, report_data: Dict[str, Any], domain: str, username: str = "unknown") -> Optional[str]:
        """
        Save a scan report to persistent storage
        
        Args:
            report_data: The complete report data
            domain: Target domain that was scanned
            username: User who initiated the scan
            
        Returns:
            Report ID if successful, None otherwise
        """
        try:
            # Generate unique report ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_id = f"scan_{timestamp}"
            
            # Prepare report metadata
            vulnerabilities = report_data.get('json_report', {}).get('vulnerabilities', [])
            severity_breakdown = report_data.get('json_report', {}).get('summary', {}).get('severity_breakdown', {})
            
            # Create report entry
            report_entry = {
                "id": report_id,
                "domain": domain,
                "scan_date": datetime.now().isoformat(),
                "username": username,
                "subdomains_count": report_data.get('json_report', {}).get('summary', {}).get('subdomains_scanned', 0),
                "vulnerabilities_count": len(vulnerabilities),
                "critical_count": severity_breakdown.get('Critical', 0),
                "high_count": severity_breakdown.get('High', 0),
                "medium_count": severity_breakdown.get('Medium', 0),
                "low_count": severity_breakdown.get('Low', 0),
                "file_path": f"{report_id}.json"
            }
            
            # Save full report data
            full_report = {
                "metadata": {
                    "report_id": report_id,
                    "scan_date": datetime.now().isoformat(),
                    "domain": domain,
                    "username": username,
                },
                "domain_info": report_data.get('json_report', {}).get('domain_analysis', {}),
                "subdomains": report_data.get('json_report', {}).get('subdomains', []),
                "vulnerabilities": vulnerabilities,
                "summary": report_data.get('json_report', {}).get('summary', {}),
                "executive_summary": report_data.get('executive_summary', ''),
                "markdown_report": report_data.get('markdown_report', '')
            }
            
            # Write report file
            report_path = os.path.join(self.reports_dir, f"{report_id}.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(full_report, f, indent=2, default=str)
            
            # Update index
            self.index["reports"].append(report_entry)
            self._save_index()
            
            print(f"[+] Report saved: {report_id} for domain {domain}")
            return report_id
            
        except Exception as e:
            print(f"[ERROR] Failed to save report: {e}")
            return None

    def save_pentest_report(self, pentest_data: Dict[str, Any], target_url: str, username: str = "unknown") -> Optional[str]:
        """
        Save an agentic pentest report to persistent storage.

        Args:
            pentest_data: Agentic pentest result payload
            target_url: Target URL tested
            username: User who initiated the pentest

        Returns:
            Report ID if successful, None otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_id = f"pentest_{timestamp}"
            summary = pentest_data.get("summary", {})
            findings = pentest_data.get("findings", [])

            report_entry = {
                "id": report_id,
                "domain": target_url,
                "scan_date": datetime.now().isoformat(),
                "username": username,
                "subdomains_count": 0,
                "vulnerabilities_count": int(summary.get("total_findings", len(findings))),
                "critical_count": sum(1 for f in findings if str(f.get("severity", "")).lower() == "critical"),
                "high_count": sum(1 for f in findings if str(f.get("severity", "")).lower() == "high"),
                "medium_count": sum(1 for f in findings if str(f.get("severity", "")).lower() == "medium"),
                "low_count": sum(1 for f in findings if str(f.get("severity", "")).lower() == "low"),
                "file_path": f"{report_id}.json",
                "report_type": "agentic_pentest",
            }

            full_report = {
                "metadata": {
                    "report_id": report_id,
                    "report_type": "agentic_pentest",
                    "scan_date": datetime.now().isoformat(),
                    "target_url": target_url,
                    "username": username,
                },
                "summary": summary,
                "findings": findings,
                "agentic_analysis": pentest_data.get("agentic_analysis"),
                "attack_paths": pentest_data.get("attack_paths"),
                "remediation_fixes": pentest_data.get("remediation_fixes"),
                "threat_intel": pentest_data.get("threat_intel"),
                "raw": pentest_data,
            }

            report_path = os.path.join(self.reports_dir, f"{report_id}.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(full_report, f, indent=2, default=str)

            self.index["reports"].append(report_entry)
            self._save_index()
            print(f"[+] Pentest report saved: {report_id} for target {target_url}")
            return report_id

        except Exception as e:
            print(f"[ERROR] Failed to save pentest report: {e}")
            return None
    
    def get_all_reports(self) -> List[Dict[str, Any]]:
        """
        Get all reports from storage
        
        Returns:
            List of report metadata
        """
        return sorted(
            self.index.get("reports", []),
            key=lambda x: x.get("scan_date", ""),
            reverse=True
        )
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific report by ID
        
        Args:
            report_id: The report ID to retrieve
            
        Returns:
            Full report data or None if not found
        """
        try:
            report_path = os.path.join(self.reports_dir, f"{report_id}.json")
            if not os.path.exists(report_path):
                return None
            
            with open(report_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"[ERROR] Failed to load report {report_id}: {e}")
            return None
    
    def get_report_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get all reports for a specific domain
        
        Args:
            domain: Domain to filter by
            
        Returns:
            List of reports for the domain
        """
        return [
            r for r in self.get_all_reports()
            if domain.lower() in r.get("domain", "").lower()
        ]
    
    def delete_report(self, report_id: str) -> bool:
        """
        Delete a report from storage
        
        Args:
            report_id: Report ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            report_path = os.path.join(self.reports_dir, f"{report_id}.json")
            
            # Remove report file
            if os.path.exists(report_path):
                os.remove(report_path)
            
            # Remove from index
            self.index["reports"] = [
                r for r in self.index.get("reports", [])
                if r.get("id") != report_id
            ]
            self._save_index()
            
            print(f"[+] Report deleted: {report_id}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to delete report {report_id}: {e}")
            return False
    
    def search_reports(self, query: str) -> List[Dict[str, Any]]:
        """
        Search reports by domain or other fields
        
        Args:
            query: Search query
            
        Returns:
            List of matching reports
        """
        query_lower = query.lower()
        return [
            r for r in self.get_all_reports()
            if query_lower in r.get("domain", "").lower()
            or query_lower in r.get("username", "").lower()
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics about saved reports
        
        Returns:
            Dictionary with statistics
        """
        reports = self.get_all_reports()
        
        if not reports:
            return {
                "total_scans": 0,
                "total_domains": 0,
                "total_vulnerabilities": 0,
                "critical_vulnerabilities": 0,
                "high_vulnerabilities": 0,
                "average_vulns_per_scan": 0,
                "last_scan": None
            }
        
        total_vulns = sum(r.get("vulnerabilities_count", 0) for r in reports)
        critical_vulns = sum(r.get("critical_count", 0) for r in reports)
        high_vulns = sum(r.get("high_count", 0) for r in reports)
        domains = set(r.get("domain", "") for r in reports)
        
        return {
            "total_scans": len(reports),
            "total_domains": len(domains),
            "total_vulnerabilities": total_vulns,
            "critical_vulnerabilities": critical_vulns,
            "high_vulnerabilities": high_vulns,
            "average_vulns_per_scan": round(total_vulns / len(reports), 2) if reports else 0,
            "last_scan": reports[0].get("scan_date") if reports else None
        }
    
    def export_report(self, report_id: str, format: str = "json") -> Optional[Dict[str, Any]]:
        """
        Export a report in specified format
        
        Args:
            report_id: Report to export
            format: Export format (json, markdown, csv)
            
        Returns:
            Exported data as dictionary
        """
        report = self.get_report(report_id)
        if not report:
            return None
        
        if format == "json":
            return report
        
        elif format == "markdown":
            return {"content": report.get("markdown_report", ""), "filename": f"{report_id}.md"}
        
        elif format == "csv":
            # Convert vulnerabilities to CSV format
            vulns = report.get("vulnerabilities", [])
            if not vulns:
                return {"content": "", "filename": f"{report_id}.csv"}
            
            csv_lines = ["URL,Type,Severity,Confidence,Description"]
            for v in vulns:
                url = v.get("url", "").replace('"', '""')
                vuln_type = v.get("type", "").replace('"', '""')
                severity = v.get("severity", "").replace('"', '""')
                confidence = str(v.get("confidence", "")).replace('"', '""')
                desc = v.get("description", "").replace('"', '""')
                csv_lines.append(f'"{url}","{vuln_type}","{severity}","{confidence}","{desc}"')
            
            return {"content": "\n".join(csv_lines), "filename": f"{report_id}.csv"}
        
        return None


# Singleton instance
_reports_db = None

def get_reports_db() -> ReportsDB:
    """Get singleton instance of ReportsDB"""
    global _reports_db
    if _reports_db is None:
        _reports_db = ReportsDB()
    return _reports_db
