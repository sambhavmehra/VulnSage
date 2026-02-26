"""
Self-Training Agent
Trains a local bug-intel classifier from latest vulnerability intelligence.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from collections import Counter

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


class SelfTrainingAgent:
    """Train and persist a classifier from threat-intel descriptions."""

    DEFAULT_MODEL_PATH = "bug_intel_model.pkl"

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        self.model_path = model_path

    def train_from_intel(self, intel_payload: Dict[str, Any], min_samples: int = 30) -> Dict[str, Any]:
        items = intel_payload.get("items", [])
        texts, labels = self._build_training_data(items)

        # Drop classes with only one sample; stratified split requires >= 2 per class.
        counts = Counter(labels)
        filtered = [(t, l) for t, l in zip(texts, labels) if counts[l] >= 2]
        texts = [t for t, _ in filtered]
        labels = [l for _, l in filtered]

        if len(texts) < min_samples or len(set(labels)) < 2:
            return {
                "success": False,
                "message": (
                    f"Not enough labeled data to train. "
                    f"Need >= {min_samples} samples and >= 2 classes."
                ),
                "samples": len(texts),
                "classes": sorted(set(labels)),
            }

        # Stratify when feasible, else fall back to random split.
        try:
            x_train, x_test, y_train, y_test = train_test_split(
                texts, labels, test_size=0.2, random_state=42, stratify=labels
            )
        except ValueError:
            x_train, x_test, y_train, y_test = train_test_split(
                texts, labels, test_size=0.2, random_state=42
            )

        pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(max_features=12000, ngram_range=(1, 2), stop_words="english")),
                ("clf", LogisticRegression(max_iter=400)),
            ]
        )
        pipeline.fit(x_train, y_train)
        accuracy = float(pipeline.score(x_test, y_test))

        model_payload = {
            "pipeline": pipeline,
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "samples": len(texts),
            "classes": sorted(set(labels)),
            "accuracy": accuracy,
        }
        joblib.dump(model_payload, self.model_path)

        return {
            "success": True,
            "message": "Threat-intel model trained successfully.",
            "samples": len(texts),
            "classes": sorted(set(labels)),
            "accuracy": round(accuracy, 4),
            "model_path": self.model_path,
        }

    def load_model(self) -> Dict[str, Any] | None:
        if not os.path.exists(self.model_path):
            return None
        try:
            return joblib.load(self.model_path)
        except Exception:
            return None

    def predict(self, text: str) -> Dict[str, Any]:
        model = self.load_model()
        if not model:
            return {"label": "Unknown", "confidence": 0.0}

        pipeline = model.get("pipeline")
        if pipeline is None:
            return {"label": "Unknown", "confidence": 0.0}

        label = pipeline.predict([text])[0]
        confidence = 0.0
        if hasattr(pipeline, "predict_proba"):
            proba = pipeline.predict_proba([text])[0]
            confidence = float(max(proba))
        return {"label": str(label), "confidence": confidence}

    def _build_training_data(self, items: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        texts: List[str] = []
        labels: List[str] = []

        for item in items:
            title = str(item.get("title", ""))
            desc = str(item.get("description", ""))
            cwe_id = str(item.get("cwe_id", "") or "")
            text = f"{title}. {desc}. {cwe_id}".strip()
            label = self._derive_label(text)

            if label != "Unknown":
                texts.append(text)
                labels.append(label)

        return texts, labels

    def _derive_label(self, text: str) -> str:
        t = text.lower()
        rules = {
            "SQL Injection": ["sql injection", "sqli", "cwe-89"],
            "XSS": ["cross-site scripting", "xss", "cwe-79"],
            "RCE": ["remote code execution", "rce", "command injection", "cwe-78", "cwe-94"],
            "SSRF": ["server-side request forgery", "ssrf", "cwe-918"],
            "CSRF": ["cross-site request forgery", "csrf", "cwe-352"],
            "Auth Bypass": ["auth bypass", "authentication bypass", "improper authentication", "cwe-287"],
            "Path Traversal": ["path traversal", "directory traversal", "cwe-22"],
            "Info Disclosure": ["information disclosure", "data exposure", "cwe-200"],
            "Misconfiguration": ["misconfiguration", "default credential", "security header", "cwe-16"],
        }
        for label, keywords in rules.items():
            if any(k in t for k in keywords):
                return label
        return "Unknown"
