# VulnSage Advanced Features — Implementation Plan

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   app_ai.py (UI)                    │
├──────────┬──────────┬──────────┬──────────┬─────────┤
│ Attack   │ Auto-    │Continuous│ CI/CD    │ SOC     │
│ Path     │ Validate │ Scanner  │ Gate     │ Copilot │
│ Agent    │ Loop     │          │          │         │
├──────────┴──────────┴──────────┴──────────┴─────────┤
│          security_agent.py (extended)                │
│          remediation_engine.py (extended)            │
│          report_generator.py (extended)              │
├─────────────────────────────────────────────────────┤
│          groq_orchestrator.py (AI backbone)          │
├─────────────────────────────────────────────────────┤
│     New Modules:                                    │
│     - attack_path_agent.py                          │
│     - scan_baseline.py                              │
│     - cicd_gate.py                                  │
│     - soc_copilot.py                                │
│     - admin_logger.py (existing)                    │
└─────────────────────────────────────────────────────┘
```

## Phase 1 (MVP) — Shipped Now
1. Attack Path Agent — correlate vulns, generate attack graph
2. Continuous Scan Baselines — delta detection
3. CI/CD Security Gate — policy engine + SARIF export
4. SOC Copilot — triage + task creation
5. Admin Panel — separated New Users / Login / Activity sections
6. Text overwriting fixes

## Phase 2 (Next Sprint)
- Auto-validation loop (re-scan to verify fixes)
- Scheduled scans (background cron-like)
- SARIF integration with GitHub Actions

## Phase 3 (Production)
- WebSocket live scan updates
- Role-based admin sub-pages
- Audit trail export
