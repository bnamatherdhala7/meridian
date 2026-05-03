"""Generic (unconstrained) model — verbose natural language output.

Simulates what you'd get asking Claude to summarize an incident without
any schema enforcement or structured output requirements. Receives raw
tool results without pre-processing, forcing it to synthesize from scratch.
"""
import anthropic

_SYSTEM = """You are a network operations analyst. Summarize the investigation findings in a comprehensive report.
Be thorough and include all relevant context, background, and caveats. Write in flowing prose."""


def summarize(evidence: list[str], tool_results: list[dict], client: anthropic.Anthropic) -> dict:
    # Generic model gets RAW tool results only — no pre-baked evidence list.
    # This mimics the realistic difference: a constrained run curates evidence;
    # an unconstrained run has to synthesize from raw output.
    content = "Analyze the following raw tool results from a network incident investigation and provide a comprehensive report:\n\n"
    if tool_results:
        for tr in tool_results[:5]:
            content += f"Tool: {tr['tool']}\nRaw output:\n{str(tr['result'])[:800]}\n\n"
    else:
        content += "No tool results available.\n"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=_SYSTEM,
        messages=[{"role": "user", "content": content}],
    )

    return {
        "output": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
    }
