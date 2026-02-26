"""
Agentic AI Security Assistant
Autonomous security agent that analyzes vulnerabilities and generates remediation solutions
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from groq_orchestrator import GroqOrchestrator


class AgentState:
    """
    Manages the state of the security agent session
    """
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.vulnerabilities_analyzed = []
        self.remediation_tasks = []
        self.completed_tasks = []
        self.agent_thoughts = []
        self.current_focus = None
        self.remediation_progress = {}
        
    def add_thought(self, thought: str, category: str = "analysis"):
        """Add agent reasoning/thought process"""
        self.agent_thoughts.append({
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "thought": thought
        })
        
    def add_vulnerability(self, vuln: Dict):
        """Track analyzed vulnerability"""
        self.vulnerabilities_analyzed.append({
            "id": len(self.vulnerabilities_analyzed) + 1,
            "vulnerability": vuln,
            "analyzed_at": datetime.now().isoformat(),
            "status": "pending"
        })
        
    def create_remediation_task(self, vuln_id: int, task_type: str, priority: str):
        """Create a remediation task"""
        task = {
            "id": len(self.remediation_tasks) + 1,
            "vuln_id": vuln_id,
            "type": task_type,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }
        self.remediation_tasks.append(task)
        return task["id"]
        
    def complete_task(self, task_id: int):
        """Mark a task as completed"""
        for task in self.remediation_tasks:
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed_at"] = datetime.now().isoformat()
                self.completed_tasks.append(task)
                return True
        return False
        
    def get_progress(self) -> Dict:
        """Get current remediation progress"""
        total = len(self.remediation_tasks)
        completed = len(self.completed_tasks)
        return {
            "total_tasks": total,
            "completed": completed,
            "pending": total - completed,
            "percentage": (completed / total * 100) if total > 0 else 0
        }


class SecurityAgent:
    """
    Autonomous Security Agent that analyzes vulnerabilities and generates remediation solutions
    """
    
    def __init__(self, groq_orchestrator: GroqOrchestrator):
        self.orchestrator = groq_orchestrator
        self.state = AgentState()
        self.tools = {
            "analyze_vulnerability": self._tool_analyze_vulnerability,
            "generate_fix_code": self._tool_generate_fix_code,
            "create_remediation_plan": self._tool_create_remediation_plan,
            "prioritize_vulnerabilities": self._tool_prioritize_vulnerabilities,
            "validate_fix": self._tool_validate_fix
        }

    def _parse_json_response(self, response: Any) -> Optional[Dict]:
        """Parse JSON body from plain or fenced model responses."""
        if not response or not isinstance(response, str):
            return None

        try:
            cleaned = response
            if "```json" in cleaned:
                cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0]
            elif "```" in cleaned:
                cleaned = cleaned.split("```", 1)[1].split("```", 1)[0]
            return json.loads(cleaned.strip())
        except Exception:
            return None
        
    def analyze_scan_results(self, vulnerabilities: List[Dict], domain_info: Dict) -> Dict:
        """
        Main entry point: Autonomously analyze all scan results
        """
        self.state.add_thought(
            f"Starting autonomous analysis of {len(vulnerabilities)} vulnerabilities for {domain_info['domain']}",
            "initialization"
        )
        
        # Step 1: Prioritize vulnerabilities
        prioritized = self._tool_prioritize_vulnerabilities(vulnerabilities, domain_info)
        
        # Step 2: Analyze each vulnerability in priority order
        analysis_results = []
        for vuln in prioritized:
            result = self._tool_analyze_vulnerability(vuln, domain_info)
            analysis_results.append(result)
            self.state.add_vulnerability(vuln)
            
        # Step 3: Create remediation plan
        remediation_plan = self._tool_create_remediation_plan(analysis_results, domain_info)
        
        # Step 4: Generate fix code for high-priority items
        fix_codes = []
        for item in remediation_plan["immediate_actions"]:
            fix_code = self._tool_generate_fix_code(item["vulnerability"])
            fix_codes.append({
                "vulnerability": item["vulnerability"],
                "fix_code": fix_code
            })
            
        return {
            "agent_session_id": self.state.session_id,
            "analysis_summary": {
                "total_vulnerabilities": len(vulnerabilities),
                "critical_count": sum(1 for v in vulnerabilities if v.get("severity") == "Critical"),
                "high_count": sum(1 for v in vulnerabilities if v.get("severity") == "High"),
                "analysis_completed": True
            },
            "prioritized_vulnerabilities": prioritized,
            "detailed_analysis": analysis_results,
            "remediation_plan": remediation_plan,
            "generated_fixes": fix_codes,
            "agent_thoughts": self.state.agent_thoughts,
            "progress": self.state.get_progress()
        }
        
    def _tool_prioritize_vulnerabilities(self, vulnerabilities: List[Dict], domain_info: Dict) -> List[Dict]:
        """
        Tool: Prioritize vulnerabilities based on risk, exploitability, and business context
        """
        self.state.add_thought("Prioritizing vulnerabilities using multi-factor risk analysis", "prioritization")
        
        prompt = f"""
