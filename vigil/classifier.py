"""
Pre-triage classifier — rules-based noise filter.
Runs before any model call. Suppresses ~35-40% of alerts.
Returns (should_investigate: bool, score: float, reason: str)
"""
import re

SUPPRESS_PATTERNS = [
    (r"test alert",           "test_alert",            0.0),
    (r"maintenance window",   "maintenance_suppressed", 0.05),
    (r"scheduled backup",     "known_scheduled_job",   0.10),
    (r"cpu [0-9]+%.*normal",  "within_baseline",       0.15),
    (r"resolved automatically", "auto_resolved",        0.05),
]

ESCALATE_SIGNALS = [
    (r"94%|95%|96%|97%|98%|99%",    0.30),
    (r"unknown process",             0.25),
    (r"tor|exfil|c2|malware",        0.40),
    (r"core.*device|tier.?1",        0.20),
    (r"bgp.*(flap|reset).*(3|4|5|6|7|8|9)", 0.20),
    (r"route withdrawal",            0.15),
    (r"packet loss.*(high|severe)",  0.15),
    (r"[6-9][0-9]%.*egress",         0.25),
]

THRESHOLD = 0.45


def classify(alert_text: str) -> tuple[bool, float, str]:
    text = alert_text.lower()

    for pattern, reason, score in SUPPRESS_PATTERNS:
        if re.search(pattern, text):
            return False, score, f"suppressed:{reason}"

    score = 0.40
    for pattern, boost in ESCALATE_SIGNALS:
        if re.search(pattern, text):
            score += boost

    score = min(score, 1.0)

    if score < THRESHOLD:
        return False, score, "below_threshold"

    return True, round(score, 2), "proceed_to_fsm"
