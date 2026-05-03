"""FSM state and transition definitions."""

STATES = ["IDLE", "TRIAGE", "INVESTIGATING", "HYPOTHESIZING", "REMEDIATING", "ESCALATING", "RESOLVED"]

TRANSITIONS = [
    {"trigger": "start_triage", "source": "IDLE", "dest": "TRIAGE"},
    {"trigger": "begin_investigation", "source": "TRIAGE", "dest": "INVESTIGATING"},
    {"trigger": "form_hypothesis", "source": "INVESTIGATING", "dest": "HYPOTHESIZING"},
    {"trigger": "remediate", "source": "HYPOTHESIZING", "dest": "REMEDIATING"},
    {
        "trigger": "escalate",
        "source": ["TRIAGE", "INVESTIGATING", "HYPOTHESIZING", "REMEDIATING"],
        "dest": "ESCALATING",
    },
    {"trigger": "resolve", "source": ["REMEDIATING", "ESCALATING"], "dest": "RESOLVED"},
]

# Valid next states from each state — used to constrain the transition_state tool enum
VALID_TRANSITIONS: dict[str, list[str]] = {
    "TRIAGE": ["INVESTIGATING", "ESCALATING"],
    "INVESTIGATING": ["HYPOTHESIZING", "ESCALATING"],
    "HYPOTHESIZING": ["REMEDIATING", "ESCALATING"],
    "REMEDIATING": ["RESOLVED", "ESCALATING"],
    "ESCALATING": ["RESOLVED"],
}