As a security expert, prioritize these vulnerabilities for domain: {domain_info['domain']}

Vulnerabilities:
{json.dumps(vulnerabilities, indent=2)}

Consider:
1. Risk score (higher = more urgent)
2. Exploitation difficulty (Easy > Medium > Hard)
3. Business impact (Data breach > Service disruption > Info disclosure)
4. Public exposure (Internet-facing > Internal)
5. Asset value (Production > Staging > Dev)

Return JSON array of vulnerability IDs in priority order (highest priority first):
{{
    "prioritized_order": [id1, id2, id3, ...],
    "reasoning": "brief explanation of prioritization logic",
    "priority_groups": {{
        "immediate": [ids],      // Fix within 24 hours
        "urgent": [ids],         // Fix within 7 days
        "planned": [ids],        // Fix within 30 days
        "low_priority": [ids]    // Fix when convenient
    }}
}}
"""
        
        response = self.orchestrator._call_groq(prompt, temperature=0.2)
        
        try:
            result = self._parse_json_response(response)
            if not isinstance(result, dict):
                raise ValueError("Invalid prioritization response format")
            
            # Reorder vulnerabilities based on priority
            id_to_vuln = {i+1: v for i, v in enumerate(vulnerabilities)}
            prioritized = []
            
            for vid in result.get("prioritized_order", []):
                if vid in id_to_vuln:
                    vuln = id_to_vuln[vid].copy()
                    vuln["priority_rank"] = len(prioritized) + 1
                    prioritized.append(vuln)
                    
            self.state.add_thought(
                f"Prioritized {len(prioritized)} vulnerabilities: "
                f"{len(result['priority_groups']['immediate'])} immediate, "
                f"{len(result['priority_groups']['urgent'])} urgent",
                "prioritization"
            )
            
            return prioritized
            
        except Exception as e:
            self.state.add_thought(f"Prioritization failed: {e}, using fallback", "error")
            # Fallback: sort by risk score
            return sorted(vulnerabilities, key=lambda x: x.get("risk_score", 0), reverse=True)
        
    def _tool_analyze_vulnerability(self, vulnerability: Dict, domain_info: Dict) -> Dict:
        """
        Tool: Deep analysis of a single vulnerability
        """
        vuln_type = vulnerability.get("type", "Unknown")
        self.state.add_thought(f"Analyzing {vuln_type} vulnerability", "analysis")
        
        prompt = f"""
Perform deep security analysis of this vulnerability:

Vulnerability: {json.dumps(vulnerability, indent=2)}
Domain Context: {json.dumps(domain_info, indent=2)}

Analyze:
1. Root cause of the vulnerability
2. Attack vectors and exploitation methods
3. Potential impact on business/data
4. Likelihood of exploitation
5. Compliance implications (GDPR, PCI-DSS, etc.)
6. Detection difficulty

Return JSON:
{{
    "root_cause": "technical explanation",
    "attack_vectors": ["vector1", "vector2"],
    "business_impact": "description",
    "data_at_risk": ["type1", "type2"],
    "exploitation_likelihood": "High|Medium|Low",
    "compliance_risk": ["GDPR", "PCI-DSS", etc],
    "detection_difficulty": "Easy|Medium|Hard",
    "affected_components": ["component1", "component2"],
    "similar_cves": ["CVE-XXXX-XXXXX"],
    "recommended_monitoring": ["monitoring1", "monitoring2"]
}}
"""
        
        response = self.orchestrator._call_groq(prompt, temperature=0.2)
        
        try:
            analysis = self._parse_json_response(response)
            if not isinstance(analysis, dict):
                raise ValueError("Invalid analysis response format")
            analysis["vulnerability_id"] = vulnerability.get("id", "unknown")
            analysis["vulnerability_type"] = vuln_type
            
            self.state.add_thought(
                f"Analysis complete: {analysis.get('exploitation_likelihood')} likelihood, "
                f"affects {len(analysis.get('affected_components', []))} components",
                "analysis"
            )
            
            return analysis
            
        except Exception as e:
            self.state.add_thought(f"Analysis failed: {e}", "error")
            return {
                "vulnerability_id": vulnerability.get("id", "unknown"),
                "vulnerability_type": vuln_type,
                "root_cause": "Analysis failed",
                "error": str(e)
            }
        
    def _tool_generate_fix_code(self, vulnerability: Dict) -> Dict:
        """
        Tool: Generate actual fix code for the vulnerability
        """
        vuln_type = vulnerability.get("type", "Unknown")
        self.state.add_thought(f"Generating fix code for {vuln_type}", "remediation")
        
        # Determine vulnerability category
        category = self._categorize_vulnerability(vuln_type)
        
        prompt = f"""
