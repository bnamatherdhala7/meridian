"""Generic (unconstrained) model — alert description + partial tool data.

Simulates what you'd get asking Claude to analyse an incident when an analyst
has the alert ticket and TRIAGE-level device context (topology + telemetry),
but has NOT run deep SPL netflow queries. This is the realistic baseline for a
NOC analyst without an agentic investigation pipeline.

Gaps vs constrained / investigation:
- No netflow data: can't identify the threat src_ip or compute egress %
- No 60% threshold business rule in context
- No schema enforcement: produces verbose prose, not machine-parseable JSON
- May misattribute root cause (hardware fault vs security threat)

Expected scores: 60-72% precision, 55-65% recall (lower bound of CTIBench
generic unconstrained 74-82%; lower here because netflow context is absent).
"""
import anthropic

_SYSTEM = """You are a network operations analyst. You have been given an incident alert
and partial diagnostic data from TRIAGE. Analyse the situation, identify the likely root
cause, and recommend immediate action. Write a comprehensive incident summary."""


def summarize(
    incident_description: str,
    tool_results: list[dict],
    client: anthropic.Anthropic,
) -> dict:
    # Generic gets: alert description + first 3 tool results (TRIAGE + telemetry)
    # but NOT the deep SPL netflow queries that reveal src_ip and egress %.
    content = (
        "Analyse this network incident and provide a summary with root cause and actions:\n\n"
        f"## Incident Alert\n{incident_description}\n"
    )

    triage_results = tool_results[:3]  # TRIAGE (search_indexes, topology) + first investigating (telemetry)
    if triage_results:
        content += "\n## Diagnostic Data\n"
        for tr in triage_results:
            content += f"\n**{tr['tool']}**:\n{str(tr['result'])[:600]}\n"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=_SYSTEM,
        messages=[{"role": "user", "content": content}],
    )

    return {
        "output": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
    }
