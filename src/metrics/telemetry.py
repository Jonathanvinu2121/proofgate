"""
Telemetry & Cost Tracker.
Logs phase execution latencies and estimates token cost for every pipeline run.
"""

import time
from typing import Dict, Any


class TelemetryTracker:
    def __init__(self):
        self.latencies: Dict[str, float] = {}
        self.token_counts: Dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0}
        self.estimated_cost_usd: float = 0.0

    def record_phase(self, phase_name: str, duration_sec: float):
        self.latencies[phase_name] = round(duration_sec, 4)

    def add_tokens(self, prompt_tokens: int, completion_tokens: int):
        self.token_counts["prompt_tokens"] += prompt_tokens
        self.token_counts["completion_tokens"] += completion_tokens
        # $0 cost for local sentence-transformers and local/mock LLMs
        self.estimated_cost_usd = 0.0

    def get_summary(self) -> Dict[str, Any]:
        total_latency = sum(self.latencies.values())
        return {
            "phase_latencies_seconds": self.latencies,
            "total_latency_seconds": round(total_latency, 4),
            "token_counts": self.token_counts,
            "estimated_cost_usd": f"${self.estimated_cost_usd:.4f}"
        }