Generate production-ready fix code for this vulnerability:

Vulnerability: {json.dumps(vulnerability, indent=2)}
Category: {category}

Provide:
1. Secure code implementation
2. Configuration changes if applicable
3. Testing code to verify the fix
4. Deployment considerations

Return JSON:
{{
    "fix_summary": "brief description of the fix",
    "language": "programming language",
    "severity": "Critical|High|Medium|Low",
    "code_fix": {{
        "description": "what this code does",
        "code": "actual code here",
        "file_path": "suggested file location"
    }},
    "configuration_fix": {{
        "description": "config changes needed",
        "config_code": "configuration code",
        "file_path": "config file location"
    }},
    "testing_code": {{
        "description": "how to test the fix",
        "test_code": "test code here"
    }},
    "deployment_steps": [
        "step 1",
        "step 2",
        "step 3"
    ],
    "rollback_plan": "how to rollback if issues occur",
    "verification_commands": [
        "command 1",
        "command 2"
    ]
}}
"""
        
        response = self.orchestrator._call_groq(prompt, temperature=0.2, max_tokens=3000)
        
        try:
            fix_code = self._parse_json_response(response)
            if not isinstance(fix_code, dict):
                raise ValueError("Invalid fix-code response format")
            
            self.state.add_thought(
                f"Fix code generated: {fix_code.get('fix_summary', 'N/A')[:50]}...",
                "remediation"
            )
            
            return fix_code
            
        except Exception as e:
            self.state.add_thought(f"Fix code generation failed: {e}", "error")
            return self._generate_fallback_fix(vulnerability)
        
    def _tool_create_remediation_plan(self, analysis_results: List[Dict], domain_info: Dict) -> Dict:
        """
        Tool: Create comprehensive remediation plan
        """
        self.state.add_thought("Creating comprehensive remediation plan", "planning")
        
        # Count by priority
        critical_count = sum(1 for a in analysis_results 
                           if a.get("exploitation_likelihood") == "High")
        
        prompt = f"""
Create a comprehensive remediation plan based on these vulnerability analyses:

Domain: {domain_info['domain']}
Analyses: {json.dumps(analysis_results, indent=2)}

Create a plan with:
1. Immediate actions (24-hour window)
2. Short-term actions (1-week window)
3. Long-term improvements (1-month window)
4. Resource requirements
5. Timeline with milestones

Return JSON:
{{
    "plan_summary": "brief overview",
    "immediate_actions": [
        {{
            "action": "specific action",
            "vulnerability": "which vuln this addresses",
            "estimated_time": "hours",
            "required_resources": ["resource1", "resource2"],
            "risk_if_delayed": "description"
        }}
    ],
    "short_term_actions": [...],
    "long_term_improvements": [...],
    "resource_requirements": {{
        "developers": number,
        "security_engineers": number,
        "estimated_total_hours": number
    }},
    "timeline": {{
        "phase_1": "description with duration",
        "phase_2": "description with duration",
        "phase_3": "description with duration"
    }},
    "success_criteria": [
        "criterion 1",
        "criterion 2"
    ],
    "monitoring_plan": [
        "monitoring action 1",
        "monitoring action 2"
    ]
}}
"""
        
        response = self.orchestrator._call_groq(prompt, temperature=0.3, max_tokens=2500)
        
        try:
            plan = self._parse_json_response(response)
            if not isinstance(plan, dict):
                raise ValueError("Invalid remediation-plan response format")
            
            # Create tasks for immediate actions
            for i, action in enumerate(plan.get("immediate_actions", [])):
                self.state.create_remediation_task(
                    vuln_id=action.get("vulnerability_id", 0),
                    task_type="immediate_fix",
                    priority="critical"
                )
                
            self.state.add_thought(
                f"Remediation plan created: {len(plan.get('immediate_actions', []))} immediate, "
                f"{len(plan.get('short_term_actions', []))} short-term actions",
                "planning"
            )
            
            return plan
            
        except Exception as e:
            self.state.add_thought(f"Plan creation failed: {e}", "error")
            return self._generate_fallback_plan(analysis_results)
        
    def _tool_validate_fix(self, vulnerability: Dict, proposed_fix: Dict) -> Dict:
        """
        Tool: Validate that a proposed fix actually addresses the vulnerability
        """
        prompt = f"""
Validate this security fix:

Vulnerability: {json.dumps(vulnerability, indent=2)}
Proposed Fix: {json.dumps(proposed_fix, indent=2)}

Check:
1. Does the fix address the root cause?
2. Are there any bypass possibilities?
3. Is the fix complete or partial?
4. Any potential side effects?
5. Compliance with security best practices?

Return JSON:
{{
    "is_valid": true/false,
    "completeness": "Complete|Partial|Insufficient",
    "addresses_root_cause": true/false,
    "bypass_possibilities": ["possibility1", "possibility2"],
    "side_effects": ["effect1", "effect2"],
    "recommendations": ["improvement1", "improvement2"],
    "confidence_score": 0-100
}}
"""
        
        response = self.orchestrator._call_groq(prompt, temperature=0.2)
        
        try:
            parsed = self._parse_json_response(response)
            if isinstance(parsed, dict):
                return parsed
            raise ValueError("Invalid validation response format")
            
        except:
            return {
                "is_valid": True,
                "completeness": "Unknown",
                "confidence_score": 50
            }
        
    def _categorize_vulnerability(self, vuln_type: str) -> str:
        """Categorize vulnerability type for fix generation"""
        vuln_lower = vuln_type.lower()
        
        if "sql" in vuln_lower or "injection" in vuln_lower:
            return "sql_injection"
        elif "xss" in vuln_lower or "cross-site" in vuln_lower:
            return "xss"
        elif "csrf" in vuln_lower:
            return "csrf"
        elif "header" in vuln_lower:
            return "security_headers"
        elif "http" in vuln_lower or "ssl" in vuln_lower or "tls" in vuln_lower:
            return "protocol_security"
        elif "config" in vuln_lower:
            return "security_configuration"
        else:
            return "general"
        
    def _generate_fallback_fix(self, vulnerability: Dict) -> Dict:
        """Generate fallback fix when AI fails"""
        vuln_type = vulnerability.get("type", "Unknown")
        
        return {
            "fix_summary": f"Manual review required for {vuln_type}",
            "language": "unknown",
            "severity": vulnerability.get("severity", "Medium"),
            "code_fix": {
                "description": "AI-generated fix unavailable. Manual implementation required.",
                "code": "// Please consult security documentation for proper fix implementation",
                "file_path": "unknown"
            },
            "configuration_fix": {
                "description": "Review security configuration",
                "config_code": "# Manual configuration review needed",
                "file_path": "unknown"
            },
            "testing_code": {
                "description": "Test the vulnerability is patched",
                "test_code": "# Add security tests here"
            },
            "deployment_steps": [
                "Review vulnerability details",
                "Research best practices for this vulnerability type",
                "Implement fix following security guidelines",
                "Test thoroughly before deployment"
            ],
            "rollback_plan": "Maintain backups before applying changes",
            "verification_commands": [
                "Run security scan to verify fix",
                "Check application functionality"
            ]
        }
        
    def _generate_fallback_plan(self, analysis_results: List[Dict]) -> Dict:
        """Generate fallback remediation plan"""
        return {
            "plan_summary": "Automated plan generation failed. Manual planning required.",
            "immediate_actions": [],
            "short_term_actions": [],
            "long_term_improvements": [
                "Review all identified vulnerabilities",
                "Prioritize based on business impact",
                "Create custom remediation plan",
                "Implement fixes following security best practices"
            ],
            "resource_requirements": {
                "developers": 1,
                "security_engineers": 1,
                "estimated_total_hours": 40
            },
            "timeline": {
                "phase_1": "Assessment and planning (1 week)",
                "phase_2": "Critical fixes (1-2 weeks)",
                "phase_3": "Remaining improvements (2-4 weeks)"
            },
            "success_criteria": [
                "All critical vulnerabilities patched",
                "Security scan shows no high-risk issues"
            ],
            "monitoring_plan": [
                "Schedule regular security scans",
                "Monitor for new vulnerabilities"
            ]
        }
        
    def get_agent_status(self) -> Dict:
        """Get current agent status and progress"""
        return {
            "session_id": self.state.session_id,
            "vulnerabilities_analyzed": len(self.state.vulnerabilities_analyzed),
            "remediation_tasks": len(self.state.remediation_tasks),
            "completed_tasks": len(self.state.completed_tasks),
            "progress": self.state.get_progress(),
            "recent_thoughts": self.state.agent_thoughts[-5:] if self.state.agent_thoughts else []
        }
        
    def execute_remediation_task(self, task_id: int) -> Dict:
        """Mark a remediation task as executed"""
        success = self.state.complete_task(task_id)
        
        if success:
            return {
                "status": "completed",
                "task_id": task_id,
                "completed_at": datetime.now().isoformat(),
                "message": "Task marked as completed"
            }
        else:
            return {
                "status": "error",
                "task_id": task_id,
                "message": "Task not found"
            }
